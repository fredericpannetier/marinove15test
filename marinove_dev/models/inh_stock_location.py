# See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _


class DiWarehouse(models.Model):
    _inherit = 'stock.location'

    di_sanit_pays = fields.Char("Code pays du numéro d'agrément (FR)")
    di_sanit = fields.Char("Agrément sanitaire")
    di_etiq_mention = fields.Char(string="Etiquette Mention")
    di_etiq_printer = fields.Many2one('di.printing.printer', string='Etiquette Printer', domain=[('isimpetiq', '=', True)])
    di_etiq_model =  fields.Many2one('di.printing.etiqmodel', string='Etiquette model')