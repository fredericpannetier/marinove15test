# See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _

class DiPackaging(models.Model):
    _name = "di.packaging"
    _description = "Packaging"
    
    name = fields.Char(string='Name')
    code = fields.Char(string='Code')
    
    _sql_constraints = [("name_uniq","unique(name)","This packaging already exists with this name."),]