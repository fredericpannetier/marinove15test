# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import tools
from odoo import fields, models


class DiSaleReport(models.Model):
    _inherit = "sale.report"

    commitment_date = fields.Datetime('Delivery Date', readonly=True)
    di_date_depart = fields.Date(string='Date de départ', readonly=True)
    di_warehouse_name= fields.Char('Warehouse Name', readonly=True)
    di_emplacement_name= fields.Char('Emplacement', readonly=True)
    di_state_name = fields.Char(string="Department", readonly=True)
    di_state_code = fields.Char(string="Code department", readonly=True)
    di_fiscal_position = fields.Char(string="Position fiscale", readonly=True)
    di_variete_name = fields.Char(string='Variété', readonly=True)
    di_taille_name = fields.Char(string='Taille', readonly=True)
    di_espece_name = fields.Char(string='Espèce', readonly=True)
    di_adv_name = fields.Char(string='ADV', readonly=True)
    
    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        fields['commitment_date'] = ', s.commitment_date as commitment_date'
        fields['di_date_depart'] = ', s.di_date_depart as di_date_depart'
        fields['di_warehouse_name'] = ', sw.name as di_warehouse_name'
        fields['di_emplacement_name'] = ', sl.name as di_emplacement_name'
        fields['di_state_name'] = ', s.di_state_name as di_state_name'
        fields['di_state_code'] = ', s.di_state_code as di_state_code'
        fields['di_fiscal_position'] = ', afp.name as di_fiscal_position'
        fields['di_variete_name'] = ', l.di_variete_name as di_variete_name'
        fields['di_taille_name'] = ', l.di_taille_name as di_taille_name'
        fields['di_espece_name'] = ', l.di_espece_name as di_espece_name'
        fields['di_adv_name'] = ', s.di_adv_name as di_adv_name'
        
        from_clause += """
                        left join stock_warehouse sw on (s.warehouse_id = sw.id) 
                        left join stock_location sl on (l.di_warehouse_id = sl.id)
                        left join account_fiscal_position afp on (s.fiscal_position_id = afp.id)
                       """
        
        groupby += """, s.commitment_date, di_date_depart, di_warehouse_name, di_emplacement_name, 
                    s.di_state_name, s.di_state_code, di_fiscal_position, di_variete_name, di_taille_name, di_espece_name, di_adv_name

                    """
        
        return super(DiSaleReport, self)._query(with_clause, fields, groupby, from_clause)

    def _select(self):
        return super(DiSaleReport, self)._select() + """,s.commitment_date, s.di_date_depart, di_warehouse_name, di_emplacement_name, 
                    s.di_state_name, s.di_state_code, di_fiscal_position, di_variete_name, di_taille_name, di_espece_name, di_adv_name
                """
          
                
   
    def _group_by(self):
        return super(DiSaleReport, self)._group_by() + """, s.commitment_date, di_date_depart, di_warehouse_name, di_emplacement_name, 
                    s.di_state_name, s.di_state_code, di_fiscal_position, di_variete_name, di_taille_name, di_espece_name, di_adv_name

                    """
                   
