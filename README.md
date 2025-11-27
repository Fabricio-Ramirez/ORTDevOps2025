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
```bash
# Bloque de Codigo:
#!/bin/bash
# ej1_crea_usuarios.sh
# Crea usuarios a partir de un archivo con 5 campos separados por ":"
# Formato de cada línea (se permiten líneas en blanco y comentarios con #):
#   usuario:comentario:directorio_home:crear_home(SI/NO):shell
# Cualquier campo puede estar vacío para usar los valores por defecto del sistema.
# Requiere privilegios de root para crear usuarios y asignar contraseñas.
#ej1_crea_usuarios.sh  [-i]  [-c contraseña ]   Archivo_con_los_usuarios_a_crea

if [ $# -lt 1 ] #Se hace Test para comprobar que hay al menos un argumento
then
    echo "Uso: $0  [-i]  [-c contraseña] Archivo_con_los_usuarios_a_crear" >&2 # Mensaje de error Si no hay argumentos
    exit 1 
fi

while getopts ":ic:" modificador #Bucle para analizar las opciones ingresadas
do
    case $modificador in
        i) echo "Modo Interactivo activado"
           INTERACTIVO=true
        ;;
        c)  # Guardar el argumento pasado a -c en la variable CONTRASENA
            CONTRASENA="$OPTARG"

            if [ -z "$CONTRASENA" ] && [ -n "$(echo $OPTERR)" ]; then
                read -s -p "Introduzca contraseña para los usuarios: " CONTRASENA
                echo
            fi
            echo "Opción -c: se guardó CONTRASENA='$CONTRASENA'"
        ;;
        :) # getopts devuelve ':' cuando falta el argumento para una opción que lo requiere
            echo "Error: La opción -$OPTARG requiere un argumento." >&2
            exit 5
        ;;
        *) echo "Opción inválida: -$OPTARG" >&2
           exit 10
        ;;
    esac
done

# Mover los parámetros posicionales para que $1 sea el primer argumento no-opción
shift $((OPTIND - 1))

# Comprobar que hay un argumento (archivo) después de las opciones
if [ -z "$1" ]
then
    echo "Falta el archivo con los usuarios a crear" >&2
    echo "Uso: $0  [-i]  [-c contraseña] Archivo_con_los_usuarios_a_crear" >&2
    exit 2
fi

maxlineas=$(wc -l < "$1")

ArchivoUsrs="$1"

if [ ! -f "$ArchivoUsrs" ] || [ ! -r "$ArchivoUsrs" ]
then
    echo "Archivo '$ArchivoUsrs' no encontrado o no legible." >&2
    exit 3
fi

usuarios_creados=0

if [ "$INTERACTIVO" = true ]
then
    for i in $(seq 1 $maxlineas); do # Leer línea por línea
    
        linea=$(tail -n +$i "$ArchivoUsrs" | head -n 1) # Asignamos a la variable linea la línea i-ésima del archivo
            
            if [ "$(echo "$linea" | grep -o ":" | wc -l)" -ne 4 ]; then
                echo "Línea $i mal formada. Se esperan 5 campos separados por ':'. Se omite." >&2
                continue
            fi

        nombre=$(echo "$linea" | cut -d':' -f1 | xargs) #Se asigna el primer campo a la variable nombre
        comentario=$(echo "$linea" | cut -d':' -f2 | xargs) #Se asigna el segundo campo a la variable comentario
        home=$(echo "$linea" | cut -d':' -f3 | xargs) #Se asigna el tercer campo a la variable home
        creahome=$(echo "$linea" | cut -d':' -f4 | xargs) #Se asigna el cuarto campo a la variable creahome
        bashusr=$(echo "$linea" | cut -d':' -f5 | xargs) #Se asigna el quinto campo a la variable bashusr

        #echo "Procesando línea $i: Usuario='$nombre', Comentario='$comentario', Home='$home', Crear_Home='$creahome', Shell='$bashusr'"

        if [ "$creahome" = "SI" ] || [ "$creahome"   = "si" ]; then
            crearopcion="-m"
       fi 

       if [ "$creahome" = "NO" ] || [ "$creahome" = "" ]; then
            crearopcion="-M"
        fi
        if [ -n "$home" ]; then
            homeopt="-d $home"
            else
            homeopt=""
        fi
   
        useradd $crearopcion $homeopt -c "$comentario" -s "$bashusr" -p "$(openssl passwd -6 "$CONTRASENA")" "$nombre"

        if [ $? -ne 0 ]; then
            echo "Error al crear el usuario '$nombre'." >&2
            continue
            else
                echo "Usuario '$nombre' creado con éxito con datos:"
                echo -e " Comentario='$comentario' \n Dir Home='$home' \n Crear_Home='$creahome' \n Shell='$bashusr' \n"
                usuarios_creados=$((usuarios_creados + 1))
        fi
    done
    echo "Total de usuarios creados: $usuarios_creados"
    exit 0

else
    echo "Modo no interactivo."

    for i in $(seq 1 $maxlineas); do # Leer línea por línea
    
        linea=$(tail -n +$i "$ArchivoUsrs" | head -n 1) # Asignamos a la variable linea la línea i-ésima del archivo

        if [ "$(echo "$linea" | grep -o ":" | wc -l)" -ne 4 ]; then 
                echo "Línea $i mal formada. Se esperan 5 campos separados por ':'. Se omite." >&2
                continue
            fi

        nombre=$(echo "$linea" | cut -d':' -f1 | xargs) #Se asigna el primer campo a la variable nombre
        comentario=$(echo "$linea" | cut -d':' -f2 | xargs) #Se asigna el segundo campo a la variable comentario
        home=$(echo "$linea" | cut -d':' -f3 | xargs) #Se asigna el tercer campo a la variable home
        creahome=$(echo "$linea" | cut -d':' -f4 | xargs) #Se asigna el cuarto campo a la variable creahome
        bashusr=$(echo "$linea" | cut -d':' -f5 | xargs) #Se asigna el quinto campo a la variable bashusr

        #echo "Procesando línea $i: Usuario='$nombre', Comentario='$comentario', Home='$home', Crear_Home='$creahome', Shell='$bashusr'"

        if [ "$creahome" = "SI" ] || [ "$creahome"   = "si" ]; then
            crearopcion="-m"
       fi 

       if [ "$creahome" = "NO" ] || [ "$creahome" = "" ]; then
            crearopcion="-M"
        fi
        if [ -n "$home" ]; then
            homeopt="-d $home"
            else
            homeopt=""
        fi
   
        useradd $crearopcion $homeopt -c "$comentario" -s "$bashusr" -p "$(openssl passwd -6 "$CONTRASENA")" "$nombre"

        if [ $? -ne 0 ]; then
            echo "Error al crear el usuario '$nombre'." >&2
            continue
            else
                echo "Usuario '$nombre' creado con éxito."
                usuarios_creados=$((usuarios_creados + 1))
        fi
    done 
fi
  ```

## Parte 2 : Script Python 
Se recomienda ejecutar en cuenta AWS sin instancias ni Security Groups creados anteriormente

  > [!CAUTION]
  > Requisitos necesarios previos al Despliegue de las Instancias y Aplicaciones en AWS:

* Cuenta de Github
* Git:
  
	Instalación de GIT
```bash
sudo dnf install git
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

