# ORTDevOps2025

El siguiente proyecto es basado en la version Centos utilizada en el curso y es la que recomendamos utilizar

## Parte 1 : Script Bash 

  ### Pasos para correcta configuración inicial:

  ```bash
  1. sudo dnf install git -y && git clone https://github.com/Fabricio-Ramirez/ORTDevOps2025.git 
  2. cd ./ORTDevOps2025
  3. sudo chmod u+x ./ej1_crea_usuarios.sh && sudo chmod u+r ./Usuarios
  ```
  > El script hace uso del paquete "openssl". Mandatoria instalación

  Debian-Ubuntu

   ```bash
  sudo apt-get install -y openssl
  sudo yum install -y openssl
  ```
RHEL-CentOS
 ```bash
  sudo yum install -y openssl
  ```

  > [!WARNING]
  > Para ejecutar ej1_crea_usuarios.sh se necesita Root / User parte de grupo Wheel haciendo uso de **SUDO**
  
  ```bash
  sudo ./ej1_crea_usuarios.sh [-i] [-c] (password) (archivousuarios)
  ```
```bash
# Bloque de Codigo:
#!/bin/bash

# ========================
# Script: ej1_crea_usuarios.sh
# Descripción general:
#   Lee un archivo de texto donde cada línea describe un usuario a crear.
#   Cada línea posee 5 campos separados por ':' en el orden:
#     usuario:comentario:directorio_home:crear_home(SI/NO):shell
#   Campos vacíos permiten usar valores por defecto del sistema.
#   Líneas en blanco o que empiezan con '#' se ignoran.
#   Soporta modo interactivo (-i) para mostrar más detalle al crear cada usuario.
#   Permite especificar una contraseña común para todos los usuarios con -c.
# Requisitos:
#   - Debe ejecutarse con privilegios de root para que 'useradd' funcione y asigne contraseña.
#   - El archivo de entrada debe ser legible.
# Uso:
#   ./ej1_crea_usuarios.sh [-i] [-c contraseña] archivo_usuarios
# ========================

if [ $# -lt 1 ] # Valida que se haya pasado al menos una opción o el archivo
then
    echo "Uso: $0  [-i]  [-c contraseña] Archivo_con_los_usuarios_a_crear" >&2 # Mensaje de error Si no hay argumentos
    exit 1 
fi

#Cada carácter representa una opción válida:
# 
# opción -i (no tiene ':' a su derecha, por tanto NO requiere argumento)
# opción -c (el ':' después de la 'c' indica que -c requiere un argumento)
# ':' inicial del optstring activa el "modo silencioso" (silent error reporting).
# comportamiento ante errores de getopts en "modo silencioso":
#     * Si falta el argumento requerido para una opción (por ejemplo, se pasa "-c" sin valor),
#       getopts asigna ':' a la variable de control y coloca en OPTARG la letra de la opción
#     * Si se encuentra una opción no reconocida (por ejemplo, "-x"),
#       getopts asigna '?' a la variable de control y coloca en OPTARG la letra inválida.
#   Sin el ':' inicial, getopts además imprimiría un mensaje de error estándar por sí mismo.

while getopts ":ic:" modificador # Procesa opciones -i (interactivo) y -c (contraseña)
do
    case $modificador in
          i) echo -e "Modo Interactivo activado \n" # Modo con salida detallada
              INTERACTIVO=true
        ;;
        c)  # Opción -c: guarda la contraseña proporcionada para todos los usuarios
            CONTRASENA="$OPTARG"

            if [ -z "$CONTRASENA" ] && [ -n "$(echo $OPTERR)" ]; then
                read -s -p "Introduzca contraseña para los usuarios: " CONTRASENA
                echo
            fi
            echo -e "Opción -c: se guardó CONTRASENA='$CONTRASENA'\n"
        ;;
        :) # Error: falta argumento obligatorio para una opción (-c sin valor)
            echo "Error: La opción -$OPTARG requiere un argumento." >&2
            exit 5
        ;;
        *) echo "Opción inválida: -$OPTARG" >&2 # Cualquier otra opción es rechazada
           exit 10
        ;;
    esac
done

# Desplaza los argumentos ya procesados para que $1 sea el archivo
shift $((OPTIND - 1))


# Comprueba que se haya pasado el archivo de usuarios
if [ -z "$1" ]
then
    echo "Falta el archivo con los usuarios a crear" >&2
    echo "Uso: $0  [-i]  [-c contraseña] Archivo_con_los_usuarios_a_crear" >&2
    exit 2
fi

maxlineas=$(wc -l < "$1") # Cuenta total de líneas del archivo (incluye vacías/comentarios)

ArchivoUsrs="$1" # Ruta al archivo de usuarios

if [ ! -f "$ArchivoUsrs" ] || [ ! -r "$ArchivoUsrs" ] # Verifica existencia y permiso de lectura
then
    echo "Archivo '$ArchivoUsrs' no encontrado o no legible." >&2
    exit 3
fi

usuarios_creados=0 # Contador de usuarios creados exitosamente

for i in $(seq 1 $maxlineas); do # Recorre cada número de línea de 1 a maxlineas
    
        linea=$(tail -n +$i "$ArchivoUsrs" | head -n 1) # Extrae la línea i
            
            if [ "$(echo "$linea" | grep -o ":" | wc -l)" -ne 4 ]; then # Verifica que existan exactamente 4 separadores ':' (5 campos)
                echo "Línea $i mal formada. Se esperan 5 campos separados por ':'. Se omite." >&2
                continue
            fi

        nombre=$(echo "$linea" | cut -d':' -f1 | xargs) # Campo 1: nombre de usuario (trim con xargs)
        if [ -z "$nombre" ] || [[ "$nombre" == \#* ]] || [[ "$nombre" == \\* ]] || [ "${#nombre}" -ge 32 ]; then # Valida nombre no vacío, no comentario, longitud < 32
            echo "Línea $i: Nombre de usuario mal formado o comentario. Se omite." >&2
            continue
   	    fi
        comentario=$(echo "$linea" | cut -d':' -f2 | xargs) # Campo 2: comentario (gecos)
        home=$(echo "$linea" | cut -d':' -f3 | xargs) # Campo 3: directorio HOME solicitado
        creahome=$(echo "$linea" | cut -d':' -f4 | xargs) # Campo 4: indicador SI/NO creación de home
        bashusr=$(echo "$linea" | cut -d':' -f5 | xargs) # Campo 5: shell del usuario

        #echo "Procesando línea $i: Usuario='$nombre', Comentario='$comentario', Home='$home', Crear_Home='$creahome', Shell='$bashusr'"

        if [ "$creahome" = "SI" ] || [ "$creahome"   = "si" ]; then # Decide crear home (-m) si se pidió SI/si
            crearopcion="-m"
       fi 

    if [ "$creahome" = "NO" ] || [ "$creahome" = "" ]; then # Si NO o vacío, evitar creación (-M)
            crearopcion="-M"
        fi
        if [ -n "$home" ]; then # Si se especificó un directorio home, se agrega opción -d
            homeopt="-d $home"
            else
            homeopt=""
        fi
   
        # Ejecuta la creación del usuario con: comentario, shell, creación (o no) de home y contraseña cifrada
        useradd $crearopcion $homeopt -c "$comentario" -s "$bashusr" -p "$(openssl passwd -6 "$CONTRASENA")" "$nombre" 2>/dev/null
        #useradd -p espera un hash, no la contraseña en texto plano. Con OpenSSL generamos SHA-512 compatible con shadow.

        if [ $? -ne 0 ]; then # Si useradd falla, informa y salta a la siguiente línea
            echo "Error al crear el usuario '$nombre'." >&2
            continue
            else
                if [ "$INTERACTIVO" = true ]; then    # Modo interactivo: salida detallada de los datos usados
                    echo "Usuario '$nombre' creado con éxito con datos:"
                    echo -e " Comentario='$comentario' \n Dir Home='$home' \n Crear_Home='$creahome' \n Shell='$bashusr' \n"
                    usuarios_creados=$((usuarios_creados + 1))
                fi
                if [ "$INTERACTIVO" != true ]; then # Modo no interactivo: mensaje breve
                    echo "Usuario '$nombre' creado con éxito."
                    usuarios_creados=$((usuarios_creados + 1))
                fi
        fi
    done
    echo "Total de usuarios creados: $usuarios_creados" # Resumen final tras procesar todas las líneas
    exit 0

  ```

## Parte 2 : Script Python 
Se recomienda ejecutar en cuenta AWS sin instancias ni Security Groups creados anteriormente

  > [!CAUTION]
  > Requisitos necesarios previos al Despliegue de las Instancias y Aplicaciones en AWS:

* Cuenta de Github
* Git:
  
	Instalación de GIT
```bash
sudo dnf install git && git clone https://github.com/Fabricio-Ramirez/ORTDevOps2025.git 
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
cd ./ORTDevOps2025 && sudo chmod u+x ./ej2_AppEC2RDS.py
python3 ./ej2_AppEC2RDS.py
```

