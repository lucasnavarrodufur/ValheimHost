#!/usr/bin/env python3
import argparse
import json
import os
import shutil
import socket
import sys
import threading
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


APP_NAME = "ValheimHost"
LOCK_FILE = "server.lock.json"
MANIFEST_FILE = "manifest.json"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def parse_iso(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def log(message: str) -> None:
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}", flush=True)


@dataclass
class Config:
    host_id: str
    world_name: str
    cloud_dir: Path
    local_worlds_dir: Path
    lock_timeout_seconds: int
    heartbeat_seconds: int
    save_settle_seconds: int
    backups_to_keep: int

    @property
    def cloud_world_dir(self) -> Path:
        return self.cloud_dir / "worlds" / self.world_name

    @property
    def cloud_backup_dir(self) -> Path:
        return self.cloud_dir / "backups" / self.world_name

    @property
    def lock_path(self) -> Path:
        return self.cloud_dir / LOCK_FILE


class ValheimHostError(Exception):
    pass


def load_config(path: Path) -> Config:
    if not path.exists():
        raise ValheimHostError(f"No existe el archivo de config: {path}")

    path = path.resolve()
    raw = json.loads(path.read_text(encoding="utf-8"))
    base_dir = path.parent

    return Config(
        host_id=raw.get("host_id") or socket.gethostname(),
        world_name=required(raw, "world_name"),
        cloud_dir=resolve_config_path(raw.get("cloud_dir") or ".", base_dir),
        local_worlds_dir=resolve_config_path(
            raw.get("local_worlds_dir") or default_worlds_dir(),
            base_dir,
        ),
        lock_timeout_seconds=int(raw.get("lock_timeout_seconds", 180)),
        heartbeat_seconds=int(raw.get("heartbeat_seconds", 30)),
        save_settle_seconds=int(raw.get("save_settle_seconds", 20)),
        backups_to_keep=int(raw.get("backups_to_keep", 10)),
    )


def resolve_config_path(value: str, base_dir: Path) -> Path:
    path = Path(value).expanduser()
    if path.is_absolute():
        return path
    return (base_dir / path).resolve()


def default_worlds_dir() -> str:
    return str(Path.home() / "AppData" / "LocalLow" / "IronGate" / "Valheim" / "worlds_local")


def required(raw: dict, key: str) -> str:
    value = raw.get(key)
    if not value:
        raise ValheimHostError(f"Falta '{key}' en config.json")
    return str(value)


def ensure_dirs(config: Config) -> None:
    config.cloud_dir.mkdir(parents=True, exist_ok=True)
    config.cloud_world_dir.mkdir(parents=True, exist_ok=True)
    config.cloud_backup_dir.mkdir(parents=True, exist_ok=True)
    config.local_worlds_dir.mkdir(parents=True, exist_ok=True)


def read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValheimHostError(f"No pude leer JSON valido en {path}: {exc}") from exc


def safe_exists(path: Path) -> bool | None:
    try:
        return path.exists()
    except PermissionError:
        return None


def format_check(value: bool | None) -> str:
    if value is None:
        return "SIN PERMISO PARA CHEQUEAR"
    return "OK" if value else "FALTA"


def write_json_atomic(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + f".{uuid.uuid4().hex}.tmp")
    temp.write_text(json.dumps(data, indent=2), encoding="utf-8")
    temp.replace(path)


def acquire_lock(config: Config, force: bool = False) -> None:
    lock = read_json(config.lock_path)
    if lock and not force:
        updated_at = parse_iso(lock["updated_at"])
        age = (datetime.now(timezone.utc) - updated_at).total_seconds()
        if age < config.lock_timeout_seconds:
            owner = lock.get("host_id", "desconocido")
            raise ValheimHostError(
                f"El servidor parece activo en '{owner}'. "
                f"Ultimo heartbeat hace {int(age)}s. Usa --force-lock solo si estas seguro."
            )
        log(f"Lock viejo detectado ({int(age)}s). Lo voy a tomar.")

    payload = {
        "host_id": config.host_id,
        "world_name": config.world_name,
        "created_at": utc_now_iso(),
        "updated_at": utc_now_iso(),
        "machine": socket.gethostname(),
        "pid": os.getpid(),
    }
    write_json_atomic(config.lock_path, payload)

    current = read_json(config.lock_path)
    if not current or current.get("host_id") != config.host_id:
        raise ValheimHostError("No pude confirmar el lock compartido.")

    log(f"Lock adquirido para '{config.world_name}' como {config.host_id}.")


def refresh_lock(config: Config) -> None:
    lock = read_json(config.lock_path)
    if not lock or lock.get("host_id") != config.host_id:
        raise ValheimHostError("Se perdio el lock. Deteniendo para evitar doble host.")
    lock["updated_at"] = utc_now_iso()
    lock["pid"] = os.getpid()
    write_json_atomic(config.lock_path, lock)


def release_lock(config: Config) -> None:
    lock = read_json(config.lock_path)
    if lock and lock.get("host_id") == config.host_id:
        config.lock_path.unlink(missing_ok=True)
        log("Lock liberado.")


def copy_tree(src: Path, dst: Path) -> None:
    if not src.exists():
        return
    dst.mkdir(parents=True, exist_ok=True)
    for item in src.iterdir():
        target = dst / item.name
        if item.is_dir():
            copy_tree(item, target)
        else:
            shutil.copy2(item, target)


def sync_down(config: Config) -> None:
    log("Bajando mundo desde la carpeta compartida...")
    copy_tree(config.cloud_world_dir, config.local_worlds_dir)
    log("Mundo local actualizado.")


def sync_up(config: Config) -> None:
    log("Subiendo mundo guardado a la carpeta compartida...")
    copy_tree(config.local_worlds_dir, config.cloud_world_dir)
    write_json_atomic(
        config.cloud_world_dir / MANIFEST_FILE,
        {
            "world_name": config.world_name,
            "uploaded_at": utc_now_iso(),
            "host_id": config.host_id,
            "machine": socket.gethostname(),
        },
    )
    log("Mundo subido.")


def world_files(config: Config) -> Iterable[Path]:
    patterns = (
        f"{config.world_name}.db",
        f"{config.world_name}.fwl",
        f"{config.world_name}.db.old",
        f"{config.world_name}.fwl.old",
    )
    for pattern in patterns:
        yield from config.local_worlds_dir.rglob(pattern)


def snapshot_state(paths: Iterable[Path]) -> tuple[tuple[str, int, int], ...]:
    state = []
    for path in paths:
        if path.exists():
            stat = path.stat()
            state.append((str(path), stat.st_size, stat.st_mtime_ns))
    return tuple(sorted(state))


def wait_for_save_settle(config: Config) -> None:
    log("Esperando que los archivos del mundo queden estables...")
    stable_since = time.monotonic()
    previous = snapshot_state(world_files(config))

    while time.monotonic() - stable_since < config.save_settle_seconds:
        time.sleep(2)
        current = snapshot_state(world_files(config))
        if current != previous:
            previous = current
            stable_since = time.monotonic()


def create_backup(config: Config) -> None:
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_base = config.cloud_backup_dir / f"{config.world_name}-{timestamp}"
    shutil.make_archive(str(backup_base), "zip", root_dir=config.local_worlds_dir)
    log(f"Backup creado: {backup_base.name}.zip")
    prune_backups(config)


def prune_backups(config: Config) -> None:
    backups = sorted(config.cloud_backup_dir.glob("*.zip"), key=lambda p: p.stat().st_mtime)
    excess = len(backups) - config.backups_to_keep
    for old_backup in backups[:max(0, excess)]:
        old_backup.unlink(missing_ok=True)


def keep_lock_alive(config: Config, stop_event: threading.Event, error_holder: list[Exception]) -> None:
    while not stop_event.wait(config.heartbeat_seconds):
        try:
            refresh_lock(config)
        except Exception as exc:
            error_holder.append(exc)
            stop_event.set()


def wait_for_manual_session(config: Config) -> None:
    stop_event = threading.Event()
    heartbeat_errors: list[Exception] = []
    heartbeat = threading.Thread(
        target=keep_lock_alive,
        args=(config, stop_event, heartbeat_errors),
        daemon=True,
    )
    heartbeat.start()

    try:
        log("Mundo listo. Abri Valheim desde Steam y hostealo desde el juego normal.")
        log("Cuando termines y estes en el menu principal o con el juego cerrado, volve aca y apreta Enter.")
        input()
    finally:
        stop_event.set()
        heartbeat.join(timeout=5)

    if heartbeat_errors:
        raise ValheimHostError(str(heartbeat_errors[0]))


def doctor(config: Config) -> None:
    checks = {
        "cloud_dir": safe_exists(config.cloud_dir),
        "local_worlds_dir": safe_exists(config.local_worlds_dir),
    }
    for name, ok in checks.items():
        print(f"{name}: {format_check(ok)}")

    try:
        lock = read_json(config.lock_path)
    except PermissionError:
        print("lock: SIN PERMISO PARA CHEQUEAR")
        return
    if lock:
        updated_at = parse_iso(lock["updated_at"])
        age = (datetime.now(timezone.utc) - updated_at).total_seconds()
        print(f"lock: ocupado por {lock.get('host_id')} hace {int(age)}s")
    else:
        print("lock: libre")


def run_host(config: Config, force_lock: bool) -> int:
    ensure_dirs(config)
    acquire_lock(config, force=force_lock)
    try:
        sync_down(config)
        wait_for_manual_session(config)
        wait_for_save_settle(config)
        create_backup(config)
        sync_up(config)
        return 0
    finally:
        release_lock(config)


def main() -> int:
    parser = argparse.ArgumentParser(description="Coordinador local compartido para Valheim.")
    parser.add_argument("--config", default="config.json", help="Ruta al config JSON.")

    subparsers = parser.add_subparsers(dest="command", required=True)
    host_parser = subparsers.add_parser("host", help="Baja mundo, reserva la sesion y sube al terminar.")
    host_parser.add_argument("--force-lock", action="store_true", help="Toma un lock viejo o colgado.")
    subparsers.add_parser("doctor", help="Chequea rutas y estado del lock.")

    args = parser.parse_args()
    try:
        config = load_config(Path(args.config))
        if args.command == "doctor":
            doctor(config)
            return 0
        if args.command == "host":
            return run_host(config, force_lock=args.force_lock)
    except ValheimHostError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
