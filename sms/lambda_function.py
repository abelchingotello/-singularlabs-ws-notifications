import os
import json
import requests
import base64
#from aws_lambda_powertools import Logger
from datetime import datetime
import pytz

#logger = Logger()

USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
credentials = f"{USERNAME}:{PASSWORD}"
encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
headers = {
    "Authorization": f"Basic {encoded_credentials}",
    "Content-Type": "application/json",
}

URL = os.getenv("URL")

tz = pytz.timezone("America/Lima")
date_utc = datetime.now(tz)
format_date = date_utc.strftime("%Y-%m-%d %H:%M:%S")

def generate_response(status_code, status, details, total_processed, total_success=0, successful_numbers=[], total_failed=0, failed_numbers=[]):
    response = {
        "statusCode": status_code,
        "status": status,
        "details": details,
        "cantidadProcesados": total_processed,
        "cantidadExitosos": total_success,
        "numerosExitosos": successful_numbers,
        "fechayhora": format_date,
    }
    if total_failed > 0:
        response["cantidadFallidos"] = total_failed
        response["numerosFallidos"] = failed_numbers
    return response

def send_message(_data):
    try:
        plantilla = _data.get("plantilla")
        texto_mensaje = plantilla.get("texto")
        data_numbers = plantilla.get("numbers",[])

        if plantilla and texto_mensaje and data_numbers:
            addresseeList = []

            for data in data_numbers:
                number = data.get("number","")
                mensaje_final = texto_mensaje.format(**data)
                addresseeList.append({"mobile": number, "message": mensaje_final})

            payload = {
                "country": "51",
                "message": "empresa_",
                "encoding": "UTF-8",
                "messageFormat": 1,
                "addresseeList": addresseeList,
            }

            response = requests.post(URL, headers=headers, data=json.dumps(payload))
            
            if response.status_code == 200:
                data = response.json()
                cont_success = len(data["result"]["receivedRequests"])
                cont_failed = len(data["result"]["failedRequests"])

                numbers_successful = [req["mobile"] for req in data["result"]["receivedRequests"]]
                numbers_failed = [req["mobile"] for req in data["result"]["failedRequests"]]

                if cont_success > 0 and cont_failed == 0:
                    return generate_response(200, "success", "Todos los mensajes se enviaron correctamente.", len(data_numbers), cont_success, numbers_successful)
                elif cont_success > 0 and cont_failed > 0:
                    return generate_response(207, "partial", "Algunos mensajes se enviaron correctamente, pero otros fallaron.", len(data_numbers), cont_success, numbers_successful, cont_failed, numbers_failed)
                else:
                    return generate_response(400, "failure", "Solicitud inválida. Por favor, verifique los parámetros de entrada.", 0)

            else:
                return {
                        "statusCode": 400,
                        "status": response.status,
                        "details": response.reason,
                        "fechayhora": f"{format_date}",
                    }
        else:
            return {
                "statusCode": 400,
                "status": "failure",
                "error": "Solicitud inválida. Falta(n) parámetro(s) de entrada",
                "fechayhora": format_date,
            }
            
    except Exception as e:
        return {
            "statusCode": 500,
            "status": "failure",
            "error": f"Error al enviar el mensajeexe: {str(e)}",
            "fechayhora": format_date,
        }

# EntryPoint
#@logger.inject_lambda_context
def lambda_handler(event, context):
# logger.set_correlation_id(context.aws_request_id)
    estado = 200
    respuesta = ""
    try:
        body = json.loads(event.get("body"))

        if body:
            respuesta = send_message(body)
            estado = respuesta["statusCode"]
        else:
            estado = 400
            respuesta = {
                "status": "failure",
                "cantidadProcesados": 0,
                "detalles": [
                    {
                        "codigo": "CuerpoSolicitudVacio",
                        "mensaje": "El cuerpo de la solicitud no puede estar vacío.",
                    }
                ],
            }
    except Exception as e:
    #  logger.exception(f"error: Error al enviar el mensajeex: {str(e)}")
        estado = 500
        respuesta = {
            "status": "failure",
            "error": f"Error al enviar el mensajee: {str(e)}",
        }
    finally:
        return {
            "statusCode": estado,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            },
            "body": json.dumps(respuesta)
    }
