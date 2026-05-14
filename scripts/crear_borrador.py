#!/usr/bin/env python3
"""Crea un borrador en Outlook con un PDF adjunto.

Detecta el SO y delega a:
- Mac:     osascript crear_borrador.applescript
- Windows: powershell crear_borrador.ps1

Salida: imprime "OK: ..." al stdout si todo bien, o un mensaje de error.
Código de salida 0 = éxito, !=0 = error.
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def run_mac(recipient, subject, body, attachment):
    script = Path(__file__).parent / "crear_borrador.applescript"
    if not script.exists():
        raise FileNotFoundError(f"Falta {script}")
    if shutil.which("osascript") is None:
        raise EnvironmentError("osascript no disponible (¿es macOS?)")
    return subprocess.run(
        ["osascript", str(script), recipient, subject, body, attachment],
        capture_output=True, text=True,
    )


def run_windows(recipient, subject, body, attachment):
    script = Path(__file__).parent / "crear_borrador.ps1"
    if not script.exists():
        raise FileNotFoundError(f"Falta {script}")
    pwsh = shutil.which("pwsh") or shutil.which("powershell")
    if pwsh is None:
        raise EnvironmentError("PowerShell no encontrado en PATH")
    return subprocess.run(
        [pwsh, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script),
         "-Recipient", recipient, "-Subject", subject, "-Body", body,
         "-Attachment", attachment],
        capture_output=True, text=True,
    )


def main():
    p = argparse.ArgumentParser(description="Crea borrador en Outlook (cross-platform)")
    p.add_argument("--to", default="", help="Correo destinatario (vacío = sin destinatario)")
    p.add_argument("--subject", required=True)
    p.add_argument("--body", required=True)
    p.add_argument("--attachment", required=True, help="Ruta absoluta al PDF")
    a = p.parse_args()

    att = Path(a.attachment)
    if not att.exists():
        print(f"ERROR: el adjunto no existe en {att}", file=sys.stderr)
        sys.exit(1)

    if sys.platform == "darwin":
        result = run_mac(a.to, a.subject, a.body, str(att))
    elif sys.platform == "win32":
        result = run_windows(a.to, a.subject, a.body, str(att))
    else:
        print(f"ERROR: SO no soportado: {sys.platform}", file=sys.stderr)
        sys.exit(2)

    if result.returncode != 0:
        sys.stderr.write(result.stderr or "Sin stderr")
        sys.stderr.write("\n")
        sys.exit(result.returncode)

    print(result.stdout.strip())


if __name__ == "__main__":
    main()
