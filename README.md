# DIEGO — Asistente de sustituciones de poder

Asistente para abogados del firm CAVV que:
- Prepara escritos de **sustitución de poder** en PDF.
- Deja el **borrador listo en Outlook** (Mac o Windows) con destinatario, asunto, cuerpo y PDF adjunto. **Nunca envía el correo automáticamente.**
- Genera un **briefing diario de audiencias** cruzando el calendario de Outlook con el índice maestro de casos del firm.
- El directorio de juzgados es **compartido** en OneDrive: cuando un colega agrega un correo nuevo, todos se benefician.

---

## Instalación (un solo comando, 5 minutos por máquina)

### Requisitos previos

- **Microsoft Outlook** instalado y configurado con tu cuenta del firm.
- **OneDrive del firm sincronizado** localmente (debes ver la carpeta `ABOGADO01 - ARCHIVO DIGITAL CAVV` en tu Finder/Explorer).
- **Claude Code** instalado.
- **Python 3.9 o superior** instalado.

#### Cómo instalar Python (si no lo tienes)

**Mac**: ya viene preinstalado en macOS reciente. Verifica abriendo Terminal y escribiendo `python3 --version`.

**Windows**: descarga el instalador de https://www.python.org/downloads/windows/, ejecútalo y **marca la casilla "Add Python to PATH"** antes de hacer click en Install.

### Instalación en Mac

Abre **Terminal** y pega este comando:

```bash
curl -fsSL https://raw.githubusercontent.com/Abogado-3/diego-poder/main/install.sh | bash
```

Te va a:
1. Instalar las librerías de Python que necesita (reportlab, openpyxl).
2. Descargar DIEGO y copiarlo a `~/.claude/`.
3. Detectar automáticamente tu OneDrive del firm (te pide confirmación).
4. Guardar la config local.

### Instalación en Windows

Abre **PowerShell** (no CMD) y pega este comando:

```powershell
iwr https://raw.githubusercontent.com/Abogado-3/diego-poder/main/install.ps1 -UseBasicParsing | iex
```

Hace los mismos pasos que el de Mac.

### Después de instalar

1. **Abre Claude Code** (cierra y abre si ya estaba abierto).
2. Escribe: `Diego, hola` — debe presentarse como DIEGO.
3. Para activar el briefing diario de audiencias, escribe: `Diego, configura mi briefing diario`.

---

## Cómo usar a DIEGO

### Pedir una sustitución de poder

En Claude Code:

```
Diego, prepara una sustitución para el Juzgado 25 Civil del Circuito de Bogotá,
proceso Verbal de Responsabilidad Civil, demandante Juan Pérez,
demandado Seguros de Vida Alfa S.A., radicado 11001310302520240012300,
cliente Seguros de Vida Alfa, audiencia 29 de mayo de 2026.
```

DIEGO va a:
1. Generar el PDF de la sustitución.
2. Buscar el correo del juzgado (en directorio compartido del firm → en tu Outlook → te pregunta si no lo encuentra).
3. Mostrarte un resumen del correo.
4. **Esperar tu confirmación** antes de tocar Outlook.
5. Dejar el borrador listo en Outlook con el PDF adjunto. **Tú lo revisas y le das Enviar.**

### Ver el briefing del día

```
Diego, muéstrame el briefing
```

Tabla con todas las audiencias programadas hoy, el caso del firm que coincide y si tenemos el correo del juzgado.

---

## Estructura compartida en OneDrive

Todo el firm comparte una carpeta en OneDrive:

```
ABOGADO01 - ARCHIVO DIGITAL CAVV/
└── 0. DIEGO - Sustitución de Poder/
    ├── config.json              ← datos de sustituyente/sustituido (firm)
    ├── firma_carlos.jpeg        ← firma del sustituyente
    ├── firma_santiago.jpeg      ← firma del sustituido
    └── directorio_juzgados.csv  ← correos de juzgados (todos enriquecen)
```

Cuando un colega agrega un nuevo correo de juzgado, OneDrive lo sincroniza al resto en segundos.

**Si eres el primer abogado del firm en instalar DIEGO**, vas a tener que crear esa carpeta manualmente la primera vez (copia las firmas y crea el `config.json` con los datos del firm). El abogado Carlos Vargas ya lo hizo, así que para los demás solo basta correr el instalador.

---

## Problemas comunes

**"No encontré la config local en ..."**
→ El instalador no completó. Vuelve a correr el comando de instalación.

**"reportlab no está instalado"**
→ El instalador falló en el paso de pip. Abre Terminal y corre `python3 -m pip install --user reportlab openpyxl`.

**"No encontré la firma del sustituyente en ..."**
→ Verifica que el OneDrive del firm esté sincronizado en tu máquina y que la carpeta `0. DIEGO - Sustitución de Poder/` exista con las firmas.

**El PDF se ve con fuente fea (Helvetica)**
→ DIEGO usa Century Gothic. En Mac la saca del bundle de Outlook; verifica que Outlook esté instalado. En Windows debe estar en `C:\Windows\Fonts\GOTHIC.TTF` (suele venir con Office).

**El borrador no se crea en Outlook (Mac)**
→ Outlook tiene que estar abierto. Asegúrate de usar la versión clásica de Outlook for Mac.

**El borrador no se crea en Outlook (Windows)**
→ Outlook debe estar instalado con al menos una cuenta configurada. Si PowerShell da error de ExecutionPolicy, corre como administrador: `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`.

---

## Actualizaciones

Para actualizar DIEGO a la última versión, vuelve a correr el comando de instalación. Sobreescribe los archivos pero respeta tu config local.

---

## Licencia

MIT. Ver `LICENSE`.
