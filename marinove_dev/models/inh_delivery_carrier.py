# See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _

class DiDeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'
    
    di_street = fields.Char(string="Rue")
    di_street2 = fields.Char(string="Rue 2")
    di_zip = fields.Char(string="CP")
    di_city = fields.Char(string="Ville")
    di_email = fields.Char(string="EMail")
    di_phone = fields.Char(string="Téléphone")
    di_mobile = fields.Char(string="Mobile")
    di_rcs = fields.Char(string="RCS")
    di_siret = fields.Char(string="Siret")
    di_capital = fields.Char(string="Capital")
    di_schedule= fields.Char(string="Schedule")
    di_etiq_mention = fields.Char(string="Etiquette Mention")
    