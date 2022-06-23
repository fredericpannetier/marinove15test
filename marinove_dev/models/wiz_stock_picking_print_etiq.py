from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class wizard_stock_picking_print_etiq(models.Model):
    _name = "wiz_stock_picking_print_etiq"
    _description = "Wizard to print label from stock picking"
    
    move_id = fields.Integer(string="Move id")
    move_name = fields.Char(string="Move name") #stock.picking name
    move_line_id = fields.Integer(string="Line id")
    product_name = fields.Char(string="Product name")
    etiquette_qty = fields.Integer(string="Qty of etiquettes")
    location_n1_mention = fields.Char(string="Upper location")
    location_n_mention = fields.Char(string="Location")
    deliv_mention = fields.Char(string="Carrier")
    customer_name = fields.Char(string="Customer name")
    contact_name = fields.Char(string="Contact name")
    contact_mobile = fields.Char(string="Contact mobile phone")
    address_street = fields.Char(string="Address street")
    address_cp = fields.Char(string="Address postal code")
    address_ville = fields.Char(string="Address city")
    variete_name = fields.Char(string="Variety name")
    calibre_name = fields.Char(string="Caliber name")
    location_sanit_pays = fields.Char(string="Location country")
    location_sanit = fields.Char(string="Location sanitary number")
    espece_name = fields.Char(string="Species name")
    categ_mention = fields.Char(string="Category")
    printer_id = fields.Many2one("di.printing.printer", string='Etiquette Printer', domain=[('isimpetiq', '=', True)])
    model_id = fields.Many2one("di.printing.etiqmodel", string='Etiquette Model')
    conservation = fields.Char(string="Conservation")
    
    def delete_table_temp(self, user):
        query = "DELETE FROM wiz_stock_picking_print_etiq WHERE create_uid=" + str(user)
        self.env.cr.execute(query)
        
    def load_stock_picking(self, picking_ids):
        user = self.env.user.id
        self.delete_table_temp(user)

        context = dict(self._context or {})
        #active_ids = context.get('active_ids', []) or self._ids or []
        active_ids = picking_ids

        self.env.cr.commit()
        list_move_ids = []
        
        for sp in self.env['stock.picking'].sudo().browse(active_ids):
            partadr = sp.partner_id
            if partadr.type == 'delivery':
                partcust = partadr.parent_id
            else:
                partcust = partadr
            if partadr.mobile:
                tel = partadr.mobile
            elif partadr.phone:
                tel = partadr.phone
            elif partcust.mobile:
                tel = partcust.mobile
            elif partcust.phone:
                tel = partcust.phone
            else:
                tel = ''
            if partadr.country_id.di_etiq_mention:
                conservation = partadr.country_id.di_etiq_mention
            elif partcust.country_id.di_etiq_mention:
                conservation = partcust.country_id.di_etiq_mention
            elif partcust.property_account_position_id.di_etiq_mention:
                conservation = partcust.property_account_position_id.di_etiq_mention
            else:
                conservation = ''
            
            for sml in sp.move_line_ids_without_package:
                empl = sml.location_id
                model_id = empl.di_etiq_model.id
                
                if sml.location_id.location_id is False:
                    n1_mention = empl.di_etiq_mention
                else:
                    n1_mention = empl.location_id.di_etiq_mention
                prod = sml.product_id
                if prod.categ_id.di_etiq_mention:
                    categ_mention = prod.categ_id.di_etiq_mention
                else:
                    categ_mention = prod.categ_id.name
                if prod.di_etiq_model: 
                    model_id = prod.di_etiq_model.id
                order_line = sml.move_id.sale_line_id
                    
                insert = {
                    'move_id': sp.id,
                    'move_name': sp.name,
                    'move_line_id': order_line,
                    'product_name': prod.name,
                    'etiquette_qty': 0,
                    'location_n_mention': empl.di_etiq_mention,
                    'location_n1_mention': n1_mention,
                    'deliv_mention': sp.carrier_id.di_etiq_mention,
                    'customer_name': partcust.name,
                    'contact_name': partadr.name,
                    'contact_mobile': tel,
                    'address_street': partadr.street,
                    'address_cp': partadr.zip,
                    'address_ville': partadr.city,
                    'variete_name': prod.di_variete_id.x_name,
                    'calibre_name': prod.di_taille_id.x_name,
                    'location_sanit_pays': empl.di_sanit_pays,
                    'location_sanit': empl.di_sanit,
                    'espece_name': prod.di_espece_id.x_name,
                    'categ_mention': categ_mention,
                    'printer_id': empl.di_etiq_printer.id,
                    'model_id': model_id,
                    'conservation': conservation,
                }
                prepare_print_etiq = self.env['wiz_stock_picking_print_etiq'].create(insert)
                list_move_ids.append(int(prepare_print_etiq.id))
                
        self.env.cr.commit()
        return list_move_ids
    
    def update_wiz_table(self):
        line_id = getattr(self, '_origin', self)._ids[0]
        etiquette_qty = self.etiquette_qty
        location_n_mention = self.location_n_mention
        deliv_mention = self.deliv_mention
        printer_id = self.printer_id.id
        model_id = self.model_id.id

        req = """UPDATE wiz_stock_picking_print_etiq SET 
                    etiquette_qty=%s,
                    location_n_mention=%s,
                    deliv_mention=%s """

        params = (etiquette_qty, location_n_mention, deliv_mention)

        if printer_id:
            req += ",printer_id=" + str(printer_id) + " "

        if model_id:
            req += ",model_id=" + str(model_id) + " "

        req += "WHERE id='" + str(line_id) + "' "

        self._cr.execute(req, params)
        self.env.cr.commit()

    @api.onchange('etiquette_qty', 'location_n_mention', 'deliv_mention', 'printer_id', 'model_id')
    def _onchange_order_line_print_etiq(self):
        self.update_wiz_table()
        
    def print_etiq_from_picking(self):
        self.env.cr.commit()
        
        wiz_ids = self.env['wiz_stock_picking_print_etiq'].browse(self._context.get('active_ids', []))
        for wiz in wiz_ids:
            if wiz.etiquette_qty > 0 and wiz.printer_id and wiz.model_id:
                informations = [
                    ('sale_ordername', wiz.move_name),
                    ('saleline_id', wiz.move_line_id),
                    ('saleline_qty', int(wiz.etiquette_qty)),
                    ('move_name', wiz.move_name),
                    ('product_name', wiz.product_name),
                    ('etiquette_qty',int(wiz.etiquette_qty)),
                    ('location_n_mention', wiz.location_n_mention),
                    ('location_n1_mention', wiz.location_n1_mention),
                    ('deliv_mention', wiz.deliv_mention),
                    ('customer_name', wiz.customer_name),
                    ('contact_name', wiz.contact_name),
                    ('contact_mobile', wiz.contact_mobile),
                    ('address_street', wiz.address_street),
                    ('address_cp', wiz.address_cp),
                    ('address_ville', wiz.address_ville),
                    ('variete_name', wiz.variete_name),
                    ('calibre_name', wiz.calibre_name),
                    ('location_sanit_pays', wiz.location_sanit_pays),
                    ('location_sanit', wiz.location_sanit),
                    ('espece_name', wiz.espece_name),
                    ('categ_mention', wiz.categ_mention),
                    ('conservation', wiz.conservation),
                ]
                printerName = wiz.printer_id.name
                labelName = wiz.model_id.name
                self.env['di.printing.printing'].printetiquetteonwindows(printerName,labelName,'[',']',informations)
        
        