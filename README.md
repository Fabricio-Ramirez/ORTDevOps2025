# Trabajo Obligatorio Devops 2025 

## Parte 1 : Script Bash 

  ### Pasos para correcta configuración inicial:

  ```bash
  1. sudo (dnf/apt) install git -y && git clone https://github.com/Fabricio-Ramirez/ORTDevOps2025.git 
  2. cd ./ORTDevOps2025
  3. sudo chmod u+x ./ej1_crea_usuarios.sh && sudo chmod u+r ./Usuarios
  ```

  > [!WARNING]
  > Para ejecutar ej1_crea_usuarios.sh se necesita Root / User parte de grupo Wheel haciendo uso de **SUDO** 
  
  ```bash
  sudo ./ej1_crea_usuarios.sh [-i] [-c] (password) (archivousuarios)
  ```


## Parte 2 : Script Python 

  > [!CAUTION]
  > Para un correcto uso del código, se necesitan instalar los siguientes servicios de manera mandatoria:
1. Instalar Python:
```bash
  sudo apt install python3
```
2. Instalación de PIP
```bash
  sudo apt install python3-pip
```
3. Instalacion de AWS CLI
```bash
 curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
  ```
4. Instalación de BOTO3
```bash
  pip3 install boto3
```
- [ ] Clonar repositorio con HTTPS https://github.com/ORT-AII-ProgramacionDevOps/obligatorio.git como ZIP

