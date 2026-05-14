#!/usr/bin/env python3
"""Helpers de configuración y paths para DIEGO.

Dos capas de config:

1. **Local** (por usuario, por máquina): vive en
   - Mac:   ~/.config/diego-poder/config.json
   - Win:   %APPDATA%\\diego-poder\\config.json
   Contiene solo `firm_path` — la ruta local del OneDrive del firm.
   La crea el comando `/diego-setup` la primera vez.

2. **Compartida** (firm-wide): vive en
   <firm_path>/0. DIEGO - Sustitución de Poder/config.json
   Contiene los datos de sustituyente, sustituido, firmas, etc.
   Igual para todos los usuarios de la oficina.
"""

import json
import os
import sys
from pathlib import Path
from typing import Optional

APP_NAME = "diego-poder"
DIEGO_SUBDIR_DEFAULT = "0. DIEGO - Sustitución de Poder"
INDICE_XLSX_DEFAULT = "1. ÍNDICE ARCHIVO DOCUMENTAL.xlsx"


def user_config_path() -> Path:
    """Ruta del archivo de config local del usuario."""
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", str(Path.home()))) / APP_NAME
    else:
        base = Path.home() / ".config" / APP_NAME
    return base / "config.json"


def load_user_config() -> dict:
    p = user_config_path()
    if not p.exists():
        raise FileNotFoundError(
            f"No encontré la config local en {p}.\n"
            f"Corre /diego-setup en Claude Code para inicializarla."
        )
    return json.loads(p.read_text(encoding="utf-8"))


def save_user_config(cfg: dict) -> Path:
    p = user_config_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(cfg, indent=2, ensure_ascii=False), encoding="utf-8")
    return p


def firm_root() -> Path:
    return Path(load_user_config()["firm_path"])


def diego_shared_dir() -> Path:
    cfg = load_user_config()
    return Path(cfg["firm_path"]) / cfg.get("diego_subdir", DIEGO_SUBDIR_DEFAULT)


def shared_config() -> dict:
    """Lee la config compartida del firm desde OneDrive."""
    p = diego_shared_dir() / "config.json"
    if not p.exists():
        raise FileNotFoundError(
            f"No encontré config.json compartida en {p}.\n"
            f"Pide al admin del firm que la cree o corre /diego-setup."
        )
    return json.loads(p.read_text(encoding="utf-8"))


def signatures_dir() -> Path:
    """Carpeta con firma_*.jpeg — vive junto al config compartido."""
    return diego_shared_dir()


def directorio_csv_path() -> Path:
    """Ruta del CSV compartido de juzgados."""
    return diego_shared_dir() / "directorio_juzgados.csv"


def indice_xlsx_path() -> Path:
    """Ruta del índice maestro de casos del firm."""
    cfg = load_user_config()
    return Path(cfg["firm_path"]) / cfg.get("indice_xlsx", INDICE_XLSX_DEFAULT)


def output_dir() -> Path:
    """Carpeta donde se guardan los PDFs generados (local por usuario)."""
    cfg = load_user_config()
    if "output_dir" in cfg:
        return Path(cfg["output_dir"])
    return Path.home() / "Documents" / "DIEGO - Sustituciones"


def briefings_dir() -> Path:
    """Carpeta donde se guardan los briefings JSON diarios (local por usuario)."""
    cfg = load_user_config()
    if "briefings_dir" in cfg:
        return Path(cfg["briefings_dir"])
    return Path.home() / "Documents" / "DIEGO - Sustituciones" / "briefings"


def autodetect_onedrive_mac() -> Optional[Path]:
    """Intenta encontrar el OneDrive del firm en Mac. Devuelve None si no."""
    base = Path.home() / "Library" / "CloudStorage"
    if not base.exists():
        return None
    for d in base.iterdir():
        if "cavvabogados" in d.name.lower():
            for sub in d.iterdir():
                if "ARCHIVO DIGITAL CAVV" in sub.name.upper():
                    return sub
    return None


def autodetect_onedrive_windows() -> Optional[Path]:
    """Intenta encontrar el OneDrive del firm en Windows."""
    candidates = [
        Path.home() / "CAVV Abogados Consultores SAS",
        Path.home() / "OneDrive - CAVV Abogados Consultores SAS",
    ]
    for c in candidates:
        if c.exists():
            for sub in c.iterdir():
                if "ARCHIVO DIGITAL CAVV" in sub.name.upper():
                    return sub
    return None


def autodetect_onedrive() -> Optional[Path]:
    if sys.platform == "darwin":
        return autodetect_onedrive_mac()
    if sys.platform == "win32":
        return autodetect_onedrive_windows()
    return None


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser(description="Helpers de paths de DIEGO (debug)")
    p.add_argument("--show", action="store_true", help="Muestra los paths resueltos")
    p.add_argument("--autodetect", action="store_true",
                   help="Intenta autodetectar el OneDrive del firm")
    args = p.parse_args()

    if args.autodetect:
        d = autodetect_onedrive()
        print(json.dumps({"detected": str(d) if d else None}, ensure_ascii=False))
        sys.exit(0)

    if args.show:
        try:
            print(json.dumps({
                "user_config": str(user_config_path()),
                "firm_root": str(firm_root()),
                "diego_shared": str(diego_shared_dir()),
                "directorio_csv": str(directorio_csv_path()),
                "indice_xlsx": str(indice_xlsx_path()),
                "output_dir": str(output_dir()),
                "briefings_dir": str(briefings_dir()),
            }, indent=2, ensure_ascii=False))
        except Exception as e:
            print(json.dumps({"error": str(e)}, ensure_ascii=False))
            sys.exit(1)
