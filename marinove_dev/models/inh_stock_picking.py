# See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _

class DiStockPicking(models.Model):
    _inherit = 'stock.picking'
    
    di_sale_partner_id = fields.Integer(string='Client commande', related='sale_id.partner_id.id', store=True)
    x_studio_deadline = fields.Date(string='Date de départ', related='sale_id.di_date_depart', store=True) #FRPA 20211110
    #partner_id = fields.Many2one(
    #    'res.partner', 'Contact',
    #    check_company=True,
    #    states={'done': [('readonly', True)], 'cancel': [('readonly', True)]},
    #    domain=lambda self: self.di_get_partner_domain()
    #    )


    def action_print_etiq(self):
        picking_ids = self.env['wiz_stock_picking_print_etiq'].browse(self._ids)
        res = picking_ids.load_stock_picking([self.id])
        
        if len(res) >= 1:
            action = self.env.ref('marinove_dev.action_wiz_stock_picking_print_etiq').read()[0]
            action['domain'] = [('id', 'in', res)]
         
            return action  
    """
    def di_get_partner_domain(self):    
        domain=[]

        if self.sale_id:
            domain= ['&amp;', '|', ('id', '=', di_sale_partner_id), ('parent_id', '=', di_sale_partner_id) , '|', ('company_id', '=', False), ('company_id', '=', company_id)]
        else:
            domain=['|', ('company_id', '=', False), ('company_id', '=', company_id)]
        return {'domain':{'partner_id':domain}}    

    @api.onchange('sale_id')
    def di_partner_onchange(self):
        super(DiStockPicking, self).di_get_partner_domain()
        
    """
        
class DiStockMove(models.Model):
    _inherit = 'stock.move'
    
    #def _action_assign(self):
    #    super(DiStockMove, self)._action_assign()
    #    for move in self:
    #        for line in move.move_line_ids:
    #            if line.move_id.sale_line_id:
    #                line.di_poids_kg = line.move_id.sale_line_id.di_poids_kg
                
        
class DiStockMoveLine(models.Model):
    _inherit = 'stock.move.line'
    
    
    di_poids_kg = fields.Float(string='Poids Kg', store=True, readonly=False, compute='di_compute_poids')
    di_poids_kg_done = fields.Float(string='Poids Kg Fait', store=True, readonly=False, compute='di_compute_poids')
    di_nb_bete = fields.Float(string='Nb de bêtes', store=True, readonly=True, compute='di_compute_poids')
    di_nb_bete_done = fields.Float(string='Nb de bêtes Fait', store=True, readonly=False, compute='di_compute_poids')

    di_nb_colis = fields.Integer(string='Nb de Colis')
    di_nb_palette = fields.Integer(string='Nb de Palettes')
    
    di_desc_cde = fields.Text(string='Description cde', related='move_id.sale_line_id.name', store=True)
    
    #@api.depends('product_uom_qty','qty_done','product_uom_id','product_id','di_poids_kg','di_poids_kg_done','di_nb_bete','di_nb_bete_done')
    @api.depends('product_uom_qty','qty_done','product_uom_id','product_id')
    def di_compute_poids(self):
        
        for line in self:
            if line.state != 'done' or line.picking_id.is_locked == False:
                if line.product_uom_id.category_id.name == "Poids":
                    line.di_poids_kg = line.product_uom_qty
                    line.di_poids_kg_done = line.qty_done
                    line.di_nb_bete = line.product_uom_qty * line.product_id.di_nb_bete_maxi_kg / 1000
                    line.di_nb_bete_done = line.qty_done * line.product_id.di_nb_bete_maxi_kg / 1000
                else:   
                    line.di_nb_bete = line.product_uom_qty 
                    line.di_nb_bete_done = line.qty_done 
                    if line.product_id.di_nb_bete_maxi_kg !=0:
                        line.di_poids_kg = line.product_uom_qty / line.product_id.di_nb_bete_maxi_kg * 1000
                        line.di_poids_kg_done = line.qty_done / line.product_id.di_nb_bete_maxi_kg * 1000
                    
                    else:
                        line.di_poids_kg = 0
                        line.di_poids_kg_done = 0  
  