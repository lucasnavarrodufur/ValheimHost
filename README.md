# ValheimHost

ValheimHost es un coordinador simple para compartir un mundo local de Valheim entre amigos usando una carpeta sincronizada en la nube, como Google Drive.

Esta version esta pensada para jugar desde **Valheim normal en Steam**, hosteando desde el menu del juego e invitando amigos por Steam. No usa servidor dedicado.

## Para Que Sirve

Cuando varias personas quieren turnarse para hostear el mismo mundo, el problema es evitar pisarse los archivos. ValheimHost hace tres cosas:

- baja el mundo mas reciente antes de jugar;
- crea un lock para que una sola persona hostee a la vez;
- sube el mundo actualizado al terminar la sesion.

## Flujo De Uso

```text
host-valheim.bat
  -> toma lock
  -> baja mundonuevo
  -> vos abris Valheim y hosteas normal
  -> al terminar apretas Enter
  -> hace backup
  -> sube el mundo
  -> libera lock
```

## Archivos Del Mundo

El mundo configurado es:

```text
mundonuevo
```

ValheimHost sincroniza estos archivos:

```text
mundonuevo.db
mundonuevo.fwl
mundonuevo.db.old
mundonuevo.fwl.old
```

## Instalacion Rapida

1. Instalar Python desde https://www.python.org/downloads/
2. Marcar `Add python.exe to PATH` durante la instalacion.
3. Descargar o clonar este proyecto.
4. Copiar `config.portable.example.json` como `config.json`.
5. Ajustar `world_name` si el mundo no se llama `mundonuevo`.

Para probar:

```powershell
python valheim_host.py --config config.json doctor
```

Para hostear:

```powershell
python valheim_host.py --config config.json host
```

Tambien se puede usar doble clic:

```text
doctor-valheim.bat
host-valheim.bat
```

## Configuracion Portatil Recomendada

Si el programa esta dentro de la carpeta compartida de Google Drive, `config.json` puede usar:

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

- `cloud_dir: "."` usa como nube la carpeta donde esta `config.json`;
- `local_worlds_dir: ""` detecta automaticamente la carpeta local de mundos de Valheim del usuario actual;
- `host_id: ""` usa el nombre de la PC.

## Google Drive

La carpeta compartida tiene que estar sincronizada como carpeta normal en Windows. No alcanza con abrirla desde el navegador.

Rutas comunes:

```text
G:/Mi unidad/Server
G:/My Drive/Server
G:/Unidades compartidas/NombreDelDrive/Server
G:/Shared drives/NombreDelDrive/Server
```

Marcar la carpeta como `Disponible sin conexion` ayuda a evitar archivos virtuales sin descargar.

## Como Funciona El Lock

El lock es un archivo llamado:

```text
server.lock.json
```

Mientras alguien hostea, ValheimHost actualiza ese archivo cada pocos segundos. Si otra persona intenta hostear, el programa ve que el lock esta fresco y corta.

Si una PC se apaga mal, el lock vence despues de `lock_timeout_seconds`. Por defecto son 180 segundos.

## Estructura En La Carpeta Compartida

```text
Server/
  config.json
  valheim_host.py
  host-valheim.bat
  doctor-valheim.bat
  LEEME.md
  server.lock.json
  worlds/
    mundonuevo/
      mundonuevo.db
      mundonuevo.fwl
      mundonuevo.db.old
      mundonuevo.fwl.old
      manifest.json
  backups/
    mundonuevo/
      mundonuevo-20260810-221500.zip
```

## Notas

- Siempre abrir `host-valheim.bat` antes de hostear el mundo.
- Al terminar, volver a la ventana y apretar Enter.
- Esperar a que Google Drive termine de sincronizar antes de que hostee otra persona.
- El lock no puede impedir que alguien abra Valheim manualmente sin usar este programa.
