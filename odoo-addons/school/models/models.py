# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError
import passlib.context

# Modelo: Rol
class Rol(models.Model):
    _name = 'school.rol'
    _description = 'Roles de Usuario'
    _rec_name = 'descripcion'  # Este campo sderá mostrado en lugar del ID

    descripcion = fields.Char(string="Descripción", required=True)


class Usuario(models.Model):
    _name = 'school.usuario'
    _description = 'Usuarios del Sistema'

    id_rol = fields.Many2one('school.rol', string="Rol", required=False, help='Rol asignado al usuario')
    correo = fields.Char(string="Correo", required=True, help='Correo electrónico del usuario')
    ci = fields.Char(string="CI", required=True, help="Cédula de Identidad del usuario")
    password = fields.Char(string="Contraseña", required=True, help='Contraseña del usuario')

    tutoria_ids = fields.One2many(
        comodel_name='school.tutoria',
        inverse_name='id_usuario_tutor',
        string='Estudiantes Asignados'
    )

    # @api.model
    # def default_get(self, fields_list):
    #     # Establecer un valor predeterminado para `id_rol` según el contexto
    #     res = super(Usuario, self).default_get(fields_list)
    #     if self.env.context.get('default_rol_tutor'):
    #         res['id_rol'] = self.env.ref('school.rol_tutor').id
    #     elif self.env.context.get('default_rol_estudiante'):
    #         res['id_rol'] = self.env.ref('school.rol_alumno').id
    #     return res

    @api.constrains('ci')
    def _check_unique_ci(self):
        for user in self:
            if self.search([('ci', '=', user.ci), ('id', '!=', user.id)]):
                raise ValidationError("La cédula de identidad debe ser única.")

    @api.model
    def create(self, vals):
        if 'password' not in vals and 'ci' in vals:
            vals['password'] = vals['ci']
        if 'password' in vals:
            vals['password'] = self._hash_password(vals['password'])
        return super(Usuario, self).create(vals)

    def _hash_password(self, password):
        # Método para encriptar la contraseña
        return self.env['school.usuario']._crypt_context().encrypt(password)

    def _crypt_context(self):
        return passlib.context.CryptContext(schemes=['pbkdf2_sha512', 'md5_crypt'], deprecated=['md5_crypt'])    
    

# Modelo: Comunicado
class Comunicado(models.Model):
    _name = 'school.comunicado'
    _description = 'Comunicados Académicos'

    title = fields.Char(string="Título", required=True)
    description = fields.Text(string="Descripción")
    emite = fields.Many2one('school.usuario', string="Emitido Por", required=True)

# Modelo: Agenda
class Agenda(models.Model):
    _name = 'school.agenda'
    _description = 'Agenda Académica'

    id_comunicado = fields.Many2one('school.comunicado', string="Comunicado", required=True)
    id_usuario = fields.Many2one('school.usuario', string="Usuario", required=True)
    leido = fields.Boolean(string="Leído")

# Modelo: Tutoria
class Tutoria(models.Model):
    _name = 'school.tutoria'
    _description = 'Tutorías'

    id_usuario_tutor = fields.Many2one('school.usuario', string="Tutor", required=True)
    id_usuario_estudiante = fields.Many2one('school.usuario', string="Estudiante", required=True)

# Modelo: Grado
class Grado(models.Model):
    _name = 'school.grado'
    _description = 'Grados Académicos'

    name = fields.Char(string="Nombre del Grado", required=True)

# Modelo: Paralelo
class Paralelo(models.Model):
    _name = 'school.paralelo'
    _description = 'Paralelos'

    letra = fields.Char(string="Letra del Paralelo", required=True)

# Modelo: Curso
class Curso(models.Model):
    _name = 'school.curso'
    _description = 'Cursos Académicos'

    id_grado = fields.Many2one('school.grado', string="Grado", required=True)
    id_paralelo = fields.Many2one('school.paralelo', string="Paralelo", required=True)

# Modelo: Materia
class Materia(models.Model):
    _name = 'school.materia'
    _description = 'Materias Académicas'

    nombre = fields.Char(string="Nombre de la Materia", required=True)

# Modelo: Horario_Dia
class HorarioDia(models.Model):
    _name = 'school.horario_dia'
    _description = 'Horarios por Día'

    dia = fields.Selection([
        ('lunes', 'Lunes'),
        ('martes', 'Martes'),
        ('miercoles', 'Miércoles'),
        ('jueves', 'Jueves'),
        ('viernes', 'Viernes')
    ], string="Día", required=True)
    hora_inicio = fields.Float(string="Hora Inicio", required=True)
    hora_fin = fields.Float(string="Hora Fin", required=True)
    id_curso = fields.Many2one('school.curso', string="Curso", required=True)
    id_materia = fields.Many2one('school.materia', string="Materia", required=True)
    id_usuario_docente = fields.Many2one('school.usuario', string="Docente", required=True)

# Modelo: Boleta
class Boleta(models.Model):
    _name = 'school.boleta'
    _description = 'Boletas de Calificaciones'

    id_alumno = fields.Many2one('school.usuario', string="Alumno", required=True)
    id_curso = fields.Many2one('school.curso', string="Curso", required=True)
    periodo = fields.Integer(string="Período Académico", required=True)

# Modelo: Asistencia
class Asistencia(models.Model):
    _name = 'school.asistencia'
    _description = 'Registro de Asistencia'

    estado = fields.Selection([
        ('presente', 'Presente'),
        ('ausente', 'Ausente')
    ], string="Estado", required=True)
    fecha = fields.Date(string="Fecha", required=True)
    id_alumno = fields.Many2one('school.usuario', string="Alumno", required=True)
    id_horario_dia = fields.Many2one('school.horario_dia', string="Horario", required=True)
