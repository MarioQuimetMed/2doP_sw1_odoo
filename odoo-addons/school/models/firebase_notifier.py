import os
import json
import requests
import firebase_admin
from firebase_admin import credentials
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from odoo import models, fields, api
from odoo.exceptions import UserError

class FirebaseNotifier(models.Model):
    _name = 'school.firebase_notifier'
    _description = 'Notificador de Firebase'

    title = fields.Char(string="Título", required=True)
    body = fields.Text(string="Mensaje", required=True)
    token = fields.Char(string="Token de Dispositivo", required=True)

    def _get_access_token(self):
        """
        Obtiene el token de acceso de Firebase usando las credenciales JSON.
        """
        # Obtener la ruta absoluta del módulo y del archivo JSON
        module_path = os.path.dirname(os.path.abspath(__file__))
        cred_path = os.path.join(module_path, "../data/firebase_api.json")

        # Verificar que el archivo de credenciales existe
        if not os.path.exists(cred_path):
            raise UserError(f"Archivo de credenciales no encontrado: {cred_path}")

        # Cargar las credenciales de Firebase
        creds = service_account.Credentials.from_service_account_file(
            cred_path,
            scopes=["https://www.googleapis.com/auth/firebase.messaging"]
        )

        # Refrescar el token para obtener uno válido
        creds.refresh(Request())

        return creds.token

    def send_notification(self):
        """
        Envía una notificación push a Firebase Cloud Messaging usando HTTP v1 con autenticación válida.
        """
        access_token = self._get_access_token()

        url = "https://fcm.googleapis.com/v1/projects/app-agenda-24964/messages:send"

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        data = {
            "message": {
                "token": self.token,
                "notification": {
                    "title": self.title,
                    "body": self.body
                }
            }
        }

        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            return {
                "status": "success",
                "message": "Notificación enviada exitosamente."
            }
        else:
            raise UserError(f"Error al enviar notificación: {response.text}")
