# See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _

class DiResPartner(models.Model):
    _inherit = 'res.partner'
    
    di_state_code = fields.Char(string="Code department", related='state_id.code', store=True)
    di_comment_invoice = fields.Text(string='Invoice Notes')
