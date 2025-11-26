# ORTDevOps2025

El siguiente proyecto es basado en la version Centos utilizada en el curso y es la que recomendamos utilizar

## Parte 1 : Script Bash 

  ### Pasos para correcta configuración inicial:

  ```bash
  1. sudo dnf install git -y && git clone https://github.com/Fabricio-Ramirez/ORTDevOps2025.git 
  2. cd ./ORTDevOps2025
  3. sudo chmod u+x ./ej1_crea_usuarios.sh && sudo chmod u+r ./Usuarios
  ```

  > [!WARNING]
  > Para ejecutar ej1_crea_usuarios.sh se necesita Root / User parte de grupo Wheel haciendo uso de **SUDO** 
  
  ```bash
  sudo ./ej1_crea_usuarios.sh [-i] [-c] (password) (archivousuarios)
  ```

## Parte 2 : Script Python 
Se recomienda ejecutar en cuenta AWS sin instancias ni Security Groups creados anteriormente

  > [!CAUTION]
  > Requisitos necesarios previos al Despliegue de las Instancias y Aplicaciones en AWS:

* Cuenta de Github
* Git:
  
	Instalación de GIT
```bash
sudo dnf install Git
```
* Python:
Instalación de Python
```bash
sudo dnf install python3
```
* pip:
		Instalación de pip
```bash
sudo dnf install python3-pip
```
* Boto3:
Instalación de Boto3
```bash
pip3 install boto3
```
* AWS CLI:
Instalación de AWS CLI:
```bash
curl https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip -o awscliv2.zip
unzip awscliv2.zip
sudo ./aws/install
aws --version
aws configure
#Aqui se ingresan aws_access_key_id, aws_secret_access_key, aws_session_token, region (us-east-1), Output json
```
  
## Ejecutar Script Python
```bash
cd ./ORTDevOps2025 && chmod u+x ./ej2_AppEC2RDS.py
python3 ./ej2_AppEC2RDS.py
```

