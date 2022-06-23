# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

class miadiCatStatResPartner(models.Model):
    _inherit = "res.partner"
    di_statistics_alpha_1 = fields.Char(string='statistics alpha 1')
    di_statistics_alpha_2 = fields.Char(string='statistics alpha 2')
    di_statistics_alpha_3 = fields.Char(string='statistics alpha 3')
    di_statistics_alpha_4 = fields.Char(string='statistics alpha 4')
    di_statistics_alpha_5 = fields.Char(string='statistics alpha 5')
    
    def write(self, vals):
        _logger.info("write")
        _write_categ_partner = self.env['ir.config_parameter'].sudo().get_param('miadi.di_write_categ_partner') or False
        _logger.info("_write_categ_partner : %s" , _write_categ_partner)
        if _write_categ_partner:
            
            for record in self:
                    
                categ_ids = record.category_id
                _logger.info("Listes des catégories : %s", categ_ids)
                i = -1
                for categ in categ_ids:
                    parent_categ=categ.parent_path
                    list_parent_categ = parent_categ.split("/")
                    _logger.info("Listes des parents : %s", list_parent_categ)
                    for parent_categ in list_parent_categ:
                        if parent_categ:
                            categ = self.env['res.partner.category'].search([('id', '=ilike', parent_categ)], limit=1)
                            if categ.name:
                                _logger.info("i = %s - Code catégorie : %s - Nom catégorie : %s", i,parent_categ,categ.name)
                                i+=1
                                if i == 0:
                                    vals['di_statistics_alpha_1'] = categ.name.strip()
                                elif i == 1:
                                    vals['di_statistics_alpha_2'] = categ.name.strip()
                                elif i == 2:
                                    vals['di_statistics_alpha_3'] = categ.name.strip()
                                elif i == 3:
                                    vals['di_statistics_alpha_4'] = categ.name.strip()
                                    #alpha_4 = categ.name.strip()
                                elif i == 4:
                                    vals['di_statistics_alpha_5'] = categ.name.strip()
                                
                
            _logger.info("Listes des valeurs modifiées : %s", vals)  
        result = super(miadiCatStatResPartner, self).write(vals) 
        
    @api.model_create_multi
    def create(self, vals_list):
        partners = super(miadiCatStatResPartner, self).create(vals_list)
        _write_categ_partner = self.env['ir.config_parameter'].sudo().get_param('miadi.di_write_categ_partner') or False
        if _write_categ_partner:
            for partner, vals in zip(partners, vals_list):
                related_vals = {}
                
                categ_ids = partner.category_id
                _logger.info("Listes des catégories : %s", categ_ids)
                i = -1
                for categ in categ_ids:
                    parent_categ=categ.parent_path
                    list_parent_categ = parent_categ.split("/")
                    _logger.info("Listes des parents : %s", list_parent_categ)
                    for parent_categ in list_parent_categ:
                        if parent_categ:
                            categ = self.env['res.partner.category'].search([('id', '=ilike', parent_categ)], limit=1)
                            if categ.name:
                                _logger.info("i = %s - Code catégorie : %s - Nom catégorie : %s", i,parent_categ,categ.name)
                                i+=1
                                if i == 0:
                                    related_vals['di_statistics_alpha_1'] = categ.name.strip()
                                elif i == 1:
                                    related_vals['di_statistics_alpha_2'] = categ.name.strip()
                                elif i == 2:
                                    related_vals['di_statistics_alpha_3'] = categ.name.strip()
                                elif i == 3:
                                    related_vals['di_statistics_alpha_4'] = categ.name.strip()
                                elif i == 4:
                                    related_vals['di_statistics_alpha_5'] = categ.name.strip()
                
                if related_vals:
                    partner.write(related_vals)
                    
        return partners         