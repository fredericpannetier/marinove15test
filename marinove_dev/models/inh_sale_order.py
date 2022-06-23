# See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class DiSaleOrder(models.Model):
    _inherit = "sale.order"
    
    @api.onchange('carrier_id')
    def di_default_schedule(self):
        if self.carrier_id:
            self.di_schedule = self.carrier_id.di_schedule


    #di_commentaire_carrier_1 = fields.Char(string='Commentaire Transporteur 1')
    #di_montant_carrier_1 = fields.Monetary(string='Montant Transporteur 1', compute='di_compute_amount_total_delivery')
    #di_carrier_id_2 = fields.Many2one('delivery.carrier', string='Transporteur 2', ondelete='set null')
    #di_commentaire_carrier_2 = fields.Char(string='Commentaire Transporteur 2')
    #di_montant_carrier_2 = fields.Monetary(string='Montant Transporteur 2')
    #di_lieu_livraison_2 = fields.Char(string='Lieu de Livraison 2')
    #di_warehouse_id_2 = fields.Many2one('stock.warehouse', string='Entrepôt 2', ondelete='set null')
    #di_nb_palette = fields.Integer(string='Nombre de Palettes')
    di_poids_kg_total = fields.Float(string='Poids Total en Kg', store=True, readonly=True, compute='di_compute_ligne')
    di_nb_colis_total = fields.Integer(string='Nombre de Colis Total', store=True, readonly=True, compute='di_compute_ligne')
   
    di_date_depart = fields.Date(string='Date de départ')
    di_lieu_livraison_1 = fields.Char(string='Lieu de Livraison 1')
    
    di_country_name = fields.Char(string="Pays", related='partner_id.country_id.name', store=True)
    di_state_name = fields.Char(string="Department", related='partner_id.state_id.name', store=True)
    di_state_code = fields.Char(string="Code department", related='partner_id.state_id.code', store=True)
    #di_schedule= fields.Char(string="Schedule", default=lambda self: self.carrier_id.di_schedule)
    di_schedule= fields.Char(string="Schedule", default=di_default_schedule)
    di_comment = fields.Text('Notes')
    di_packaging = fields.Many2one('di.packaging', string='Packaging')
    x_studio_n_semaine_1 = fields.Integer(string='N° semaine')
    di_adv_name = fields.Char(string='ADV', related='partner_id.x_studio_adv.name', store=True)
 
    @api.depends('order_line')
    def di_compute_amount_total_delivery(self):
        for order in self:
            delivery_cost = sum([l.price_total for l in order.order_line if l.is_delivery])
            order.di_montant_carrier_1 = delivery_cost
    
    @api.depends('order_line.di_poids_kg', 'order_line.di_nb_colis')
    def di_compute_ligne(self):
        for order in self:
            total_poids = 0.0
            total_colis = 0
            for line in order.order_line:
                total_poids += line.di_poids_kg
                total_colis += line.di_nb_colis
                
            order.di_poids_kg_total = total_poids
            order.di_nb_colis_total = total_colis
            
    @api.onchange('partner_id')
    def di_onchange_partner_id_carrier(self):
        """
        Update the following fields when the partner is changed:
        - Carrier
        """
        if not self.partner_id:
            self.update({
                'carrier_id': False,

            })
            return
    
        values = { 
            'carrier_id' : self.partner_id.property_delivery_carrier_id and self.partner_id.property_delivery_carrier_id.id or False
            }
        
        self.update(values)

    def _prepare_invoice(self):
        tot_delivered = 0.0
        nb_deliverable = 0
        for order in self:
            for line in order.order_line:
                if line.qty_delivered > 0:
                    tot_delivered += line.qty_delivered
                if line.product_id.type == 'consu':
                    nb_deliverable += 1
        if tot_delivered == 0 and nb_deliverable > 0:
            raise UserError(_('No deliverable product are delivered'))
        
        invoice_vals = super(DiSaleOrder, self)._prepare_invoice()
        return invoice_vals
        
    def _create_invoices(self, grouped=False, final=False, date=None):
        #if not self.sale_order_id and self.sale_order_id.invoice_status != 'to invoice':
        #    raise UserError(_("The selected Sales Order should contain something to invoice."))
    
        for line in self:
            if line.partner_invoice_id.commercial_partner_id.property_account_receivable_id.code[0:3] == '411':
                raise UserError(_("One of the selected Sales Order contain a partner account with 411. %s - %s") % (line.partner_id.name, line.name))
            if line.partner_invoice_id.type[0:7] not in ['contact', 'invoice']:
                raise UserError(_("One of the selected Sales Order contain a partner with an incorrect address. %s - %s") % (line.partner_id.name, line.name))
    
        res = super(DiSaleOrder, self)._create_invoices(grouped=False, final=False, date=None)    
        return res

    def update_position_fiscal(self):
        records = self.env['sale.order'].search([('fiscal_position_id', '=', False)])
        if records:
            for record in records:
                record.update({
                    'fiscal_position_id': record.partner_id.property_account_position_id.id,
                    'user_id': record.partner_id.user_id.id,
                     })
                    
        records = self.env['account.move'].search([('fiscal_position_id', '=', False),('move_type','in',('out_invoice','out_refund'))])
        if records:
            for record in records:
                record.update({
                    'fiscal_position_id': record.commercial_partner_id.property_account_position_id.id,
                    'invoice_user_id': record.partner_id.user_id.id,
                     })
                    
        
            
    def action_confirm(self):
        result = super(DiSaleOrder, self).action_confirm()
        
        # Modification de l'emplacement dans les lignes du bon de livraison : stock.move.line
        self.env.cr.commit()
        id_order = self.id
        query = """ SELECT so.id as order_id, sp.id as picking_id, sm.id as move_id, 
                sol.id as line_id, sol.di_warehouse_id as emplacement, sol.product_uom as unite, sol.di_poids_kg as poids   
                FROM sale_order so
                INNER JOIN stock_picking sp on sp.sale_id = so.id 
                INNER JOIN stock_move sm on sm.picking_id = sp.id
                INNER JOIN sale_order_line sol on sm.sale_line_id = sol.id
                where so.id=%s """ % int(id_order)
        self._cr.execute(query)
        ids_sp = [(r[0], r[1], r[2], r[3], r[4], r[5], r[6]) for r in self.env.cr.fetchall()]    
        for order_id, picking_id, move_id, line_id, emplacement, unite, poids in ids_sp:
            move_line = self.env["stock.move.line"].search(
                [
                    ("move_id", "=", move_id),
                    ("picking_id", "=", picking_id),
                ],
                limit=1,
                )
            if move_line.id:
                move_line.update(
                    {
                        "location_id": emplacement or False,
                        "product_uom_id": unite or False,
                        "di_poids_kg": poids or 0,
                    }
                )      
       
            stock_picking = self.env["stock.picking"].search(
                [
                    ("id", "=", picking_id),
                ],
                limit=1,
                )
            if stock_picking.id:
                stock_picking.update(
                    {
                        "location_id": emplacement or False,
                    }
                )      
       
        return True
    
class DiSaleOrderLine(models.Model):
    _inherit = 'sale.order.line'  
   
    @api.onchange('di_carrier_id')
    def di_default_schedule(self):
        if self.di_carrier_id:
            self.di_schedule = self.di_carrier_id.di_schedule
             
    di_poids_kg = fields.Float(string='Poids en Kg')#, store=True, readonly=True, compute='di_compute_qte_poids')
    di_nb_colis = fields.Integer(string='Nombre de Colis')
    di_quantite_maxi = fields.Integer(string='Quantité maxi (en milliers)')#, store=True, readonly=True, compute='di_compute_qte_poids')
    di_quantite_mini = fields.Integer(string='Quantité mini (en milliers)')#, store=True, readonly=True, compute='di_compute_qte_poids')
    di_prix = fields.Monetary(string='Prix (en milliers)')#, store=True, readonly=True, compute='di_compute_montant')
    di_prix_kg = fields.Monetary(string='Prix au Kg')#, store=True, readonly=True, compute='di_compute_montant')
    
    di_warehouse_id = fields.Many2one('stock.location', string='Emplacement', ondelete='set null')
    di_lieu_livraison = fields.Char(string='Lieu de Livraison 1')
    di_carrier_id = fields.Many2one('delivery.carrier', string='Transporteur', ondelete='set null')
    di_unite_categorie_name = fields.Char(string="Nom Catégorie de l'unité", related='product_uom.category_id.name', store=True)
    di_geste_commercial = fields.Selection([("Mortalite", "Mortalité"), ("Raison_Comm", "Raison Commerciale"),
                              ("Surclassement", "Surclassement Taille")], string="Geste Commercial")
    di_schedule= fields.Char(string="Schedule", default=di_default_schedule)
    di_comment = fields.Text('Notes')
    
    di_variete_name = fields.Char(string='Variété', related='product_id.di_variete_id.x_name', store=True)
    di_taille_name = fields.Char(string='Taille', related='product_id.di_taille_id.x_name', store=True)
    di_espece_name = fields.Char(string='Espèce', related='product_id.di_espece_id.x_name', store=True)

    
    #@api.depends('product_uom_qty','product_uom', 'product_id','price_unit','di_poids_kg','di_quantite_mini','di_quantite_maxi','di_prix','di_prix_kg')
    @api.onchange('product_uom_qty','product_uom', 'product_id','price_unit')
    def di_compute_qte_poids(self):
        
        for line in self:
            if line.product_uom.category_id.name == "Poids":
                line.di_poids_kg = line.product_uom_qty
                line.di_quantite_mini = line.product_uom_qty * line.product_id.di_nb_bete_mini_kg / 1000
                line.di_quantite_maxi = line.product_uom_qty * line.product_id.di_nb_bete_maxi_kg / 1000
                line.di_prix_kg = line.price_unit 
                line.di_prix = 0
            else:    
                if line.product_id.di_nb_bete_maxi_kg !=0:
                    line.di_poids_kg = line.product_uom_qty / line.product_id.di_nb_bete_maxi_kg * 1000
                    
                else:
                    line.di_poids_kg = 0 
                    
                line.di_prix_kg = 0    
                line.di_prix = line.price_unit
                line.di_quantite_maxi = line.product_uom_qty
                line.di_quantite_mini = line.product_uom_qty
    
    """
    @api.onchange('name')
    def _update_move_line(self):
        
        for line in self:
            line.di_comment = line.name
            for move in line.move_ids:
                moveline.update({
                    'name': line.name,
                    'description_picking': line.name,
                    })
                for moveline in move.move_line_ids:
                    moveline.update({
                        #'name': line.name,
                        'description_picking': line.name,
                        'di_desc_cde': line.name,
                        })
    """
          
    def _prepare_invoice_line(self, **optional_values):
        invoice_line = super(DiSaleOrderLine, self)._prepare_invoice_line(**optional_values)
        #invoice_line['di_poids_kg'] = self.di_poids_kg
        #invoice_line['di_prix_kg'] = self.di_prix_kg
        #invoice_line['di_prix'] = self.di_prix
        #invoice_line['di_quantite_mini'] = self.di_quantite_mini
        #invoice_line['di_quantite_maxi'] = self.di_quantite_maxi
        
        
        #return invoice_line
        
        #prix_kg = self.di_prix_kg
        #prix = self.di_prix
        #quantite_mini = self.di_quantite_mini
        #quantite_maxi = self.di_quantite_maxi
            
        for line in self:
            poids_kg = 0.0
            poids_out = 0.0
            poids_in = 0.0
            colis = 0.0
            colis_out = 0.0
            colis_in = 0.0
            palette = 0.0
            palette_out = 0.0
            palette_in = 0.0
            
            if line.qty_delivered_method == 'stock_move':

                outgoing_moves, incoming_moves = line._get_outgoing_incoming_moves()
                for move in outgoing_moves:
                    if move.state != 'done':
                        continue
                    if move.product_id.invoice_policy == 'order':
                        poids_out = move.sale_line_id.di_poids_kg
                    else:
                        poids_out += sum(move.move_line_ids.mapped('di_poids_kg_done'))    
                    colis_out += sum(move.move_line_ids.mapped('di_nb_colis')) 
                    palette_out += sum(move.move_line_ids.mapped('di_nb_palette')) 
                    #for stock in move.move_line_ids:
                    #    poids_kg += stock.di_poids_kg_done
                    
                for move in incoming_moves:
                    if move.state != 'done':
                        continue
                    if move.product_id.invoice_policy == 'order':
                        poids_in = move.sale_line_id.di_poids_kg
                    else:
                        poids_in += sum(move.move_line_ids.mapped('di_poids_kg_done'))
                    colis_in += sum(move.move_line_ids.mapped('di_nb_colis')) 
                    palette_in += sum(move.move_line_ids.mapped('di_nb_palette')) 
                    #for stock in move.move_line_ids:
                    #    poids_kg -= stock.di_poids_kg_done
                    
                    
                poids_kg = poids_kg + poids_out - poids_in
                colis = colis + colis_out - colis_in
                palette = palette + palette_out - palette_in

        invoice_line.update({'di_poids_kg': poids_kg,
                             'di_nb_colis': colis,
                             'di_nb_palette': palette,
                             'di_prix_kg': self.di_prix_kg,
                             'di_prix': self.di_prix,
                             'di_quantite_mini': self.di_quantite_mini,
                             'di_quantite_maxi': self.di_quantite_maxi,
                             
                             })
        return invoice_line

 