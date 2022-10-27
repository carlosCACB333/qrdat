# sistema de control de asistencia

## software requerido

- python 3.10.7
- Qt designer 5.11.1
- visual studio code 1.72.2

## librerias requeridas

- numpy==1.23.4
- opencv-python==4.6.0.66
- peewee==3.15.3
- PyQt5==5.15.7
- openpyxl==3.0.10
- pyinstaller==5.6.1

## pasos para ejecutar el programa

- **Instalar python 3.10.7**
- **Abrir una terminal**
- **Clonar el repositorio** (tener instalado git)
  ```
  git clone git@github.com:carlosCACB333/qrdat.git
  ```
- **Ingresar a la carpeta del proyecto**
  ```
  cd qrdat
  ```
- **Crear un entorno virtual**
  ```
  py -m venv env
  ```
- **Activar el entorno virtual**
  ```
  .\env\Scripts\activate
  ```
- **Instalar las librerias requeridas**
  ```
    pip install -r requirements.txt
  ```
- **Ejecutar el programa**
  ```
  py main.py
  ```

## generar la interfaz grafica

con el programa de Qt designer 5.11.1 abrir el archivo `UI/main_window.ui` y hacer las modificaciones necesarias, luego de esto ejecutar el siguiente comando en la terminal para generar el archivo `main_window.py` que contiene el diseño en python

```
pyuic5 -x .\UI\main_window.ui -o .\UI\main_window.py
```

## general el ejecutable del programa

# <<<<<<< HEAD

- **Instalar pyinstaller**

  ```
  pip install pyinstaller
  ```

> > > > > > > 7a513f757545e6f8cb7f1bb13941a52423f4a965

- **Ejecutar el siguiente comando**
  ```
  pyinstaller --onefile --windowed --icon=assets/icon.ico main.py
  ```
- **El ejecutable se encuentra en la carpeta dist**
