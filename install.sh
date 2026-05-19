#!/bin/bash
# Instalador de DIEGO para Mac.
# Uso: curl -fsSL https://raw.githubusercontent.com/Abogado-3/diego-poder/main/install.sh | bash

set -e

echo ""
echo "=============================================="
echo "  DIEGO — Instalador para Mac"
echo "=============================================="
echo ""

REPO="Abogado-3/diego-poder"
INSTALL_DIR="$HOME/.claude/diego-poder"

# --- 1. Verificar Python ---
if ! command -v python3 &> /dev/null; then
    echo "❌ ERROR: Python 3 no está instalado en este Mac."
    echo "   Instálalo desde https://www.python.org/downloads/ y vuelve a correr este script."
    exit 1
fi
echo "✅ Python 3 encontrado: $(python3 --version)"

# --- 2. Instalar dependencias Python ---
echo ""
echo "→ Instalando librerías (reportlab, openpyxl)..."
python3 -m pip install --user --quiet reportlab openpyxl
echo "✅ Librerías instaladas."

# --- 3. Descargar el código del repo ---
echo ""
echo "→ Descargando DIEGO desde GitHub..."
TMP_DIR=$(mktemp -d)
trap "rm -rf $TMP_DIR" EXIT

curl -fsSL "https://github.com/$REPO/archive/refs/heads/main.tar.gz" \
    | tar -xz -C "$TMP_DIR"
REPO_DIR="$TMP_DIR/diego-poder-main"

if [ ! -d "$REPO_DIR" ]; then
    echo "❌ ERROR: no pude descargar el repo."
    exit 1
fi
echo "✅ Código descargado."

# --- 4. Copiar archivos a ~/.claude/ ---
echo ""
echo "→ Instalando archivos en $INSTALL_DIR..."
mkdir -p "$HOME/.claude/agents"
mkdir -p "$INSTALL_DIR/scripts"
mkdir -p "$INSTALL_DIR/scheduled-task-template"

cp "$REPO_DIR/agents/diego.md" "$HOME/.claude/agents/diego.md"
cp "$REPO_DIR/scripts/"* "$INSTALL_DIR/scripts/"
cp "$REPO_DIR/scheduled-task-template/briefing-prompt.md" "$INSTALL_DIR/scheduled-task-template/"
echo "✅ Archivos copiados."

# --- 5. Autodetectar OneDrive del firm ---
echo ""
echo "→ Buscando el OneDrive del firm..."
DETECTED=$(python3 "$INSTALL_DIR/scripts/diego_paths.py" --autodetect 2>/dev/null \
    | python3 -c "import json,sys; d=json.load(sys.stdin).get('detected'); print(d if d else '')" 2>/dev/null || echo "")

FIRM_PATH=""
if [ -n "$DETECTED" ]; then
    echo "✅ OneDrive detectado:"
    echo "   $DETECTED"
    echo ""
    read -p "¿Es correcto? [Y/n]: " RESP </dev/tty
    if [ -z "$RESP" ] || [ "$RESP" = "Y" ] || [ "$RESP" = "y" ]; then
        FIRM_PATH="$DETECTED"
    fi
fi

if [ -z "$FIRM_PATH" ]; then
    echo ""
    echo "Pega la ruta absoluta donde tienes sincronizado 'ABOGADO01 - ARCHIVO DIGITAL CAVV'."
    echo "Ejemplo: /Users/tunombre/Library/CloudStorage/OneDrive-.../ABOGADO01 - ARCHIVO DIGITAL CAVV"
    read -p "Ruta: " FIRM_PATH </dev/tty
fi

if [ ! -d "$FIRM_PATH" ]; then
    echo "❌ ERROR: la ruta '$FIRM_PATH' no existe."
    echo "   Verifica que el OneDrive del firm esté sincronizado en este Mac y vuelve a correr."
    exit 1
fi

# --- 6. Verificar carpeta compartida del firm ---
DIEGO_DIR="$FIRM_PATH/0. DIEGO - Sustitución de Poder"
if [ ! -d "$DIEGO_DIR" ]; then
    echo ""
    echo "⚠️  La carpeta compartida '0. DIEGO - Sustitución de Poder' no existe aún en el OneDrive del firm."
    echo "   El primer abogado del firm que instale DIEGO debe crearla con la config compartida."
    echo "   (Ve al README en GitHub para los pasos.)"
    echo "   Por ahora guardo la config local, pero DIEGO no podrá generar PDFs hasta que exista esa carpeta."
fi

# --- 7. Guardar config local del usuario ---
mkdir -p "$HOME/.config/diego-poder"
cat > "$HOME/.config/diego-poder/config.json" <<EOF
{
  "firm_path": "$FIRM_PATH"
}
EOF
echo ""
echo "✅ Config local guardada en ~/.config/diego-poder/config.json"

# --- 8. Verificación final ---
echo ""
echo "→ Verificando instalación..."
python3 "$INSTALL_DIR/scripts/diego_paths.py" --show

echo ""
echo "=============================================="
echo "  ✅ DIEGO instalado correctamente"
echo "=============================================="
echo ""
echo "Próximos pasos:"
echo ""
echo "1. Abre Claude Code y di:  Diego, hola"
echo "   (debe presentarse y responder)"
echo ""
echo "2. Para activar el briefing diario:  Diego, configura mi briefing diario"
echo ""
echo "3. Para pedir una sustitución:  Diego, prepara una sustitución de poder para …"
echo ""
