# See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _

class DiWizAccountingTransfer(models.TransientModel):
    _inherit = 'wiz.accountingtransfer'
    
    def di_libelle_ecriture (self, move_type, n_piece, partner):
        lib = super(DiWizAccountingTransfer, self).di_libelle_ecriture(move_type, n_piece, partner)
        lib = lib.replace('/', '').replace('Facture ', '').replace('Avoir ', '')
        
        return lib