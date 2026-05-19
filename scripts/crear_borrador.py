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


def run_mac(recipient, subject, body, attachment, body_is_html):
    script = Path(__file__).parent / "crear_borrador.applescript"
    if not script.exists():
        raise FileNotFoundError(f"Falta {script}")
    if shutil.which("osascript") is None:
        raise EnvironmentError("osascript no disponible (¿es macOS?)")
    body_kind = "html" if body_is_html else "plain"
    return subprocess.run(
        ["osascript", str(script), recipient, subject, body, attachment, body_kind],
        capture_output=True, text=True,
    )


def run_windows(recipient, subject, body, attachment, body_is_html):
    script = Path(__file__).parent / "crear_borrador.ps1"
    if not script.exists():
        raise FileNotFoundError(f"Falta {script}")
    pwsh = shutil.which("pwsh") or shutil.which("powershell")
    if pwsh is None:
        raise EnvironmentError("PowerShell no encontrado en PATH")
    cmd = [pwsh, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script),
           "-Recipient", recipient, "-Subject", subject, "-Body", body,
           "-Attachment", attachment]
    if body_is_html:
        cmd += ["-BodyIsHtml"]
    return subprocess.run(cmd, capture_output=True, text=True)


def main():
    p = argparse.ArgumentParser(description="Crea borrador en Outlook (cross-platform)")
    p.add_argument("--to", default="", help="Correo destinatario (vacío = sin destinatario)")
    p.add_argument("--subject", required=True)
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--body", help="Cuerpo del correo como texto plano")
    g.add_argument("--body-html", help="Cuerpo del correo como HTML")
    g.add_argument("--body-html-file", help="Ruta a archivo .html con el cuerpo")
    p.add_argument("--attachment", required=True, help="Ruta absoluta al PDF")
    a = p.parse_args()

    att = Path(a.attachment)
    if not att.exists():
        print(f"ERROR: el adjunto no existe en {att}", file=sys.stderr)
        sys.exit(1)

    if a.body_html_file:
        body_path = Path(a.body_html_file)
        if not body_path.exists():
            print(f"ERROR: no encontré el HTML del cuerpo en {body_path}", file=sys.stderr)
            sys.exit(1)
        body = body_path.read_text(encoding="utf-8")
        body_is_html = True
    elif a.body_html:
        body = a.body_html
        body_is_html = True
    else:
        body = a.body
        body_is_html = False

    if sys.platform == "darwin":
        result = run_mac(a.to, a.subject, body, str(att), body_is_html)
    elif sys.platform == "win32":
        result = run_windows(a.to, a.subject, body, str(att), body_is_html)
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
