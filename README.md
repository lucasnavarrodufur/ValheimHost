# ValheimHost - Guia Simple

Este proyecto sirve para que un grupo de personas pueda turnarse para hostear el mismo mundo de Valheim usando Google Drive.

Esta pensado para **Valheim normal desde Steam**, no para servidor dedicado. La persona que hostea abre el mundo desde el juego e invita a los demas por Steam.

## Que Hace

ValheimHost se encarga de:

- bajar el mundo mas reciente antes de jugar;
- evitar que dos personas hosteen al mismo tiempo;
- subir el mundo actualizado cuando termina la sesion;
- guardar backups automaticos.

El mundo configurado es:

```text
mundonuevo
```

Los archivos reales del mundo son:

```text
mundonuevo.db
mundonuevo.fwl
```

## Que Tiene Que Hacer Cada Persona

Cada persona que quiera hostear puede entrar al repo:

```text
https://github.com/lucasnavarrodufur/ValheimHost
```

Y seguir estos pasos:

1. Descargar el repo.
2. Instalar Python.
3. Tener sincronizada la carpeta compartida de Google Drive.
4. Copiar los archivos del repo dentro de esa carpeta compartida.
5. Copiar `config.portable.example.json` como `config.json`.
6. Ejecutar `doctor-valheim.bat`.
7. Ejecutar `host-valheim.bat` cuando quiera hostear.

## 1. Instalar Python

Descargar Python desde:

```text
https://www.python.org/downloads/
```

Durante la instalacion, marcar esta opcion:

```text
Add python.exe to PATH
```

Despues de instalar, cerrar y abrir de nuevo cualquier ventana de PowerShell o consola.

## 2. Sincronizar La Carpeta De Google Drive

La carpeta compartida tiene que aparecer como carpeta normal en el Explorador de archivos de Windows.

No alcanza con verla desde el navegador.

Pasos:

1. Instalar Google Drive para computadoras.
2. Aceptar la carpeta compartida.
3. Abrir Google Drive desde el Explorador de archivos.
4. Entrar a la carpeta compartida, por ejemplo `Server`.
5. Marcarla como `Disponible sin conexion`, si aparece esa opcion.

Rutas comunes de Google Drive en Windows:

```text
G:/Mi unidad/Server
G:/My Drive/Server
G:/Unidades compartidas/NombreDelDrive/Server
G:/Shared drives/NombreDelDrive/Server
```

No importa si cada PC tiene una ruta distinta. El programa puede usar la carpeta donde esta `config.json`.

## 3. Poner El Programa En La Carpeta Compartida

Dentro de la carpeta compartida de Google Drive tienen que quedar estos archivos:

```text
Server/
  valheim_host.py
  config.json
  host-valheim.bat
  doctor-valheim.bat
  README.md
```

Para crear `config.json`, copiar:

```text
config.portable.example.json
```

y renombrarlo como:

```text
config.json
```

El `config.json` recomendado es:

```json
{
  "host_id": "",
  "world_name": "mundonuevo",
  "cloud_dir": ".",
  "local_worlds_dir": "",
  "lock_timeout_seconds": 180,
  "heartbeat_seconds": 30,
  "save_settle_seconds": 20,
  "backups_to_keep": 10
}
```

Con esa configuracion:

- `cloud_dir: "."` usa como nube la misma carpeta compartida;
- `local_worlds_dir: ""` detecta automaticamente la carpeta local de mundos de Valheim;
- `host_id: ""` usa automaticamente el nombre de la PC.

## 4. Chequear Que Este Todo Bien

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

## 5. Hostear

Hacer doble clic en:

```text
host-valheim.bat
```

El programa va a:

```text
tomar lock -> bajar mundo -> esperar mientras jugas
```

Cuando la ventana diga que el mundo esta listo:

1. Abrir Valheim desde Steam.
2. Elegir el mundo `mundonuevo`.
3. Activar la opcion de hostear desde el juego.
4. Invitar amigos por Steam.
5. Jugar normal.

## 6. Terminar La Sesion

Cuando terminen de jugar:

1. Salir al menu principal o cerrar Valheim.
2. Volver a la ventana de `host-valheim.bat`.
3. Apretar Enter.
4. Esperar a que termine de subir el mundo.

El programa va a:

```text
esperar guardado -> crear backup -> subir mundo -> liberar lock
```

Cuando termina, otra persona ya puede hostear.

## Como Funciona El Lock

El lock es un archivo que se crea en la carpeta compartida:

```text
server.lock.json
```

Mientras alguien hostea, el programa actualiza ese archivo cada pocos segundos. Si otra persona intenta hostear, el programa ve que el lock esta activo y no la deja avanzar.

Si una PC se apaga mal, el lock vence despues de 180 segundos.

## Regla Importante

Siempre usar:

```text
host-valheim.bat
```

antes de abrir el mundo.

Si alguien hostea manualmente sin usar el programa, ValheimHost no puede evitar conflictos ni asegurar que el mundo quede actualizado.

## Resumen Corto

```text
1. Sincronizar carpeta de Google Drive
2. Abrir doctor-valheim.bat para chequear
3. Abrir host-valheim.bat para reservar el mundo
4. Abrir Valheim y hostear mundonuevo
5. Al terminar, volver al .bat y apretar Enter
```
