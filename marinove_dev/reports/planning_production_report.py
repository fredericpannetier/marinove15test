# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import tools
from odoo import SUPERUSER_ID, fields, models, api

class DiPlanningProductionReport(models.Model):
    _name = "di.report.planning.production"
    _description = "Planning Production"
    _auto = False
    _rec_name = 'date_depart'
    _order = 'date_depart asc'

    id = fields.Integer("", readonly=True)
    name_lig = fields.Char(string="Name")
    partner_id = fields.Many2one('res.partner', string='Customer', index=True) 
    partner_name = fields.Char(string="Partner Name")

    company_id = fields.Many2one('res.company', 'Company')
    user_id = fields.Many2one('res.users', string='Salesperson', index=True)
    team_id = fields.Many2one('crm.team', string='Sales Team', index=True)

    statut_commande = fields.Char(string="Etape")
    stage_id = fields.Many2one('crm.stage', string='Stage', index=True)
    product_id = fields.Many2one('product.product', string='Product')
    variete_id = fields.Many2one('x_varietes', string='Variété', ondelete='set null')
    taille_id = fields.Many2one('x_tailles', string='Taille', ondelete='set null')
    espece_id = fields.Many2one('x_especes', string='Espèce', ondelete='set null')

    date_depart = fields.Date(string='Date de départ')
    
    poids_kg = fields.Float(string='Poids en Kg')
    quantite_maxi = fields.Integer(string='Quantité maxi (en milliers)')
    quantite_mini = fields.Integer(string='Quantité mini (en milliers)')
    prix_millier  = fields.Float(string='Prix (en milliers)')
    
    prix_kg = fields.Float(string='Prix au Kg')
    montant_ca = fields.Float(string='Montant')
 
    carrier_id = fields.Many2one('delivery.carrier', string='Transporteur', ondelete='set null')
    warehouse_id = fields.Many2one('stock.location', string='Emplacement', ondelete='set null')
    lieu_livraison = fields.Char(string='Lieu de Livraison 1')
    schedule = fields.Char(string='Schedule')
    unite_categorie_name = fields.Char(string="Nom Catégorie de l'unité")
    unite_id = fields.Many2one('uom.uom', string='Unité')
    
    description = fields.Char(string="Description")
    active = fields.Boolean('Active', default=True)
    packaging = fields.Many2one('di.packaging', string='Packaging')
    no_commande = fields.Char(string="No Document")
    
    inv = fields.Boolean(string="Invisible", compute="c_inv", default= False, store=False)
    
    def c_inv(self):
        user = self.env['res.users'].browse(self.env.uid)
        group_stock_manager = user.has_group('stock.group_stock_manager')

        group_user = user.has_group('base.group_user')
        if SUPERUSER_ID == self.env.uid or group_user == True:
            invis = False
        else:
            invis = True

        for record in self:
            record.inv = invis
 
    def _selectC(self):
        
        select_str = """
 SELECT cl.id, cl.name AS name_lig, partner_id, partner_name AS partner_name, cl.company_id AS company_id, cl.user_id AS user_id, cl.team_id AS team_id, 
 CASE WHEN st.name ilike 'confirm%' THEN 'Confirmé client' ELSE 'Confirmé et planifié' END as statut_commande, stage_id,
x_studio_article as product_id, x_studio_varit AS variete_id, x_studio_taille AS taille_id, x_studio_espece AS espece_id, x_studio_date_de_dpart AS date_depart, 
x_studio_poids_kg AS poids_kg, x_studio_quantit_maxi_en_milliers AS quantite_maxi, x_studio_quantit_mini_en_milliers AS quantite_mini, 
x_studio_prix AS prix_millier, x_studio_prix_kg AS prix_kg, x_studio_montant AS montant_ca, 
x_studio_transporteur_1 AS carrier_id, x_studio_site_de_depart as warehouse_id, x_studio_lieu_de_livraison AS lieu_livraison, 
di_schedule AS schedule, uc.name AS unite_categorie_name, description as description, cl.active  as active, 
x_studio_unite AS unite_id, null as packaging, ' ' as no_commande  

FROM crm_lead cl
LEFT JOIN uom_uom uu ON uu.id = x_studio_unite
LEFT JOIN uom_category uc ON uc.id = uu.category_id
LEFT JOIN crm_stage st ON cl.stage_id = st.id

where ((st.name ilike 'confirm%') or (st.is_won =true))
and x_studio_date_de_dpart is not null
and cl.active = true

UNION ALL

select ol.id, ol.name AS name_lig, so.partner_id, rp.name AS partner_name, so.company_id AS company_id, so.user_id AS user_id, so.team_id AS team_id, 
case so.state when 'draft' then 'Devis' else case so.state when 'sent' then 'Devis envoyé' else'Commande' end end as statut_commande, null as stage_id, 
product_id AS product_id, pt.di_variete_id AS variete_id, pt.di_taille_id AS taille_id, pt.di_espece_id AS espece_id, di_date_depart AS date_depart ,
di_poids_kg AS poids_kg, di_quantite_maxi AS quantite_maxi, di_quantite_mini AS quantite_mini, 
di_prix AS prix_millier, di_prix_kg AS prix_kg, price_total AS montant_ca,
di_carrier_id AS carrier_id, di_warehouse_id as warehouse_id, di_lieu_livraison AS lieu_livraison, 
ol.di_schedule AS schedule, uc.name AS unite_categorie_name, ol.di_comment  as description, True as active, 
ol.product_uom AS unite_id, so.di_packaging as packaging, so.name as no_commande 

FROM sale_order_line ol
LEFT JOIN sale_order so ON so.id = ol.order_id
LEFT JOIN res_partner rp ON rp.id = so.partner_id
LEFT JOIN product_product pp ON pp.id = ol.product_id 
LEFT JOIN product_template pt ON pt.id = pp.product_tmpl_id
LEFT JOIN uom_uom uu ON uu.id = ol.product_uom
LEFT JOIN uom_category uc ON uc.id = uu.category_id
WHERE product_id is not null and pt.type <> 'service'
and di_date_depart is not null and so.state in ('draft','sale','sent')


        """ 
        return select_str


    def init(self):
       
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
            %s
            
            )""" % (self._table, self._selectC()))

