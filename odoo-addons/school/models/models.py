# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError

# Modelo: Usuario (Hereda de res.users)
class Usuario(models.Model):
    _name = 'school.usuario'
    _description = 'Usuarios del Sistema'
    _inherits = {'res.users': 'user_id'}

    ci = fields.Char(
        string="CI",
        required=False,
        help="Cédula de Identidad del usuario",
        unique=True
    )
    correo = fields.Char(
        string="Correo",
        required=True,
        help="Correo electrónico del usuario"
    )
    password = fields.Char(
        string="Contraseña",
        required=True,
        help="Contraseña del usuario"
    )
    
    apellido_paterno = fields.Char(string="Apellido Paterno", required=True)
    apellido_materno = fields.Char(string="Apellido Materno", required=True)
    nombre = fields.Char(string="Nombre", required=True)

    # Aquí la magia: en lugar de un compute propio, utilizamos un related
    # a 'curso_actual_id' de 'school.alumno'
    curso_id = fields.Many2one(
        'school.curso',
        string="Curso",
        related="alumno_id.curso_actual_id",
        store=True
    )

    # Esta relación inversa hará que, si existe un alumno con el mismo 'id',
    # se muestre en 'alumno_id'. Normalmente, con _inherits, comparten ID.
    alumno_id = fields.One2many(
        'school.alumno',
        'id',  # el campo 'id' de school.alumno es el mismo ID que este record
        string="Registro de Alumno"
    )

    tipo_usuario = fields.Selection([
        ('docente', 'Docente'),
        ('tutor', 'Tutor'),
        ('alumno', 'Alumno'),
        ('admin', 'Administrador')
    ], string="Tipo de Usuario", compute="_compute_tipo_usuario", store=True)

    @api.depends('user_id')
    def _compute_tipo_usuario(self):
        """
        Detecta si este 'school.usuario' es un alumno, docente, tutor o admin
        buscando en sus respectivos modelos que también heredan de 'school.usuario'.
        """
        for user in self:
            if self.env['school.docente'].search([('user_id', '=', user.id)], limit=1):
                user.tipo_usuario = 'docente'
            elif self.env['school.tutor'].search([('user_id', '=', user.id)], limit=1):
                user.tipo_usuario = 'tutor'
            elif self.env['school.alumno'].search([('user_id', '=', user.id)], limit=1):
                user.tipo_usuario = 'alumno'
            elif self.env['school.administrador'].search([('user_id', '=', user.id)], limit=1):
                user.tipo_usuario = 'admin'
            else:
                user.tipo_usuario = False

    @api.constrains('ci')
    def _check_unique_ci(self):
        """Valida que el campo CI sea único en 'school.usuario'."""
        for user in self:
            if self.search([('ci', '=', user.ci), ('id', '!=', user.id)]):
                raise ValidationError("La cédula de identidad debe ser única.")
            
    @api.model_create_multi
    def create(self, vals_list):
        """
        Sobrescribe el create para:
        - Asignar CI si no viene.
        - Generar contraseña si no viene.
        - Crear el res.users subyacente.
        - (Opcionalmente) crear la tabla hija si corresponde, aunque
          lo usual es crear directamente en 'school.alumno', etc.
        """
        for vals in vals_list:
            # Generar CI predeterminado si no se proporciona
            if not vals.get('ci'):
                vals['ci'] = self.env['ir.sequence'].next_by_code('school.usuario.ci') or '00000'

            # Generar contraseña basada en el CI o en el apellido paterno
            if not vals.get('password'):
                if vals.get('ci'):
                    vals['password'] = vals['ci']
                else:
                    vals['password'] = vals.get('apellido_paterno', 'password').lower()

            password_plano = vals.get('password')  # en texto, no hasheado

            user_vals = {
                'name': vals['correo'],
                'login': vals['correo'],
                'password': password_plano,
            }

            # Asignar grupo de admin si corresponde
            if vals.get('tipo_usuario') == 'admin':
                admin_group = self.env.ref('base.group_system')
                user_vals['groups_id'] = [(4, admin_group.id)]

            # Crea el res.users
            res_user = self.env['res.users'].create(user_vals)
            # Relaciona con school.usuario (este modelo) a través de 'user_id'
            vals['user_id'] = res_user.id

        return super(Usuario, self).create(vals_list)

    def name_get(self):
        """
        Para mostrar el nombre completo en lugar del 'name' de res.users
        """
        result = []
        for record in self:
            name = f"{record.nombre} {record.apellido_paterno} {record.apellido_materno}"
            result.append((record.id, name))
        return result


# Modelo: Alumno (Hereda de Usuario)
class Alumno(models.Model):
    _name = 'school.alumno'
    _inherits = {'school.usuario': 'user_id'}
    _description = 'Alumno'

    boleta_ids = fields.One2many('school.boleta', 'id_alumno', string="Boletas")

    # Campo que obtiene el curso "vigente" en base a sus boletas
    curso_actual_id = fields.Many2one(
        'school.curso',
        string="Curso Actual",
        compute="_compute_curso_actual",
        store=True
    )

    @api.depends('boleta_ids', 'boleta_ids.periodo', 'boleta_ids.id_curso')
    def _compute_curso_actual(self):
        """
        Busca la boleta de mayor periodo (o última creada, según order)
        y asigna el curso de esa boleta. Si no hay boletas, queda vacío.
        """
        for alumno in self:
            boleta = self.env['school.boleta'].search(
                [('id_alumno', '=', alumno.id)], 
                order='periodo desc', 
                limit=1
            )
            alumno.curso_actual_id = boleta.id_curso if boleta else False


# Modelo: Tutor (Hereda de Usuario)
class Tutor(models.Model):
    _name = 'school.tutor'
    _inherits = {'school.usuario': 'user_id'}
    _description = 'Tutor'

    tutoria_ids = fields.One2many('school.tutoria', 'id_tutor', string="Tutorías")


# Modelo: Docente (Hereda de Usuario)
class Docente(models.Model):
    _name = 'school.docente'
    _inherits = {'school.usuario': 'user_id'}
    _description = 'Docente'

    horario_ids = fields.One2many('school.horario_dia', 'id_usuario_docente', string="Horarios")


# Modelo: Administrador (Hereda de Usuario)
class Administrador(models.Model):
    _name = 'school.administrador'
    _inherits = {'school.usuario': 'user_id'}
    _description = 'Administrador'


# Modelo: Comunicado
class Comunicado(models.Model):
    _name = 'school.comunicado'
    _description = 'Comunicados Académicos'

    title = fields.Char(string="Título", required=True)
    description = fields.Text(string="Descripción")
    emite_id = fields.Many2one('school.usuario', string="Emitido Por", required=True, 
                               default=lambda self: self.env.user)
    destinatarios_ids = fields.Many2many('school.usuario', string="Destinatarios")

    def enviar_comunicado(self):
        if not self.destinatarios_ids:
            raise ValidationError("Debe seleccionar al menos un destinatario antes de enviar el comunicado.")
        
        for destinatario in self.destinatarios_ids:
            self.env['school.agenda'].create({
                'id_comunicado': self.id,
                'id_usuario': destinatario.id,
                'leido': False,
            })


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

    id_tutor = fields.Many2one('school.tutor', string="Tutor", required=True)
    id_alumno = fields.Many2one('school.alumno', string="Estudiante", required=True)


# Modelo: Boleta
class Boleta(models.Model):
    _name = 'school.boleta'
    _description = 'Boletas de Calificaciones'

    id_alumno = fields.Many2one('school.alumno', string="Alumno", required=True)
    id_curso = fields.Many2one('school.curso', string="Curso", required=True)
    periodo = fields.Integer(string="Período Académico", required=True)


# Modelo: Materia
class Materia(models.Model):
    _name = 'school.materia'
    _description = 'Materias Académicas'

    name = fields.Char(string="Nombre de la Materia", required=True)


# Modelo: Grado
class Grado(models.Model):
    _name = 'school.grado'
    _description = 'Grados Académicos'

    name = fields.Char(string="Nombre del Grado", required=True)


# Modelo: Paralelo
class Paralelo(models.Model):
    _name = 'school.paralelo'
    _description = 'Paralelos'

    name = fields.Char(string="Letra del Paralelo", required=True)

    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, record.name))
        return result
    

# Modelo: Curso
class Curso(models.Model):
    _name = 'school.curso'
    _description = 'Cursos Académicos'

    id_grado = fields.Many2one('school.grado', string="Grado", required=True)
    id_paralelo = fields.Many2one('school.paralelo', string="Paralelo", required=True)
    name = fields.Char(string="Nombre del Curso", compute="_compute_name", store=True)

    @api.depends('id_grado', 'id_paralelo')
    def _compute_name(self):
        for record in self:
            grado_name = record.id_grado.name if record.id_grado else ''
            paralelo_name = record.id_paralelo.name if record.id_paralelo else ''
            record.name = f"{grado_name} - {paralelo_name}".strip()


# Modelo: HorarioDia
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
    id_usuario_docente = fields.Many2one('school.docente', string="Docente", required=True)

    @api.constrains('dia', 'hora_inicio', 'hora_fin', 'id_usuario_docente')
    def _check_horario_solapado(self):
        for record in self:
            solapados = self.search([
                ('id', '!=', record.id),
                ('dia', '=', record.dia),
                ('id_usuario_docente', '=', record.id_usuario_docente.id),
                ('hora_inicio', '<', record.hora_fin),
                ('hora_fin', '>', record.hora_inicio)
            ])
            if solapados:
                raise ValidationError(
                    "El docente ya tiene un horario asignado que se solapa con este horario."
                )


# Modelo: Asistencia
class Asistencia(models.Model):
    _name = 'school.asistencia'
    _description = 'Registro de Asistencia'

    estado = fields.Selection([
        ('presente', 'Presente'),
        ('ausente', 'Ausente')
    ], string="Estado", required=True)
    fecha = fields.Date(string="Fecha", required=True)
    id_alumno = fields.Many2one('school.alumno', string="Alumno", required=True)
    id_horario_dia = fields.Many2one('school.horario_dia', string="Horario", required=True)
