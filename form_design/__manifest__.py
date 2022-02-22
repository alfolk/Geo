# -*- coding: utf-8 -*-
{
    'name': "form_design",

    'summary': """
      free create and fill forms""",

    'description': """
    """,

    'author': "Alzahraa Gamal",
    'website': "",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['hr', 'mail', 'web_widget_x2many_2d_matrix','partner_category'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/apply.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
}
