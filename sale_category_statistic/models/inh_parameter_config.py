# -*- coding: utf-8 -*-
from odoo import api, fields, models, modules

class miadiCatStatResConfigSettings(models.TransientModel):
    _inherit = ['res.config.settings']
    
    di_write_categ_product = fields.Boolean(string='Write Category Product' ,config_parameter="miadi.di_write_categ_product", default=False)
    di_write_categ_partner = fields.Boolean(string='Write Category Partner',config_parameter="miadi.di_write_categ_partner", default=False)
    

    #@api.multi
    def set_values(self):
        super(miadiCatStatResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()

        _write_categ_product = self.di_write_categ_product or False
        _write_categ_partner = self.di_write_categ_partner or False

        param.set_param('miadi.di_write_categ_product', _write_categ_product)
        param.set_param('miadi.di_write_categ_partner', _write_categ_partner)
              