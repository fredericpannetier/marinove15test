# See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _

class DiCurrentStock(models.Model):
    _name = "di.current.stock"
    _description = "Stock en cours : Inventaire"
    
    product_id = fields.Many2one('product.product', string='Product')
    variete_name = fields.Char(string='Variété', related='product_id.di_variete_id.x_name', store=True)
    taille_name = fields.Char(string='Taille', related='product_id.di_taille_id.x_name', store=True)
    espece_name = fields.Char(string='Espèce', related='product_id.di_espece_id.x_name', store=True)
    
    no_lot = fields.Char(string='No Lot')
    date_disponibilite = fields.Date(string='Date Disponibilité')
    date_fin_disponibilite = fields.Date(string='Date de fin de disponibilité')
    poids_kg = fields.Float(string='Poids en Kg')
    nb_bete = fields.Integer(string='Nombre de Bêtes')
    
    location_id = fields.Many2one('stock.location', string='Location')
    description = fields.Text('Notes')
    
    _sql_constraints = [("product_lot_uniq","unique(product_id,no_lot)","This product already exists with this batch."),]