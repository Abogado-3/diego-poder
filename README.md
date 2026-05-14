# DIEGO — Plugin de sustituciones de poder

Asistente para abogados del firm CAVV que:
- Prepara escritos de **sustitución de poder** en PDF.
- Deja el **borrador listo en Outlook** (Mac o Windows) con destinatario, asunto, cuerpo y PDF adjunto. **Nunca envía el correo automáticamente.**
- Genera un **briefing diario de audiencias** cruzando el calendario de Outlook con el índice maestro de casos del firm.

---

## Instalación (15 minutos por máquina)

### Requisitos

- Una computadora **Mac o Windows**.
- **Microsoft Outlook** instalado y configurado con tu cuenta.
- **OneDrive del firm** sincronizado localmente (la biblioteca compartida de CAVV).
- **Claude Code** instalado (https://claude.com/code).

### Paso 1 — Instalar Python

**Mac:** ya viene preinstalado. Verifica abriendo Terminal y escribiendo `python3 --version`. Debe decir 3.9 o superior.

**Windows:**
1. Ve a https://www.python.org/downloads/windows/.
2. Descarga el instalador "Windows installer (64-bit)" de la versión más reciente.
3. Ejecútalo y **marca la casilla "Add Python to PATH"** antes de hacer click en Install.
4. Verifica abriendo PowerShell y escribiendo `python --version`.

### Paso 2 — Instalar las librerías que usa DIEGO

Abre tu terminal (Terminal en Mac, PowerShell en Windows) y corre:

```
python3 -m pip install reportlab openpyxl
```

(En Windows quizá tengas que escribir `python` en lugar de `python3`.)

### Paso 3 — Agregar el marketplace del firm a Claude Code

Abre Claude Code y escribe:

```
/plugin marketplace add Abogado-3/diego-poder
```

### Paso 4 — Instalar el plugin DIEGO

```
/plugin install diego-poder
```

### Paso 5 — Configurar DIEGO en esta máquina

```
/diego-setup
```

DIEGO te va a hacer preguntas (te toma 2 minutos):
- Verifica que el OneDrive del firm esté sincronizado.
- Detecta automáticamente la ruta. Si no la encuentra, te la pide.
- Si eres el primer usuario del firm que instala, te ayuda a crear la carpeta compartida `0. DIEGO - Sustitución de Poder/` con las firmas y la config inicial.
- Registra la tarea programada del briefing diario (8:13 AM).

### Paso 6 — Conectar Outlook (si no lo has hecho)

En Claude Code, abre la configuración de conectores y conecta **Microsoft Outlook**. Te abrirá el navegador para autorizar acceso. Hazlo una vez por máquina.

---

## Cómo usar a DIEGO

### Pedir una sustitución de poder

En Claude Code escribe:

```
Diego, prepara una sustitución de poder
```

O directamente con datos:

```
Diego, sustitución para el Juzgado 25 Civil del Circuito de Bogotá,
proceso Verbal de Responsabilidad Civil, demandante Juan Pérez,
demandado Seguros de Vida Alfa S.A., radicado 11001310302520240012300,
cliente Seguros de Vida Alfa, audiencia 29 de mayo de 2026.
```

DIEGO va a:
1. Generar el PDF.
2. Buscar el correo del juzgado (en directorio compartido → en tu Outlook → te pregunta si no encuentra).
3. Mostrarte un resumen del correo a enviar.
4. **Esperar tu confirmación** antes de tocar Outlook.
5. Dejar el borrador listo en Outlook. **Tú lo revisas y le das Enviar.**

### Ver el briefing del día

```
Diego, muéstrame el briefing
```

Te muestra tabla con todas las audiencias programadas hoy, con qué caso del firm coincide cada una y si tenemos el correo del juzgado en el directorio.

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

Cuando un colega agrega un nuevo correo de juzgado, los demás se benefician automáticamente.

---

## Problemas comunes

**"No encontré la config local en ..."**
Corre `/diego-setup` en esa máquina. Es la primera vez que la usas.

**"reportlab no está instalado"**
Falta el paso 2. Vuelve y corre `python3 -m pip install reportlab openpyxl`.

**"No encontré la firma del sustituyente en ..."**
Verifica que el OneDrive del firm esté sincronizado en tu máquina y que la carpeta `0. DIEGO - Sustitución de Poder/` exista con las firmas.

**El PDF se ve con fuente fea (Helvetica en lugar de Century Gothic)**
- En Mac: instala Outlook (la fuente viene en el bundle).
- En Windows: la fuente Century Gothic suele venir con Office. Verifica que esté en `C:\Windows\Fonts\GOTHIC.TTF`.

**El borrador no se crea en Outlook (Mac)**
Outlook tiene que estar abierto. Si el AppleScript falla, asegúrate de que estás usando la versión clásica de Outlook for Mac (no la nueva en algunos sistemas).

**El borrador no se crea en Outlook (Windows)**
Outlook tiene que estar instalado y debe haber al menos una cuenta configurada. PowerShell debe poder ejecutar scripts: si te da error de ExecutionPolicy, corre como administrador `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`.

---

## Licencia

MIT. Ver `LICENSE`.
