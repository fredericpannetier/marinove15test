# See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class DiAccountPayment(models.Model):
    _inherit = 'account.payment'
    
    """
    @api.depends('journal_id', 'partner_id', 'partner_type', 'is_internal_transfer')
    def _compute_destination_account_id(self):
        super(DiAccountPayment, self)._compute_destination_account_id()
        for pay in self:
            if pay.destination_account_id.display_name[0:3] == '411':
               
                msg = 'Can not choose this partner. ' \
                      '%s as on %s !\nCheck Partner Accounts  ' \
                      '' % (pay.partner_id.name, pay.destination_account_id.display_name)
                pay.partner_id = None
                pay.destination_account_id = None   
                #pay.destination_account_id.display_name = False  
                raise UserError(_('Account Partner !\n' + msg)) 
    """
            
    @api.onchange('destination_account_id')       
    def di_change_destination_account_id(self):
        warning = {}
        if self.destination_account_id:
            if self.destination_account_id.display_name[0:3] == '411':
               
                msg = _('Can not choose this partner. ' \
                      '%s as on %s !\nCheck Partner Accounts  ' \
                      '' % (self.partner_id.name, self.destination_account_id.display_name))
                self.partner_id = False
                self.destination_account_id = False   
                #pay.destination_account_id.display_name = False  
                #raise UserError(_('Account Partner !\n' + msg)) 
            
                warning = {
                    'title': _("Warning for %s", self.partner_id.name),
                    'message': msg
                }
            
        if warning:
            return {'warning': warning}         