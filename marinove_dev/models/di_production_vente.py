# See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _

class DiProductionVente(models.Model):
    _name = "di.production.vente"
    _description = "Statistique Production des ventes"
    
    name = fields.Char(string="Name")
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
    
    def update_data_production(self):
        #action = {'type': 'ir.actions.act_window_close'}
        
        query = "DELETE FROM di_production_vente"
        self.env.cr.execute(query)
        
        won_stage_id = self.env['crm.stage'].search([('is_won', '=', True)], limit=1).id
    
        query = """
SELECT cl.name, partner_id, partner_name AS partner_name, cl.company_id, cl.user_id, cl.team_id, CASE WHEN st.name ilike 'confirm%' THEN 'Confirmé client' ELSE 'Confirmé et planifié' END as statut_cde, stage_id,
x_studio_article, x_studio_varit, x_studio_taille, x_studio_espece, x_studio_date_de_dpart AS date_depart, x_studio_poids_kg,
x_studio_quantit_maxi_en_milliers, x_studio_quantit_mini_en_milliers, x_studio_prix, x_studio_prix_kg, x_studio_montant, 
x_studio_transporteur_1, x_studio_site_de_depart as site_depart, x_studio_lieu_de_livraison, di_schedule, uc.name, description as lib, cl.active, 
x_studio_unite, null as packaging, ' ' as no_cde  

FROM crm_lead cl
LEFT JOIN uom_uom uu ON uu.id = x_studio_unite
LEFT JOIN uom_category uc ON uc.id = uu.category_id
LEFT JOIN crm_stage st ON cl.stage_id = st.id

where ((st.name ilike 'confirm%') or (st.is_won =true))
and x_studio_date_de_dpart is not null
and cl.active = true

UNION

select ol.name, so.partner_id, rp.name AS partner_name, so.company_id, so.user_id, so.team_id, 
case so.state when 'draft' then 'Devis' else case so.state when 'sent' then 'Devis envoyé' else'Commande' end end as statut_cde, null as stage_id, 
product_id, pt.di_variete_id, pt.di_taille_id, pt.di_espece_id, di_date_depart AS date_depart ,
di_poids_kg, di_quantite_maxi, di_quantite_mini, di_prix, di_prix_kg, price_total,
di_carrier_id, di_warehouse_id as site_depart, di_lieu_livraison, ol.di_schedule, uc.name, ol.di_comment  as lib, True as active, 
ol.product_uom, so.di_packaging as packaging, so.name as no_cde 

FROM sale_order_line ol
LEFT JOIN sale_order so ON so.id = ol.order_id
LEFT JOIN res_partner rp ON rp.id = so.partner_id
LEFT JOIN product_product pp ON pp.id = ol.product_id 
LEFT JOIN product_template pt ON pt.id = pp.product_tmpl_id
LEFT JOIN uom_uom uu ON uu.id = ol.product_uom
LEFT JOIN uom_category uc ON uc.id = uu.category_id
WHERE product_id is not null and pt.type <> 'service'
and di_date_depart is not null and so.state in ('draft','sale','sent')

order by date_depart,  partner_name

        """
        # 15/10/2020 seulement les opportunités Confirmé client et Confirmé planifié
        #where (st.name ilike 'intentionnel' Or st.name ilike 'Global' or st.name ilike 'confirm%')  
        #and (st.is_won = false OR st.is_won is null)

        #where x_studio_statut_de_la_commande in ('I','G','C')
        
        self.env.cr.execute(query)
        ids = [(r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10], r[11], r[12], r[13], r[14], r[15], r[16], r[17], r[18], r[19], r[20], r[21], r[22], r[23], r[24], r[25], r[26], r[27], r[28]) for r in self.env.cr.fetchall()]
        for name, partner, partner_name, cie, user,  team, statut, stage, art, variete, taille, espece, depart, pds, maxi, mini, prix, prix_kg, mont, carrier, warehouse, lieu_liv, schedule, unite_cat, lib, active, unite, packaging, no_cde in ids:   
            product_vals = {
                'name': name or '',
                'partner_id': partner or False,
                'partner_name': partner_name or '',
                'company_id': cie or False,
                'user_id': user or False,
                'team_id': team or False,
                'statut_commande': statut or '',
                'stage_id': stage or won_stage_id ,
                'product_id': art or False,
                'variete_id': variete or False,
                'taille_id': taille or False,
                'espece_id': espece or False,
                'date_depart': depart,
                'poids_kg': pds or 0,
                'quantite_maxi': maxi or 0,
                'quantite_mini': mini or 0,
                'prix_millier': prix or 0,
                'prix_kg': prix_kg or 0,
                'montant_ca': mont or 0,
                'carrier_id': carrier or False,
                'warehouse_id': warehouse or False,
                'lieu_livraison': lieu_liv or '',
                'schedule': schedule or '',
                'unite_categorie_name': unite_cat or '',
                'unite_id': unite or False,
                'description': lib or '',
                'active': active or True,
                'packaging': packaging or '',
                'no_commande': no_cde or '',

                }
            prepare_product = self.env['di.production.vente'].create(product_vals)

        self.env.cr.commit()
        
        
        #action = self.env.ref('di_production_vente_action_production').read()[0]
        #action['views'] = [(self.env.ref('di_production_vente_tree_view').id, 'tree')]
        
        #query_args = {'active': True}
        #query = """ SELECT  id FROM di_production_vente  """
        #self.env.cr.execute(query)
        #sales = [r[0] for r in self.env.cr.fetchall()]
        
        sales =self.env['di.production.vente'].search([('id','!=',False),  ]).ids
        
        action = self.env.ref('marinove_dev.di_production_vente_action_production').read()[0]
        action['domain'] = [('id', 'in', sales)]    
        return action
    
    
    def sale_production_list(self):
        
        _message = "Voulez_vous recalculer les données ?"
        return self.env['wiz.dialog'].show_dialog(_message, "creat_production" )
         
        """
        sales =self.env['di.production.vente'].search([('id','!=',False),  ]).ids
        if len(sales) == 0:
            sales = self.update_data_production()
        else: 
            action = self.env.ref('marinove_dev.di_production_vente_action_production').read()[0]
            action['domain'] = [('id', 'in', sales)]    
            return action
        """