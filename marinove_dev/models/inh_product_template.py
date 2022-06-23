# See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _

class DiProductTemplate(models.Model):
    _inherit = 'product.template'
    
    di_nb_bete_mini_kg = fields.Integer(string="Nombre de bêtes mini par KG")
    di_nb_bete_maxi_kg = fields.Integer(string="Nombre de bêtes maxi par KG")
    di_variete_id = fields.Many2one('x_varietes', string='Variété', ondelete='set null')
    di_taille_id = fields.Many2one('x_tailles', string='Taille', ondelete='set null')
    di_espece_id = fields.Many2one('x_especes', string='Espèce', ondelete='set null')
    di_cerfa  = fields.Boolean('Generate Cerfa', default=True)
    di_etiq_model =  fields.Many2one('di.printing.etiqmodel', string='Etiquette model')
    
class DiProductCategory(models.Model):
    _inherit = 'product.category'  
    di_calcul_stat  = fields.Boolean('Calcul Stat', default=True)
      
