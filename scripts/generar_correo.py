#!/usr/bin/env python3
"""Genera el cuerpo HTML del correo de sustitución de poder.

El correo del juzgado lleva el texto formal completo (con tabla, negrita,
links). El PDF con firmas se manda como adjunto.

Salida: imprime el HTML a stdout, o lo guarda en --output si se pide.
"""

import argparse
import html as html_lib
import sys
from pathlib import Path

import diego_paths


SOCIEDAD_TOKENS = {"SA", "SAS", "LTDA", "CORP", "INC", "EU"}
SOCIEDAD_PHRASES = ("S EN C", "EN COMANDITA", "& CIA", "Y CIA")


def es_sociedad(nombre: str) -> bool:
    """Detecta si el cliente es persona jurídica (S.A., S.A.S., LTDA., etc.)."""
    if not nombre:
        return False
    cleaned = nombre.upper().replace(".", " ").replace(",", " ")
    tokens = set(cleaned.split())
    if tokens & SOCIEDAD_TOKENS:
        return True
    return any(p in cleaned for p in SOCIEDAD_PHRASES)


def esc(s) -> str:
    return html_lib.escape(str(s) if s is not None else "")


def build_html(juzgado, correo_juzgado, proceso, demandante, demandado,
               radicado, cliente_nombre, cliente_rol, fecha_audiencia,
               sustituyente, sustituido):

    if es_sociedad(cliente_nombre):
        cliente_desc = f"de la sociedad <b>{esc(cliente_nombre)}</b>"
    else:
        cliente_desc = f"del {esc(cliente_rol)} <b>{esc(cliente_nombre)}</b>"

    correo_link = ""
    if correo_juzgado:
        correo_link = (
            f'<p style="margin:0 0 4px 0;">'
            f'<a href="mailto:{esc(correo_juzgado)}">{esc(correo_juzgado)}</a>'
            f'</p>'
        )

    html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><style>
body {{ font-family: 'Century Gothic', Arial, sans-serif; font-size: 11pt; color: #000; line-height: 1.4; }}
p {{ margin: 0 0 12px 0; text-align: justify; }}
.header p {{ margin: 0 0 4px 0; text-align: left; }}
table.proceso {{ border-collapse: collapse; margin: 14px 0; width: 100%; }}
table.proceso td {{ border: 1px solid #000; padding: 5px 8px; vertical-align: top; font-size: 11pt; }}
table.proceso td.label {{ font-weight: bold; width: 28%; }}
</style></head><body>

<div class="header">
<p><b>SEÑORES</b></p>
<p><b>{esc(juzgado.upper())}</b></p>
{correo_link}
<p><b>E. S. D. V.</b></p>
</div>

<table class="proceso">
<tr><td class="label">REFERENCIA:</td><td>{esc(proceso)}</td></tr>
<tr><td class="label">DEMANDANTE:</td><td>{esc(demandante)}</td></tr>
<tr><td class="label">DEMANDADO:</td><td>{esc(demandado)}</td></tr>
<tr><td class="label">RADICADO:</td><td>{esc(radicado)}</td></tr>
<tr><td class="label">ASUNTO:</td><td>SUSTITUCIÓN DE PODER</td></tr>
</table>

<p><b>{esc(sustituyente['nombre'])}</b>, abogado en ejercicio mayor, y vecino de esta ciudad identificado con Cédula de Ciudadanía número {esc(sustituyente['cc'])} y portador de la Tarjeta Profesional número {esc(sustituyente['tp'])} y quien tiene como correo registrado <a href="mailto:{esc(sustituyente['correo'])}">{esc(sustituyente['correo'])}</a>, obrando como apoderado judicial {cliente_desc}, respetuosamente manifiesto que por medio del presente escrito <b>SUSTITUYO</b> el poder a mi conferido al abogado <b>{esc(sustituido['nombre'])}</b>, mayor de edad y vecino de Bogotá, identificado con Cédula de Ciudadanía No.{esc(sustituido['cc'])}, abogado en ejercicio y portador de la Tarjeta Profesional No.{esc(sustituido['tp'])}, para que actúe dentro de la audiencia programada para el día {esc(fecha_audiencia)}, en todas las etapas procesales que allí se desarrollen.</p>

<p>El apoderado queda ampliamente facultado a la luz del artículo 77 CGP para solicitar audiencia de conciliación, recibir, transigir, sustituir, desistir, pedir copias, interponer recursos y todas las demás necesarias para el buen desempeño del presente mandato, así como las que por la ley le sean propias.</p>

<p>De igual manera, por medio del presente me permito solicitar se me allegue enlace de acceso al expediente y el enlace de acceso a la diligencia.</p>

<p>Cordialmente,</p>

<p><b>{esc(sustituyente['nombre'])}</b></p>

</body></html>
"""
    return html


def main():
    p = argparse.ArgumentParser(
        description="Genera cuerpo HTML del correo de sustitución de poder"
    )
    p.add_argument("--juzgado", required=True)
    p.add_argument("--correo-juzgado", default="",
                   help="Correo del juzgado (sale como link en el encabezado del correo).")
    p.add_argument("--proceso", required=True)
    p.add_argument("--demandante", required=True)
    p.add_argument("--demandado", required=True)
    p.add_argument("--radicado", required=True)
    p.add_argument("--cliente-nombre", required=True)
    p.add_argument("--cliente-rol", choices=["demandado", "demandante"], required=True)
    p.add_argument("--fecha-audiencia", required=True)
    p.add_argument("--output", default=None,
                   help="Ruta donde guardar el HTML. Si se omite, sale a stdout.")
    a = p.parse_args()

    cfg = diego_paths.shared_config()
    sustituyente = cfg["sustituyente"]
    sustituido = cfg["sustituido"]

    html = build_html(
        juzgado=a.juzgado,
        correo_juzgado=a.correo_juzgado,
        proceso=a.proceso,
        demandante=a.demandante,
        demandado=a.demandado,
        radicado=a.radicado,
        cliente_nombre=a.cliente_nombre,
        cliente_rol=a.cliente_rol,
        fecha_audiencia=a.fecha_audiencia,
        sustituyente=sustituyente,
        sustituido=sustituido,
    )

    if a.output:
        out = Path(a.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(html, encoding="utf-8")
        print(str(out))
    else:
        sys.stdout.write(html)


if __name__ == "__main__":
    main()
