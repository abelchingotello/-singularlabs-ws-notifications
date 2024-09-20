const nodemailer = require("nodemailer");

exports.handler = async (event) => {
    
    const { to, subject, text, user, password, host, port } = event;
    
    const config = {
        host: host,
        port: port,
        auth: {
            user: user,
            pass: password,
        },
    };

    const mensaje = {
        from: user,
        to,
        subject,
        text,
    };

    try {
        const transport = nodemailer.createTransport(config);
        const info = await transport.sendMail(mensaje);
        
        return {
            statusCode: 200,
            message: "Correo enviado correctamente",
            body:  info ,
        };

    }
    catch (error) {
        console.error("Error al enviar correo: ", error);
        
        return {
            statusCode: 500,
            message: "Error al enviar el correo",
            body:  error ,
        };
    }
};

