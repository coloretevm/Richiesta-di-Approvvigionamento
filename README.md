# App Python a .exe

App de escritorio en Python que pide los datos de una `Richiesta di Approvvigionamento` y genera directamente el PDF final. Esta version esta pensada para compilarse a `.exe` en Windows con `PyInstaller`.

## Requisitos

- Python 3.11 o superior

## Ejecutar en desarrollo

```powershell
python app.py
```

## Generar el .exe

```powershell
.\build.ps1
```

Si `PyInstaller` ya existe en tu instalacion de Python, el script lo reutiliza. Si no existe, intenta instalarlo dentro de una carpeta local del proyecto.

El ejecutable se genera en:

```text
dist\MiAppEscritorio.exe
```

## Que hace la app

- Lleva una numeracion automatica y persistente de las richieste
- Incluye el numero de richiesta dentro del PDF y en el nombre del archivo
- Permite elegir una opcion superior del formulario y marcarla con una cruz
- Pide el texto extra cuando eliges la primera o la ultima opcion
- Permite marcar todas las opciones de `PARTICOLARE`
- Pide el texto de `altro` en `PARTICOLARE`
- Permite anadir, editar y eliminar materiales en la tabla `DISTINTA`
- Coloca automaticamente la fecha de hoy
- Marca siempre `Spedizione a: Tecnidro`
- Marca siempre `Richiedente: Altro Ente` con `Rodriguez Manuel Mateo`
- Inserta la firma y genera el PDF con nombre `Richiesta di approvvigionamento N. 0001 - YYYY-MM-DD.pdf`

## Numeracion

El contador se guarda en `richiesta_counter.json` junto al programa. Si el archivo no existe, la numeracion empieza en `0001`.
La numeracion es anual: al cambiar de anio, vuelve automaticamente a `0001`.
El numero solo avanza cuando el PDF se genera correctamente.

## Archivos principales

- `app.py`: interfaz y generacion del PDF
- `assets/signature_rodriguez.png`: firma incluida en el PDF
- `requirements.txt`: dependencias de compilacion
- `build.ps1`: compila el `.exe`
