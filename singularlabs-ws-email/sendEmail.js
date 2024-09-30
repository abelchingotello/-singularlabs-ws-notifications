const nodemailer = require("nodemailer");

const sendEmail = async (host, port, user, password, to, subject, text, html, attachments) => {

    const config = {
        host: host,
        port: port,
        //secure: true, // Cambia esto si tu servicio de correo requiere SSL/TLS
        auth: {
            user: user,
            pass: password,
        },
        tls: {
            // do not fail on invalid certs
            rejectUnauthorized: false,
        },
    };

    const mensaje = {
        from: user,
        to,
        subject,
        text,
        html,
        attachments,
    };

    try {
        const transport = nodemailer.createTransport(config);
        const info = await transport.sendMail(mensaje);
        return {
            success: true,
            info,
        };
    } catch (error) {
        console.error("Error al enviar correo: ", error);
        return {
            success: false,
            error: error.message || "Error no especificado",
        };
    }
};

module.exports = {
    sendEmail,
};
