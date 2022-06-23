# -*- coding: utf-8 -*-
{
    'name': "maintenance_follow_up",

    'summary': """
        maintenance_follow_up""",

    'description': """      
      Follow_up request maintenance
    """,

    'author': "Difference informatique - MIADI",
    'website': "http://www.pole-erp-pgi.fr",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': '',
    'version': '14',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail'],

    # always loaded
    'data': [
        'security/di_maintenance.xml',
        'security/ir.model.access.csv',
        'data/di_maintenance_data.xml',
        'data/di_mail_data.xml',
        'views/di_maintenance_views.xml',
        'views/di_mail_activity_views.xml',
        'data/di_maintenance_cron.xml',
    ],
    'demo': [
        'data/di_maintenance_demo.xml'
             ],
    'installable': True,
    'application': True,
    'assets': {
        'web.assets_backend': [
            'maintenance_followup/static/src/**/*',
        ],
    },
               
               
}