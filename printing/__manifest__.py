# -*- coding: utf-8 -*-
{
    'name': 'PRINTING',
    'version': '15.0',
    'summary': 'printing',
    'category': 'difmiadi',
    'description': u"""
This module configures your printing.
""",
    'author': 'Difference informatique - MIADI',
    'depends': [
        'base', 'base_setup', 'sale', 'sales_team'
        
    ],
    'data': [
        "wizard/wiz_print_etiquette.xml",
        "views/etiq_model_views.xml",
        "views/printer_views.xml",
        "views/parameter_views.xml",
        "views/printing_views.xml",
        "printing_menu.xml",
       
        "security/ir.model.access.csv",
        
    ],
    'demo': [
        'data/printing_data.xml'
             ],
    'application': False,
    'license': 'OPL-1',
   
  
}
