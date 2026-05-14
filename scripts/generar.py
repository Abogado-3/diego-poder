#!/usr/bin/env python3
"""Genera un PDF de sustitución de poder. Lee datos fijos desde la config
compartida del firm (en OneDrive); los variables vienen por argumentos.

Cross-platform: Mac y Windows.
"""

import argparse
import re
import sys
from datetime import date
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

import diego_paths

# Candidatos de fuentes Century Gothic: (carpeta, {regular, bold, italic, boldItalic})
FONT_CANDIDATES = [
    # Mac via Outlook (bundle)
    (Path("/Applications/Microsoft Outlook.app/Contents/Resources/DFonts"), {
        "regular": "Century Gothic.ttf",
        "bold": "Century Gothic Bold.ttf",
        "italic": "Century Gothic Italic.ttf",
        "boldItalic": "Century Gothic Bold Italic.ttf",
    }),
    # Windows system fonts
    (Path("C:/Windows/Fonts"), {
        "regular": "GOTHIC.TTF",
        "bold": "GOTHICB.TTF",
        "italic": "GOTHICI.TTF",
        "boldItalic": "GOTHICBI.TTF",
    }),
    # Mac user fonts
    (Path.home() / "Library" / "Fonts", {
        "regular": "Century Gothic.ttf",
        "bold": "Century Gothic Bold.ttf",
        "italic": "Century Gothic Italic.ttf",
        "boldItalic": "Century Gothic Bold Italic.ttf",
    }),
]


def find_font_set():
    """Devuelve (folder, {regular,bold,...}) del primer set que exista, o None."""
    for folder, names in FONT_CANDIDATES:
        if (folder / names["regular"]).exists() and (folder / names["bold"]).exists():
            return folder, names
    return None, None


def register_fonts():
    """Registra Century Gothic si la encuentra. Cae a Helvetica si no."""
    folder, names = find_font_set()
    if not folder:
        print("WARN: no encontré Century Gothic — uso Helvetica", file=sys.stderr)
        return "Helvetica", "Helvetica-Bold"

    try:
        pdfmetrics.registerFont(TTFont("CenturyGothic", str(folder / names["regular"])))
        pdfmetrics.registerFont(TTFont("CenturyGothic-Bold", str(folder / names["bold"])))
        if (folder / names["italic"]).exists():
            pdfmetrics.registerFont(TTFont("CenturyGothic-Italic",
                                           str(folder / names["italic"])))
        if (folder / names["boldItalic"]).exists():
            pdfmetrics.registerFont(TTFont("CenturyGothic-BoldItalic",
                                           str(folder / names["boldItalic"])))
        from reportlab.pdfbase.pdfmetrics import registerFontFamily
        registerFontFamily(
            "CenturyGothic",
            normal="CenturyGothic",
            bold="CenturyGothic-Bold",
            italic="CenturyGothic-Italic",
            boldItalic="CenturyGothic-BoldItalic",
        )
        return "CenturyGothic", "CenturyGothic-Bold"
    except Exception as e:
        print(f"WARN: fallo al cargar Century Gothic ({e}) — uso Helvetica", file=sys.stderr)
        return "Helvetica", "Helvetica-Bold"


def build_pdf(output_path, juzgado, proceso, demandante, demandado,
              radicado, cliente_nombre, cliente_rol, fecha_audiencia,
              sustituyente, sustituido, firma_sustituyente, firma_sustituido):

    font_regular, font_bold = register_fonts()

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=LETTER,
        leftMargin=2.5 * cm,
        rightMargin=2.5 * cm,
        topMargin=2.5 * cm,
        bottomMargin=2.5 * cm,
        title="Sustitución de Poder",
    )

    base = getSampleStyleSheet()["Normal"]
    body = ParagraphStyle("Body", parent=base, fontName=font_regular,
                         fontSize=11, leading=16, alignment=TA_JUSTIFY,
                         spaceAfter=10)
    header = ParagraphStyle("Header", parent=base, fontName=font_regular,
                            fontSize=11, leading=14)
    juzgado_st = ParagraphStyle("Juzgado", parent=base,
                                fontName=font_bold, fontSize=11,
                                leading=14, spaceAfter=12)

    story = []
    story.append(Paragraph("Señores,", header))
    story.append(Paragraph(juzgado.upper(), juzgado_st))

    table_data = [
        [Paragraph("<b>PROCESO</b>", header), Paragraph(proceso, header)],
        [Paragraph("<b>DEMANDANTE</b>", header), Paragraph(demandante, header)],
        [Paragraph("<b>DEMANDADO</b>", header), Paragraph(demandado, header)],
        [Paragraph("<b>RADICADO</b>", header), Paragraph(radicado, header)],
        [Paragraph("<b>REF.</b>", header), Paragraph("SUSTITUCIÓN DE PODER", header)],
    ]
    info = Table(table_data, colWidths=[4.2 * cm, 11 * cm])
    info.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LINEBELOW", (0, 0), (-1, -2), 0.5, colors.lightgrey),
    ]))
    story.append(info)
    story.append(Spacer(1, 0.6 * cm))

    body_text = (
        f"<b>{sustituyente['nombre']}</b>, abogado en ejercicio mayor, y vecino de esta "
        f"ciudad identificado con Cédula de Ciudadanía número {sustituyente['cc']} y "
        f"portador de la Tarjeta Profesional número {sustituyente['tp']} y quien tiene "
        f"como correo registrado {sustituyente['correo']}, obrando como apoderado "
        f"judicial del {cliente_rol} <b>{cliente_nombre}</b>, respetuosamente manifiesto "
        f"que por medio del presente escrito <b>SUSTITUYO</b> el poder a mi conferido al "
        f"abogado <b>{sustituido['nombre']}</b>, mayor de edad y vecino de Bogotá, "
        f"identificado con Cédula de Ciudadanía No. {sustituido['cc']}, abogado en "
        f"ejercicio y portador de la Tarjeta Profesional No. {sustituido['tp']}, para "
        f"que actúe dentro de la audiencia programada para el día {fecha_audiencia}, "
        f"en todas las etapas procesales que allí se desarrollen."
    )
    story.append(Paragraph(body_text, body))

    facultades = (
        "El apoderado queda ampliamente facultado a la luz del artículo 77 del CGP "
        "para solicitar audiencia de conciliación, recibir, transigir, sustituir, "
        "desistir, pedir copias, interponer recursos y todas las demás necesarias para "
        "el buen desempeño del presente mandato, así como las que por la ley le sean "
        "propias."
    )
    story.append(Paragraph(facultades, body))
    story.append(Spacer(1, 0.6 * cm))

    labels = Table(
        [[Paragraph("Atentamente,", header), Paragraph("Acepto,", header)]],
        colWidths=[8 * cm, 8 * cm],
    )

    sig_left = Image(str(firma_sustituyente), width=4.5 * cm, height=2.08 * cm)
    sig_left.hAlign = "LEFT"
    sig_right = Image(str(firma_sustituido), width=3.5 * cm, height=2.6 * cm)
    sig_right.hAlign = "LEFT"

    sig_row = Table([[sig_left, sig_right]], colWidths=[8 * cm, 8 * cm])
    sig_row.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
    ]))

    name_left = (
        f"<b>{sustituyente['nombre']}</b><br/>"
        f"C.C. {sustituyente['cc']}<br/>"
        f"T.P. {sustituyente['tp']}"
    )
    name_right = (
        f"<b>{sustituido['nombre']}</b><br/>"
        f"C.C. {sustituido['cc']}<br/>"
        f"T.P. {sustituido['tp']}"
    )
    names = Table(
        [[Paragraph(name_left, header), Paragraph(name_right, header)]],
        colWidths=[8 * cm, 8 * cm],
    )
    names.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))

    story.append(KeepTogether([labels, Spacer(1, 0.2 * cm), sig_row, names]))

    doc.build(story)


def main():
    p = argparse.ArgumentParser(description="Genera PDF de sustitución de poder")
    p.add_argument("--juzgado", required=True)
    p.add_argument("--proceso", required=True)
    p.add_argument("--demandante", required=True)
    p.add_argument("--demandado", required=True)
    p.add_argument("--radicado", required=True)
    p.add_argument("--cliente-nombre", required=True)
    p.add_argument("--cliente-rol", choices=["demandado", "demandante"], required=True)
    p.add_argument("--fecha-audiencia", required=True)
    p.add_argument("--output", default=None,
                   help="Ruta de salida. Si se omite, se genera en la carpeta "
                        "por defecto del usuario con nombre automático.")
    a = p.parse_args()

    cfg = diego_paths.shared_config()
    sustituyente = cfg["sustituyente"]
    sustituido = cfg["sustituido"]

    firmas_dir = diego_paths.signatures_dir()
    firma_sustituyente = firmas_dir / sustituyente["firma_archivo"]
    firma_sustituido = firmas_dir / sustituido["firma_archivo"]

    for label, path in [("sustituyente", firma_sustituyente),
                         ("sustituido", firma_sustituido)]:
        if not path.exists():
            print(f"ERROR: no encontré la firma del {label} en {path}",
                  file=sys.stderr)
            sys.exit(1)

    if a.output:
        out = Path(a.output)
    else:
        radicado_digits = re.sub(r"\D", "", a.radicado) or "XXXXXX"
        radicado_corto = radicado_digits[-6:]
        fecha_iso = date.today().isoformat()
        out = diego_paths.output_dir() / f"sustitucion_{radicado_corto}_{fecha_iso}.pdf"
    out.parent.mkdir(parents=True, exist_ok=True)

    build_pdf(
        output_path=out,
        juzgado=a.juzgado,
        proceso=a.proceso,
        demandante=a.demandante,
        demandado=a.demandado,
        radicado=a.radicado,
        cliente_nombre=a.cliente_nombre,
        cliente_rol=a.cliente_rol,
        fecha_audiencia=a.fecha_audiencia,
        sustituyente=sustituyente,
        sustituido=sustituido,
        firma_sustituyente=firma_sustituyente,
        firma_sustituido=firma_sustituido,
    )
    print(str(out))


if __name__ == "__main__":
    main()
