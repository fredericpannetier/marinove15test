# See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _

class DiFiscalPosition(models.Model):
    _inherit = 'account.fiscal.position'
    
    di_etiq_mention = fields.Text(string="Etiquette Mention")