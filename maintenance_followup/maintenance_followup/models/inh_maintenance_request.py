# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class DiMaintenanceRequest(models.Model):
    _inherit = "maintenance.request"
    
    di_amount_quotation = fields.Float(string="Amount Quotation", help="Amount Quotation")

    