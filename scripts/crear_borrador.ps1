# Crea un borrador en Outlook for Windows con un PDF adjunto.
# Uso:
#   .\crear_borrador.ps1 -Recipient "x@y.com" -Subject "..." -Body "..." -Attachment "C:\ruta\al.pdf" [-BodyIsHtml]

param(
    [Parameter(Mandatory=$false)][string]$Recipient = "",
    [Parameter(Mandatory=$true)][string]$Subject,
    [Parameter(Mandatory=$true)][string]$Body,
    [Parameter(Mandatory=$true)][string]$Attachment,
    [Parameter(Mandatory=$false)][switch]$BodyIsHtml
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path -LiteralPath $Attachment)) {
    Write-Error "ERROR: el adjunto no existe en $Attachment"
    exit 1
}

try {
    $outlook = New-Object -ComObject Outlook.Application
} catch {
    Write-Error "ERROR: no pude conectar con Microsoft Outlook. ¿Está instalado?"
    exit 2
}

# 0 = olMailItem
$mail = $outlook.CreateItem(0)
$mail.Subject = $Subject

if ($BodyIsHtml) {
    $mail.HTMLBody = $Body
} else {
    $mail.Body = $Body
}

if ($Recipient -ne "") {
    $mail.To = $Recipient
}

$absPath = (Resolve-Path -LiteralPath $Attachment).Path
$mail.Attachments.Add($absPath) | Out-Null

$mail.Display() | Out-Null

$bodyKind = if ($BodyIsHtml) { "html" } else { "plain" }
Write-Output "OK: borrador creado en Outlook (Windows, $bodyKind)"
exit 0
