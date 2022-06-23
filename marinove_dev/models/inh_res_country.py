# See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _

class DiResCountry(models.Model):
    _inherit = 'res.country'
    
    di_etiq_mention = fields.Text(string="Etiquette Mention")