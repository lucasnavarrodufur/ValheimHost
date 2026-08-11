# Guia Rapida: Valheim Compartido

Esta carpeta permite que varios amigos se turnen para hostear el mundo `mundonuevo` desde Valheim normal en Steam.

## 1. Preparar La PC

Antes de hostear, cada persona necesita:

- Valheim instalado desde Steam.
- Python instalado desde https://www.python.org/downloads/
- La carpeta compartida sincronizada con Google Drive para computadoras.

Al instalar Python, marcar:

```text
Add python.exe to PATH
```

## 2. Sincronizar La Carpeta Con Google Drive

La carpeta tiene que aparecer en el Explorador de archivos de Windows. No alcanza con verla desde el navegador.

Pasos:

1. Instalar Google Drive para computadoras.
2. Aceptar la carpeta compartida o agregarla a tu unidad.
3. Abrir la carpeta desde el Explorador de archivos.
4. Verificar que existan estos archivos:
   - `host-valheim.bat`
   - `doctor-valheim.bat`
   - `config.json`
   - `valheim_host.py`
5. Click derecho sobre la carpeta y elegir `Disponible sin conexion`, si aparece la opcion.

Rutas comunes:

```text
G:/Mi unidad/Server
G:/My Drive/Server
G:/Unidades compartidas/NombreDelDrive/Server
G:/Shared drives/NombreDelDrive/Server
```

No importa si cada PC tiene una ruta distinta. El programa usa la carpeta donde esta `config.json`.

## 3. Chequear Estado

Hacer doble clic en:

```text
doctor-valheim.bat
```

Lo ideal es ver:

```text
cloud_dir: OK
local_worlds_dir: OK
lock: libre
```

Si `lock` aparece ocupado, otra persona esta hosteando o quedo una sesion anterior sin cerrar.

## 4. Hostear

Hacer doble clic en:

```text
host-valheim.bat
```

Cuando la ventana diga que el mundo esta listo:

1. Abrir Valheim desde Steam.
2. Elegir el mundo `mundonuevo`.
3. Activar la opcion para hostear desde el juego.
4. Invitar amigos por Steam.
5. Jugar normal.

## 5. Terminar La Sesion

Cuando terminen:

1. Salir al menu principal o cerrar Valheim.
2. Volver a la ventana de `host-valheim.bat`.
3. Apretar Enter.
4. Esperar a que termine de subir el mundo.

Cuando el programa termina, otra persona ya puede hostear desde su PC.

## Regla De Oro

Siempre usar `host-valheim.bat` antes de abrir el mundo. Si alguien hostea manualmente sin usar este archivo, el programa no puede evitar conflictos ni asegurar que el mundo quede actualizado.
