# See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _


class DiWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    di_sanit = fields.Char("Agrément sanitaire")
