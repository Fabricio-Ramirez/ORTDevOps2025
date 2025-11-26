import boto3
import time
import getpass
from botocore.exceptions import ClientError
from datetime import datetime

ec2 = boto3.client('ec2')
ssm = boto3.client('ssm')

user_data = '''#!/bin/bash
sudo -i
yum update -y
yum install -y httpd
systemctl start httpd
systemctl enable httpd
echo "¡Sitio personalizado!" > /var/www/html/index.html
'''

# Crear una instancia EC2 asociada al Instance Profile del rol LabRole
response = ec2.run_instances(
    ImageId='ami-06b21ccaeff8cd686',
    MinCount=1,
    MaxCount=1,
    InstanceType='t2.micro',
    IamInstanceProfile={'Name': 'LabInstanceProfile'},
    UserData=user_data,
)

# Agregar tag Name: Obligatorio-Devops
instance_id = response['Instances'][0]['InstanceId']
ec2.create_tags(
    Resources=[instance_id],
    Tags=[{'Key': 'Name', 'Value': 'Obligatorio-Devops'}]
)

print(f"Instancia activa con ID: {instance_id} y tag 'Obligatorio-Devops'")
print ("Esperando a que la instancia esté en estado running...")
# Esperar a que la instancia esté en estado running y mostrar mensajes hasta recibir ok de
ec2.get_waiter('instance_status_ok').wait(InstanceIds=[instance_id])

# Enviar comando y extraer resultado
command = 'echo "Hello world"'
response = ssm.send_command(
    InstanceIds=[instance_id],
    DocumentName="AWS-RunShellScript",
    Parameters={'commands': [command]}
)
command_id = response['Command']['CommandId']

# Esperar resultado
while True:
    output = ssm.get_command_invocation(CommandId=command_id, InstanceId=instance_id)
    if output['Status'] in ['Success', 'Failed', 'Cancelled', 'TimedOut']:
        break
    time.sleep(2)
print("Output:")
print(output['StandardOutputContent'])

# Bloque duplicado eliminado: el manejo de creación y errores del Security Group
# se realiza más abajo en el script.

sg_name = "web-sg-boto3"
# 1. Intentar crear el Security Group
try:
    response = ec2.create_security_group(
        GroupName=sg_name,
        Description="Permitir trafico web desde cualquier IP"
    )
    sg_id = response["GroupId"]
    print(f"Security Group creado: {sg_id}")

except ClientError as e:
    error_code = e.response["Error"]["Code"]

    # SG duplicado
    if error_code == "InvalidGroup.Duplicate":
        print("El Security Group ya existe. Recuperando su ID...")
        sg_id = ec2.describe_security_groups(
            GroupNames=[sg_name]
        )["SecurityGroups"][0]["GroupId"]

    else:
        # Error real → volver a lanzar
        raise


# 2. Intentar agregar la regla solo si no existe
try:
    ec2.authorize_security_group_ingress(
        GroupId=sg_id,
        IpPermissions=[
            {
                "IpProtocol": "tcp",
                "FromPort": 80,
                "ToPort": 80,
                "IpRanges": [{"CidrIp": "0.0.0.0/0"}]
            }
        ]
    )
    print("Regla agregada al SG.")

except ClientError as e:
    error_code = e.response["Error"]["Code"]

    if error_code == "InvalidPermission.Duplicate":
        print("La regla ya existe. Continuando…")
    else:
        raise


#Asociar el SG a la instancia sin fallar
print(f"Asociando SG {sg_id} a la instancia {instance_id}...")

try:
    ec2.modify_instance_attribute(
        InstanceId=instance_id,
        Groups=[sg_id]  # Puede usar lista de múltiples SG si quisieras
    )
    print(f"SG {sg_id} asociado correctamente.")

except ClientError as e:
    print("Error inesperado al asociar el SG:")
    raise

# Obtener IP pública de la instancia y mostrarla
def get_public_ip(ec2_client, instance_id, timeout=120, interval=3):
    elapsed = 0
    while elapsed < timeout:
        resp = ec2_client.describe_instances(InstanceIds=[instance_id])
        try:
            public_ip = resp['Reservations'][0]['Instances'][0].get('PublicIpAddress')
        except (IndexError, KeyError):
            public_ip = None
        if public_ip:
            return public_ip
        time.sleep(interval)
        elapsed += interval
    return None

public_ip = get_public_ip(ec2, instance_id)
if public_ip:
    print(f"Ahora puede navegar a http://{public_ip} para verificar el acceso web.")
else:
    print("No se pudo obtener la IP pública de la instancia (puede que no tenga IP pública asignada).")

# Parámetros
rds = boto3.client('rds')
DB_INSTANCE_ID = f"app-mysql-{datetime.now().strftime('%Y%m%d-%H%M')}"
DB_NAME = 'app'
DB_USER = 'admin'
"""Script para crear una instancia RDS MySQL.

La contraseña del usuario administrador se solicita de forma interactiva
con entrada oculta (no se muestra lo tecleado). No usa variables de entorno.
"""

# Solicitud segura por terminal (no muestra lo tecleado)
while True:
    DB_PASS = getpass.getpass('\nIngresa la contraseña del admin RDS: ').strip()
    if not DB_PASS:
        print('La contraseña no puede estar vacía. Intenta nuevamente.')
        continue
    if len(DB_PASS) < 8:
        print('La contraseña debe tener al menos 8 caracteres. Intenta nuevamente.')
        continue
    break


try:
    rds.create_db_instance(
        DBInstanceIdentifier=DB_INSTANCE_ID,
        AllocatedStorage=20,
        DBInstanceClass='db.t3.micro',
        Engine='mysql',
        MasterUsername=DB_USER,
        MasterUserPassword=DB_PASS,  # contraseña solicitada de forma segura
        DBName=DB_NAME,
        PubliclyAccessible=True,
        BackupRetentionPeriod=0
    )

    # crear security group para acceso segun el engine: permitir tráfico desde web-sg-boto3
    rds_sg_name = "rds-sg-boto3"

    # Obtener VPC de la instancia EC2 para crear el SG en la misma VPC
    resp = ec2.describe_instances(InstanceIds=[instance_id])
    vpc_id = resp['Reservations'][0]['Instances'][0].get('VpcId')

    try:
        if vpc_id:
            resp = ec2.create_security_group(
                GroupName=rds_sg_name,
                Description="SG para RDS que permite acceso desde web-sg-boto3",
                VpcId=vpc_id
            )
        else:
            resp = ec2.create_security_group(
                GroupName=rds_sg_name,
                Description="SG para RDS que permite acceso desde web-sg-boto3"
            )
        rds_sg_id = resp["GroupId"]
        print(f"Security Group RDS creado: {rds_sg_id}")

    except ClientError as e:
        code = e.response["Error"]["Code"]
        if code == "InvalidGroup.Duplicate":
            # Buscar SG existente en la misma VPC si es posible
            filters = [{'Name': 'group-name', 'Values': [rds_sg_name]}]
            if vpc_id:
                filters.append({'Name': 'vpc-id', 'Values': [vpc_id]})
            sgs = ec2.describe_security_groups(Filters=filters)["SecurityGroups"]
            if not sgs:
                raise
            rds_sg_id = sgs[0]["GroupId"]
            print(f"Security Group RDS existente: {rds_sg_id}")
        else:
            raise

    # Autorizar ingreso en el SG de RDS desde el SG web (sg_id) en el puerto MySQL (3306)
    try:
        ec2.authorize_security_group_ingress(
            GroupId=rds_sg_id,
            IpPermissions=[
                {
                    "IpProtocol": "tcp",
                    "FromPort": 3306,
                    "ToPort": 3306,
                    "UserIdGroupPairs": [{"GroupId": sg_id}]
                }
            ]
        )
        print("Regla agregada al SG RDS (permite desde web-sg-boto3).")
    except ClientError as e:
        if e.response["Error"]["Code"] == "InvalidPermission.Duplicate":
            print("La regla ya existe en el SG RDS. Continuando…")
        else:
            raise

    # Esperar a que la instancia RDS esté en estado 'available' antes de modificarla
    print(f"Esperando a que la instancia RDS {DB_INSTANCE_ID} esté disponible...")
    waiter = rds.get_waiter('db_instance_available')
    waiter.wait(DBInstanceIdentifier=DB_INSTANCE_ID)
    print(f"La instancia RDS {DB_INSTANCE_ID} ya está disponible. Asociando el SG...")

    # Asociar el SG de RDS a la instancia RDS recién creada (aplicar inmediatamente)
    try:
        rds.modify_db_instance(
            DBInstanceIdentifier=DB_INSTANCE_ID,
            VpcSecurityGroupIds=[rds_sg_id],
            ApplyImmediately=True
        )
        print(f"SG RDS {rds_sg_name} asociado a la instancia RDS {DB_INSTANCE_ID}.")
    except ClientError as e:
        print("Error al asociar el SG a la instancia RDS:")
        raise   

    print(f'Instancia RDS {DB_INSTANCE_ID} creada correctamente.')

except rds.exceptions.DBInstanceAlreadyExistsFault:
    print(f'La instancia {DB_INSTANCE_ID} ya existe.')

