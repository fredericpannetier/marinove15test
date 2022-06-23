# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import date, timedelta, datetime
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class Wizard_updatestats_prod(models.TransientModel):
    _name = "wiz.updatestats.prod"
    _description = "Wizard update statistics : product"
    
    category_id = fields.Many2one('product.category', 'Internal Category', required=True)
    
    message = fields.Text(string="Information")
    
#    @api.multi
    def update_stats_prod(self):
        product_count = 0
        alpha_1 = ""
        alpha_2 = ""
        alpha_3 = ""
        alpha_4 = ""
        alpha_5 = ""
        
        categ_code = self.category_id.id 
        
        _write_categ_product = self.env['ir.config_parameter'].sudo().get_param('miadi.di_write_categ_product')
        if _write_categ_product:
            for cat in self.env['product.category'].search([('id', '=', categ_code) ]):  
                Nom_Categ=cat.complete_name
                Nom_Categ = Nom_Categ.split("/")
            
                # Recherche des produits de la catégorie
                products=self.env['product.template'].search([('categ_id', '=', cat.id) ])   
                for prod in products:
                    alpha1 = prod.di_statistics_alpha_1
                    alpha2 = prod.di_statistics_alpha_2
                    alpha3 = prod.di_statistics_alpha_3
                    alpha4 = prod.di_statistics_alpha_4
                    alpha5 = prod.di_statistics_alpha_5
                    i = 0
                    for categ in Nom_Categ:
                        if Nom_Categ[i]:
                            if i == 0:
                                alpha_1 = categ.strip()
                            elif i == 1:
                                alpha_2 = categ.strip()
                            elif i == 2:
                                alpha_3 = categ.strip()
                            elif i == 3:
                                alpha_4 = categ.strip()
                            elif i == 4:
                                alpha_5 = categ.strip()
                        i+=1
                    prod.update({
                            'di_statistics_alpha_1': alpha_1,
                            #'di_statistics_alpha_2': alpha_2,
                            #'di_statistics_alpha_3': alpha_3,
                            #'di_statistics_alpha_4': alpha_4,
                            #'di_statistics_alpha_5': alpha_5,
                        })
                    product_count = product_count + 1
            
        view_id = self.env["ir.model.data"].check_object_reference("sale_category_statistic", "wiz_update_stats_step2", True)
        self.message = ("%s %s %s %s %s %s %s") % ("Update statistics OK  for category = (",self.category_id.id, ") ", self.category_id.complete_name, " for ", product_count, " products.")
        return {"type":"ir.actions.act_window",
                "view_mode":"form",
                "view_type":"form",
                "views":[(view_id[1], "form")],
                "res_id":self.id,
                "target":"new",
                "res_model":"wiz.updatestats.prod"                
                }

class Wizard_updatestats_partner(models.TransientModel):
    _name = "wiz.updatestats.partner"
    _description = "Wizard update statistics : partner"
    
    category_id = fields.Many2one('res.partner.category', 'Internal Category', required=True)
    
    message = fields.Text(string="Information")
    
#    @api.multi
    def update_stats_partner(self):
        customer_count = 0
        alpha_1 = ""
        alpha_2 = ""
        alpha_3 = ""
        alpha_4 = ""
        alpha_5 = ""
        
        categ_code = self.category_id.id     
        _logger.info("codes catégories : %s", categ_code)
        
        _write_categ_partner = self.env['ir.config_parameter'].sudo().get_param('miadi.di_write_categ_partner')
        if _write_categ_partner:
                # Recherche des partenaires de la catégorie
                partners=self.env['res.partner'].search([('category_id', '=', categ_code) ])   
                _logger.info("Listes des partners : %s", partners)
                for partner in partners:
                    alpha1 = partner.di_statistics_alpha_1
                    alpha2 = partner.di_statistics_alpha_2
                    alpha3 = partner.di_statistics_alpha_3
                    alpha4 = partner.di_statistics_alpha_4
                    alpha5 = partner.di_statistics_alpha_5
                    _logger.info("Listes des zones stats avant : %s - %s - %s -%s -%s", alpha1,alpha2,alpha3,alpha4,alpha5)
                    parent_path_categ=self.category_id.parent_path
                    list_parent_categ = parent_path_categ.split("/")
                    _logger.info("Listes des parents : %s", list_parent_categ)
                    i = -1
                    for parent_categ in list_parent_categ:
                        if parent_categ:
                            categ = self.env['res.partner.category'].search([('id', '=ilike', parent_categ)], limit=1)
                            if categ.name:
                                _logger.info("i = %s - Code catégorie : %s - Nom catégorie : %s", i,parent_categ,categ.name)
                                i+=1
                                if i == 0:
                                   alpha_1 = categ.name.strip()
                                elif i == 1:
                                   alpha_2 = categ.name.strip()
                                elif i == 2:
                                   alpha_3 = categ.name.strip()
                                elif i == 3:
                                   alpha_4 = categ.name.strip()
                                elif i == 4:
                                    alpha_5 = categ.name.strip()
                                   
                    
                    _logger.info("Listes des zones stats clt avant : %s - %s - %s -%s -%s",  partner.di_statistics_alpha_1, partner.di_statistics_alpha_2, partner.di_statistics_alpha_3, partner.di_statistics_alpha_4, partner.di_statistics_alpha_5)
        
                   
                    partner.update({
                            'di_statistics_alpha_1': alpha_1,
                            #'di_statistics_alpha_2': alpha_2,
                            #'di_statistics_alpha_3': alpha_3,
                            #'di_statistics_alpha_4': alpha_4,
                            #'di_statistics_alpha_5': alpha_5,
                        })
                    
                    _logger.info("Listes des zones stats après : %s - %s - %s -%s -%s", alpha1,alpha2,alpha3,alpha4,alpha5)
                    _logger.info("Listes des zones stats clt après : %s - %s - %s -%s -%s",  partner.di_statistics_alpha_1, partner.di_statistics_alpha_2, partner.di_statistics_alpha_3, partner.di_statistics_alpha_4, partner.di_statistics_alpha_5)
        
                    customer_count = customer_count +1
                    
        view_id = self.env["ir.model.data"].check_object_reference("sale_category_statistic", "wiz_update_stats_step4", True)
        self.message = ("%s %s %s %s %s %s %s") % ("Update statistics OK  for category = (",self.category_id.id, ") ", self.category_id.name, " for ", customer_count, " partners.")
        return {"type":"ir.actions.act_window",
                "view_mode":"form",
                "view_type":"form",
                "views":[(view_id[1], "form")],
                "res_id":self.id,
                "target":"new",
                "res_model":"wiz.updatestats.partner"                
                }