---
description: Configura DIEGO en esta máquina (primera vez). Detecta el OneDrive del firm, crea la config local y registra el briefing diario.
---

Tu trabajo es configurar DIEGO en esta máquina. Sigue estos pasos en orden.

# Paso 1: Verificar dependencias

Corre estos chequeos y reporta resultado:

```bash
python3 --version
python3 -c "import reportlab; print('reportlab', reportlab.Version)"
python3 -c "import openpyxl; print('openpyxl', openpyxl.__version__)"
```

Si alguno falla, dile al usuario que instale lo que falta:
```bash
python3 -m pip install -r "${CLAUDE_PLUGIN_ROOT}/requirements.txt"
```

No continúes hasta que estén instaladas.

# Paso 2: Detectar el OneDrive del firm

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/diego_paths.py" --autodetect
```

Resultado JSON:
- Si `detected` no es null → muéstrale al usuario la ruta detectada y pregúntale "¿Es correcta?" (AskUserQuestion).
- Si `detected` es null o el usuario dice que no → AskUserQuestion para que pegue la ruta absoluta donde tiene sincronizado el OneDrive del firm (ABOGADO01 - ARCHIVO DIGITAL CAVV).

Guarda esa ruta como variable `FIRM_PATH`.

# Paso 3: Verificar que la ruta existe y tiene la estructura esperada

```bash
ls "$FIRM_PATH" 2>&1 | head -20
```

Debe ver "1. ÍNDICE ARCHIVO DOCUMENTAL.xlsx" y subcarpetas como "2. SEGUROS ALFA", etc.

Si no aparecen, dile al usuario que verifique la ruta y vuelve al paso 2.

# Paso 4: Guardar la config local del usuario

```bash
python3 -c "
import sys
sys.path.insert(0, '${CLAUDE_PLUGIN_ROOT}/scripts')
import diego_paths
cfg = {'firm_path': '$FIRM_PATH'}
p = diego_paths.save_user_config(cfg)
print('Config local guardada en', p)
"
```

# Paso 5: Verificar/crear la carpeta compartida del firm "0. DIEGO - Sustitución de Poder"

```bash
DIEGO_DIR="$FIRM_PATH/0. DIEGO - Sustitución de Poder"
ls "$DIEGO_DIR" 2>&1 | head -20
```

Si la carpeta NO existe:
- Pregunta al usuario: "¿Soy el primer usuario del firm en instalar DIEGO? Si sí, voy a crear la carpeta compartida con la config del firm. Necesito que tengas las firmas (firma_carlos.jpeg, firma_santiago.jpeg) listas para copiar — ¿las tienes?"
- Si dice sí:
  ```bash
  mkdir -p "$DIEGO_DIR"
  ```
- Pídele al usuario que copie las firmas a `$DIEGO_DIR/firma_carlos.jpeg` y `$DIEGO_DIR/firma_santiago.jpeg`.
- Crea el `config.json` compartido con los datos por defecto del firm:
  ```bash
  cat > "$DIEGO_DIR/config.json" <<'JSON'
  {
    "sustituyente": {
      "nombre": "CARLOS ANDRÉS VARGAS VARGAS",
      "cc": "79.687.849 de Bogotá",
      "tp": "111.896 del C.S.J",
      "correo": "cvargas.abogado@gmail.com",
      "firma_archivo": "firma_carlos.jpeg"
    },
    "sustituido": {
      "nombre": "SANTIAGO BERMÚDEZ CRUZ",
      "cc": "1.001.204.828 de Mosquera",
      "tp": "449.826 del C. S. de la J.",
      "firma_archivo": "firma_santiago.jpeg"
    },
    "cliente_automatico": {
      "patron": "seguros de vida alfa",
      "rol": "demandado"
    }
  }
  JSON
  ```
- Crea el CSV vacío:
  ```bash
  echo "email,nombre,departamento,ciudad,especialidad,notas" > "$DIEGO_DIR/directorio_juzgados.csv"
  ```

Si la carpeta SÍ existe, dile al usuario que ya estaba configurada por otro miembro del firm — no toca nada de la config compartida.

# Paso 6: Verificar que todo lee bien

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/diego_paths.py" --show
```

Reporta el JSON. Si falla, diagnostica.

# Paso 7: Registrar la tarea programada del briefing diario

Usa la herramienta `mcp__scheduled-tasks__create_scheduled_task` con:

- `taskId`: `briefing-audiencias-diego`
- `description`: `Briefing matutino diario de audiencias para DIEGO. Cruza calendario de Outlook con índice de casos del firm.`
- `cronExpression`: `5 8 * * *`
- `prompt`: el contenido del archivo `${CLAUDE_PLUGIN_ROOT}/scheduled-task-template/briefing-prompt.md` (léelo primero con Read y pásalo como prompt).

Antes de crear, verifica si ya existe con `mcp__scheduled-tasks__list_scheduled_tasks`. Si ya existe (porque el usuario ya corrió setup antes), no la dupliques — solo confirma que está habilitada.

# Paso 8: Confirmar al usuario

Mensaje final:

> ✅ DIEGO configurado en esta máquina.
> - OneDrive del firm: $FIRM_PATH
> - Carpeta compartida: $DIEGO_DIR
> - Briefing diario programado: 8:13 AM
>
> Para pedir una sustitución, escribe en Claude Code: "Diego, prepara una sustitución de poder para …"
> Para ver el briefing del día: "Diego, muéstrame el briefing".

# Reglas

- No pidas datos al usuario que ya estén en la config compartida del firm.
- Si cualquier paso falla, repórtalo claramente y no continúes con los siguientes.
- Responde siempre en español.
