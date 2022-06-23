# -*- coding: utf-8 -*-
{
    'name': "marinove_dev",

    'summary': """
        marinove""",

    'description': """
      Develop Marinove
    """,

    'author': "Miadi - Difference informatique",
    'website': "http://www.pole-erp-pgi.fr",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': '',
    'version': '14',

    # any module necessary for this one to work correctly
      'depends': [   
        'base',
        'base_setup',  'popup' ,
        'crm', 'sale' , 'delivery',                                                
        'stock', 'printing',
        ],

    # always loaded
    'data': [  
        ##'security/ir.model.access.csv',    
        'views/inh_product_template_views.xml', 
        'views/inh_delivery_carrier_views.xml',      
        'views/di_crm_lead.xml', 
        'views/inh_res_partner_views.xml',
        'views/inh_crm_lead_views.xml',
        'views/inh_sale_order_views.xml',
        'views/inh_account_move_views.xml',
        'views/inh_stock_picking_views.xml',
        'views/inh_historique_sage_views.xml',
        'views/inh_account_payment_views.xml',
        'reports/report_templates_bontransport.xml',
        'reports/inh_account_invoice_report.xml',
        
        #'reports/inh_sale_report_templates.xml',
        'reports/marinove_reports.xml',
        'reports/inh_account_analyse.xml',
        'reports/inh_sale_analyse.xml',
        'wizards/wiz_dialog_views.xml',
        'wizards/crm_opportunities_order_views.xml',   
                                                                  
        'security/ir.model.access.csv',          
        # 'data/data.xml', 
        'views/di_crm_lead.xml',  
        'views/di_production_vente.xml', 
        'views/di_packaging_views.xml',
        'views/di_stock_warehouse.xml', 
        'views/di_current_stock_views.xml',
        'views/inh_stock_location.xml',
        'views/inh_product_category.xml',
        'views/inh_account_fiscal_position.xml',
        'views/inh_res_country.xml',
        'wizards/di_cerfa_wiz.xml', 
        'reports/planning_production_report_views.xml',
        'wizards/wiz_stock_picking_print_etiq.xml',
        
    ],
    # only loaded in demonstration mode
    'demo': [
       
    ],
    'installable': True,   
    'license': 'OPL-1', 
}