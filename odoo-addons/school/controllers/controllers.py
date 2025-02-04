from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

class FcmTokenController(http.Controller):
    @http.route('/api/guardar_fcm_token', type='json', auth='public', methods=['POST'], csrf=False)
    def guardar_fcm_token(self, **kwargs):
        _logger.info(f"Parámetros recibidos: {kwargs}")  # Imprime los parámetros recibidos
        
        user_id = kwargs.get('user_id')
        fcm_token = kwargs.get('fcm_token')
        
        if not user_id or not fcm_token:
            _logger.warning("Faltan parámetros: user_id o fcm_token")
            return {'status': 'error', 'message': 'Parámetros incompletos'}
        
        usuario = request.env['school.usuario'].sudo().search([('id', '=', user_id)], limit=1)
        
        if usuario:
            usuario.write({'fcm_token': fcm_token})
            return {'status': 'success', 'message': 'Token FCM guardado'}
        else:
            _logger.warning(f"Usuario no encontrado con ID {user_id}")
            return {'status': 'error', 'message': 'Usuario no encontrado'}