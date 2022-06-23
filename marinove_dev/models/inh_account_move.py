# See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _

class DiAccountMove(models.Model):
    _inherit = 'account.move'
    
    di_comment_invoice = fields.Text(string='Invoice Notes')
    di_depart_code = fields.Char(string='Department code', related='partner_id.state_id.code', store=True)
    di_depart_name = fields.Char(string='Department name', related='partner_id.state_id.name', store=True)
    di_adv_name = fields.Char(string='ADV', related='partner_id.x_studio_adv.name', store=True)
    di_country_name = fields.Char(string="Pays", related='partner_id.country_id.name', store=True)
    
    @api.onchange('partner_id')
    def di_onchange_partner_id(self):
        warning = {}
        if self.partner_id:
            self.di_comment_invoice = self.partner_id.di_comment_invoice
            
            if self.commercial_partner_id.property_account_receivable_id.code[0:3] == '411':
                warning = {
                    'title': _("Warning for %s", self.partner_id.name),
                    'message': _('Check Partner Accounts')
                }
                self.partner_id = False
                self.partner_shipping_id = False
        if warning:
            return {'warning': warning}

    
    @api.model
    def _move_autocomplete_invoice_lines_create(self, vals_list):
            
        #copie standard
        ''' During the create of an account.move with only 'invoice_line_ids' set and not 'line_ids', this method is called
        to auto compute accounting lines of the invoice. In that case, accounts will be retrieved and taxes, cash rounding
        and payment terms will be computed. At the end, the values will contains all accounting lines in 'line_ids'
        and the moves should be balanced.

        :param vals_list:   The list of values passed to the 'create' method.
        :return:            Modified list of values.
        '''
        new_vals_list = []
        for vals in vals_list:
            if not vals.get('invoice_line_ids'):
                new_vals_list.append(vals)
                continue
            # modif pour toujours mettre à jour avec les données saisies
#            if vals.get('line_ids'):
#                vals.pop('invoice_line_ids', None)
#                new_vals_list.append(vals)
#                continue
            #fin modif
            if not vals.get('move_type') and not self._context.get('default_move_type'):
                vals.pop('invoice_line_ids', None)
                new_vals_list.append(vals)
                continue
            vals['move_type'] = vals.get('move_type', self._context.get('default_move_type', 'entry'))
            if not vals['move_type'] in self.get_invoice_types(include_receipts=True):
                new_vals_list.append(vals)
                continue

            vals['line_ids'] = vals.pop('invoice_line_ids')

            if vals.get('invoice_date') and not vals.get('date'):
                vals['date'] = vals['invoice_date']

            ctx_vals = {'default_move_type': vals.get('move_type') or self._context.get('default_move_type')}
            if vals.get('currency_id'):
                ctx_vals['default_currency_id'] = vals['currency_id']
            if vals.get('journal_id'):
                ctx_vals['default_journal_id'] = vals['journal_id']
                # reorder the companies in the context so that the company of the journal
                # (which will be the company of the move) is the main one, ensuring all
                # property fields are read with the correct company
                journal_company = self.env['account.journal'].browse(vals['journal_id']).company_id
                allowed_companies = self._context.get('allowed_company_ids', journal_company.ids)
                reordered_companies = sorted(allowed_companies, key=lambda cid: cid != journal_company.id)
                ctx_vals['allowed_company_ids'] = reordered_companies
            self_ctx = self.with_context(**ctx_vals)
            new_vals = self_ctx._add_missing_default_values(vals)

            move = self_ctx.new(new_vals)
            new_vals_list.append(move._move_autocomplete_invoice_lines_values())

        return new_vals_list

    def _move_autocomplete_invoice_lines_write(self, vals):
        #copie standard
        ''' During the write of an account.move with only 'invoice_line_ids' set and not 'line_ids', this method is called
        to auto compute accounting lines of the invoice. In that case, accounts will be retrieved and taxes, cash rounding
        and payment terms will be computed. At the end, the values will contains all accounting lines in 'line_ids'
        and the moves should be balanced.

        :param vals_list:   A python dict representing the values to write.
        :return:            True if the auto-completion did something, False otherwise.
        '''
        
        # modif pour toujours mettre à jour avec les données saisies
        if not vals.get('invoice_line_ids'):
            return False
#        enable_autocomplete = 'invoice_line_ids' in vals and 'line_ids' not in vals and True or False

#        if not enable_autocomplete:
#            return False
        #fin modif
        
        vals['line_ids'] = vals.pop('invoice_line_ids')
        for invoice in self:
            invoice_new = invoice.with_context(default_move_type=invoice.move_type, default_journal_id=invoice.journal_id.id).new(origin=invoice)
            invoice_new.update(vals)
            values = invoice_new._move_autocomplete_invoice_lines_values()
            values.pop('invoice_line_ids', None)
            invoice.write(values)
        return True
 
    
 
class DiAccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    
    di_unite_categorie_name = fields.Char(string="Nom Catégorie de l'unité", related='product_uom_id.category_id.name', store=True)
    di_poids_kg = fields.Float(string='Poids en Kg')
    di_quantite_maxi = fields.Integer(string='Quantité maxi (en milliers)')
    di_quantite_mini = fields.Integer(string='Quantité mini (en milliers)')
    di_prix = fields.Monetary(string='Prix (en milliers)')
    di_prix_kg = fields.Monetary(string='Prix au Kg')
    di_nb_colis = fields.Integer(string='Nb de Colis')
    di_nb_palette = fields.Integer(string='Nb de Palettes')
    di_categ_name = fields.Char(string='Product Categ Name', related='product_id.categ_id.display_name', store=True)

    di_variete_name = fields.Char(string='Variété', related='product_id.di_variete_id.x_name', store=True)
    di_taille_name = fields.Char(string='Taille', related='product_id.di_taille_id.x_name', store=True)
    di_espece_name = fields.Char(string='Espèce', related='product_id.di_espece_id.x_name', store=True)

    
    @api.onchange('quantity','product_uom_id', 'product_id','price_unit')
    def di_compute_qte_poids(self):
        
        for line in self:
            if line.product_uom_id.category_id.name == "Poids":
                line.di_poids_kg = line.quantity
                line.di_quantite_mini = line.quantity * line.product_id.di_nb_bete_mini_kg / 1000
                line.di_quantite_maxi = line.quantity * line.product_id.di_nb_bete_maxi_kg / 1000
                line.di_prix_kg = line.price_unit 
                line.di_prix = 0
            else:    
                if line.product_id.di_nb_bete_maxi_kg !=0:
                    line.di_poids_kg = line.quantity / line.product_id.di_nb_bete_maxi_kg * 1000
                    
                else:
                    line.di_poids_kg = 0 
                    
                line.di_prix_kg = 0    
                line.di_prix = line.price_unit
                line.di_quantite_maxi = line.quantity
                line.di_quantite_mini = line.quantity
    
    
                