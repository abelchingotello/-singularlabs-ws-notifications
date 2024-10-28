const { sendEmail } = require("./sendEmail");

exports.handler = async (event) => {
    const headers = event.headers || {};

    // Extraer host, puerto, usuario y contraseña del header
    const host = Buffer.from(headers['HostEmail'], 'base64').toString('utf-8');
    const port = Buffer.from(headers['Port'], 'base64').toString('utf-8');
    const user = Buffer.from(headers['User'], 'base64').toString('utf-8');
    const password = Buffer.from(headers['Password'], 'base64').toString('utf-8');

    
    const { to, subject, text, html, attachments } = JSON.parse(event.body);

    // Llamar a la función sendEmail del módulo emailService
    const result = await sendEmail(host, port, user, password, to, subject, text, html, attachments);

    if (result.success) {
        return {
            statusCode: 200,
            body: JSON.stringify({
                message: "Correo enviado correctamente",
                body: result.info,
            }),
            headers: {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": true,
            },
        };
    } else {
        return {
            statusCode: 500,
            body: JSON.stringify({
                message: "Error al enviar el correo",
                body: result.error,
            }),
            headers: {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": true,
            },
        };
    }
};
