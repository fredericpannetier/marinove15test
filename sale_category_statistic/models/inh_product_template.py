# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, Warning, UserError, AccessError
import logging

_logger = logging.getLogger(__name__)

class miadiCatStatProductTemplate(models.Model):
    _inherit = "product.template"
    di_statistics_alpha_1 = fields.Char(string='Statistics alpha 1')
    di_statistics_alpha_2 = fields.Char(string='Statistics alpha 2')
    di_statistics_alpha_3 = fields.Char(string='Statistics alpha 3')
    di_statistics_alpha_4 = fields.Char(string='Statistics alpha 4')
    di_statistics_alpha_5 = fields.Char(string='Statistics alpha 5')
    

    def write(self, vals):
        vals = self.get_vals_stat(vals)
        result = super(miadiCatStatProductTemplate, self).write(vals)    
     
    @api.model_create_multi
    def create(self, vals_list):
        templates = super(miadiCatStatProductTemplate, self).create(vals_list)
        _write_categ_product = self.env['ir.config_parameter'].sudo().get_param('miadi.di_write_categ_product') or False
        if _write_categ_product:
            for template, vals in zip(templates, vals_list):
                related_vals = {}
                Nom_Categ =''
                if template.categ_id:
                    Nom_Categ=template.categ_id.complete_name
                if Nom_Categ:
                    Nom_Categ = Nom_Categ.split("/")
                    i = 0
                    for categ in Nom_Categ:
                        if Nom_Categ[i]:
                            if i == 0:
                                related_vals['di_statistics_alpha_1']  = categ.strip()
                            elif i == 1:
                                related_vals['di_statistics_alpha_2'] = categ.strip()
                            elif i == 2:
                                related_vals['di_statistics_alpha_3'] = categ.strip()
                            elif i == 3:
                                related_vals['di_statistics_alpha_4'] = categ.strip()
                            elif i == 4:
                                related_vals['di_statistics_alpha_5'] = categ.strip()
                        i+=1 
                        if related_vals:
                            template.write(related_vals)
                    
        return templates
            
    def get_vals_stat(self, vals):
        _write_categ_product = self.env['ir.config_parameter'].sudo().get_param('miadi.di_write_categ_product') or False
        _logger.info("_write_categ_product : %s" , _write_categ_product)
        if _write_categ_product:
            Nom_Categ =''
            for record in self:
                if record.categ_id:
                    Nom_Categ=record.categ_id.complete_name
                if Nom_Categ:
                    Nom_Categ = Nom_Categ.split("/")
                    i = 0
                    for categ in Nom_Categ:
                        if Nom_Categ[i]:
                            if i == 0:
                                vals['di_statistics_alpha_1'] = categ.strip()
                            elif i == 1:
                                vals['di_statistics_alpha_2'] = categ.strip()
                            elif i == 2:
                                vals['di_statistics_alpha_3'] = categ.strip()
                            elif i == 3:
                                vals['di_statistics_alpha_4'] = categ.strip()
                            elif i == 4:
                                vals['di_statistics_alpha_5'] = categ.strip()
                        i+=1
                    
                    _logger.info("Listes des valeurs modifiées : %s", vals)  
        return vals    
    