# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import tools
from odoo import fields, models


class DiAccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"

    price_unit_average = fields.Float(string='Average Price Unit', readonly=True, group_operator="avg")
    calcul_stat  = fields.Boolean('Calcul Stat')
    
    di_adv_name = fields.Char(string='ADV', readonly=True)
    di_depart_name = fields.Char(string="Department", readonly=True)
    di_depart_code = fields.Char(string="Code department", readonly=True)
    di_variete_name = fields.Char(string='Variété', readonly=True)
    di_taille_name = fields.Char(string='Taille', readonly=True)
    di_espece_name = fields.Char(string='Espèce', readonly=True)


    def _select(self):
        # * (CASE WHEN move.move_type IN ('in_invoice','out_refund','in_receipt') THEN -1 ELSE 1 END)
        #(currency_table.rate * (-line.balance / NULLIF(COALESCE(uom_line.factor, 1) / COALESCE(uom_template.factor, 1), 0.0)) / NULLIF(CASE WHEN line.quantity=0 THEN 1 ELSE COALESCE(line.quantity,1) END / NULLIF(COALESCE(uom_line.factor, 1) / COALESCE(uom_template.factor, 1), 0.0) , 1) ) 
                                                                               
        return super(DiAccountInvoiceReport, self)._select() + """,
            CASE WHEN move.move_type IN ('out_refund') AND line.quantity in (-1,0,1) THEN 0 ELSE
ROUND( 
    (currency_table.rate * (-line.balance / COALESCE(uom_line.factor,1) / COALESCE(uom_template.factor, 1)) / 
    CASE WHEN line.quantity=0 THEN 1 ELSE COALESCE(line.quantity,1) END / COALESCE(uom_line.factor, 1) / COALESCE(uom_template.factor, 1) * (CASE WHEN move.move_type IN ('in_invoice','out_refund','in_receipt') THEN -1 ELSE 1 END) 
       )
    ,2) 
    END
                    AS price_unit_average 
            , category.di_calcul_stat  AS calcul_stat   
            , move.di_adv_name, move.di_depart_name, move.di_depart_code, line.di_variete_name , line.di_taille_name , line.di_espece_name
                             
                """


    def _from(self):
        return super(DiAccountInvoiceReport, self)._from() + """
            LEFT JOIN product_category category on category.id = template.categ_id
            """