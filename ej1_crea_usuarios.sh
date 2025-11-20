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

: 
