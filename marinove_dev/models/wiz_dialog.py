# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import date, timedelta, datetime
from odoo.exceptions import ValidationError


class Wizard_dialog(models.TransientModel):
    _name = "wiz.dialog"
    _description = "Wizard for dialog"
    
    confirm_message = fields.Text(string="Information")
    code_message = fields.Text(string="Code Message")
   
        
#    @api.multi
    def wiz_create_production(self):
        sales = self.env['di.production.vente'].update_data_production()
        return sales 
    
    def wiz_liste_production(self):
        sales =self.env['di.production.vente'].search([('id','!=',False),  ]).ids
        if len(sales) == 0:
            sales = self.env['di.production.vente'].update_data_production()
            return sales
        else: 
            action = self.env.ref('marinove_dev.di_production_vente_action_production').read()[0]
            action['domain'] = [('id', 'in', sales)]   
            return action 
    
    
    def show_dialog(self, mess="Creation", codemess="creat_production"):
        return {
            'name':'Production',            
            'code_message': codemess,
            
            'context':{'default_confirm_message': mess, 
                       'default_code_message': codemess },
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'wiz.dialog',
            'target':'new' 
        }    
        