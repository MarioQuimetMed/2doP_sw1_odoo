# -*- coding: utf-8 -*-
{
    'name': "school",

    'summary': "Modulo enfocado para la Gestion de Una Agenda Electronica",

    'description': """
Funcionalidades muchas xd
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/rol_data.xml',
        'data/paralelo_data.xml',
        'data/grado_data.xml',
        'data/sequence.xml',
        'data/materia_data.xml',
        'data/users_data.xml',
        'views/views.xml',
        'views/templates.xml',
        # -----------------------------------
        'views/Academico/grado_views.xml',
        'views/Academico/paralelo_views.xml',
        'views/Academico/rol_views.xml',
        'views/Academico/materia_views.xml',
        'views/Academico/curso_views.xml',
        'views/Academico/horario_views.xml',
        # -----------------------------------
        'views/Usuarios/usuarios_views.xml',
        'views/Usuarios/administrador_views.xml',
        'views/Usuarios/tutor_views.xml',
        'views/Usuarios/alumno_views.xml',
        'views/Usuarios/docente_views.xml',
        # -----------------------------------
        'views/Comunicados/usuario_search_views.xml',
        'views/Comunicados/Comunicado_views.xml',
        # -----------------------------------
        'views/school_menu.xml',
        
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

