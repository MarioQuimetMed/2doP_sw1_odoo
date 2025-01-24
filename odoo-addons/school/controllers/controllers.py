# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.exceptions import ValidationError
import passlib.context
import logging
import json

_logger = logging.getLogger(__name__)

class School(http.Controller):
    @http.route('/school/login', type='json', auth='public', methods=['POST'])
    def login(self):
        """
        Controlador de autenticación para el modelo school.usuario.
        """
        data = json.loads(request.httprequest.data)
        _logger.info('Datos recibidos: %s', data)

        # Verificar si los datos necesarios están presentes
        correo = data.get('correo')
        password = data.get('password')

        _logger.info('Correo: %s, Password: %s', correo, password)

        if not correo or not password:
            return {'error': 'Correo y contraseña son requeridos'}

        # Buscar el usuario por correo
        user = request.env['school.usuario'].sudo().search([('correo', '=', correo)], limit=1)
        if not user:
            return {'error': 'Usuario no encontrado'}

        # Verificar la contraseña
        crypt_context = passlib.context.CryptContext(schemes=['pbkdf2_sha512', 'md5_crypt'], deprecated=['md5_crypt'])
        if not crypt_context.verify(password, user.password):
            return {'error': 'Contraseña incorrecta'}

        # Autenticación exitosa
        return {
            'success': 'Login exitoso',
            'user_id': user.id,
            'correo': user.correo,
            'rol': user.id_rol.descripcion if user.id_rol else None
        }