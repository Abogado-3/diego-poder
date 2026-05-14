-- Crea un borrador en Outlook for Mac con un PDF adjunto.
-- Uso: osascript crear_borrador.applescript "destinatario@juzgado.com" "Asunto" "Cuerpo" "/ruta/al/adjunto.pdf"
-- Si el destinatario va vacío (""), el borrador se crea sin destinatario.

on run argv
    if (count of argv) < 4 then
        return "ERROR: faltan argumentos. Uso: destinatario asunto cuerpo ruta_adjunto"
    end if

    set recipientEmail to item 1 of argv
    set emailSubject to item 2 of argv
    set emailBody to item 3 of argv
    set attachmentPath to item 4 of argv

    tell application "System Events"
        if not (exists file attachmentPath) then
            return "ERROR: el adjunto no existe en " & attachmentPath
        end if
    end tell

    set posixAttachment to POSIX file attachmentPath

    tell application "Microsoft Outlook"
        activate
        set newMsg to make new outgoing message with properties {subject:emailSubject, plain text content:emailBody}
        if recipientEmail is not "" then
            make new recipient at newMsg with properties {email address:{address:recipientEmail}}
        end if
        make new attachment at newMsg with properties {file:posixAttachment}
        open newMsg
    end tell

    return "OK: borrador creado en Outlook (Mac)"
end run
