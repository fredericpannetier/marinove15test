# See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _


class DiProdCateg(models.Model):
    _inherit = 'product.category'

    di_etiq_mention = fields.Char(string="Etiquette Mention")