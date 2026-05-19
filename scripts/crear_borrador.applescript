-- Crea un borrador en Outlook for Mac con un PDF adjunto.
-- Uso: osascript crear_borrador.applescript "destinatario@juzgado.com" "Asunto" "Cuerpo" "/ruta/al/adjunto.pdf" "plain|html"
-- Si el destinatario va vacío (""), el borrador se crea sin destinatario.
-- El último argumento dice si el cuerpo es "plain" (texto) o "html".

on run argv
    if (count of argv) < 4 then
        return "ERROR: faltan argumentos. Uso: destinatario asunto cuerpo ruta_adjunto [plain|html]"
    end if

    set recipientEmail to item 1 of argv
    set emailSubject to item 2 of argv
    set emailBody to item 3 of argv
    set attachmentPath to item 4 of argv

    set bodyKind to "plain"
    if (count of argv) >= 5 then
        set bodyKind to item 5 of argv
    end if

    tell application "System Events"
        if not (exists file attachmentPath) then
            return "ERROR: el adjunto no existe en " & attachmentPath
        end if
    end tell

    set posixAttachment to POSIX file attachmentPath

    tell application "Microsoft Outlook"
        activate
        if bodyKind is "html" then
            set newMsg to make new outgoing message with properties {subject:emailSubject, content:emailBody}
        else
            set newMsg to make new outgoing message with properties {subject:emailSubject, plain text content:emailBody}
        end if
        if recipientEmail is not "" then
            make new recipient at newMsg with properties {email address:{address:recipientEmail}}
        end if
        make new attachment at newMsg with properties {file:posixAttachment}
        open newMsg
    end tell

    return "OK: borrador creado en Outlook (Mac, " & bodyKind & ")"
end run
