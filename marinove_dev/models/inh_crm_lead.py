# See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError
from dateutil.relativedelta import relativedelta
from odoo.tools.safe_eval import safe_eval


class DiCRMLead(models.Model):
    _inherit = 'crm.lead'

    @api.onchange('x_studio_transporteur_1')
    def di_default_schedule(self):
        if self.x_studio_transporteur_1:
            self.di_schedule = self.x_studio_transporteur_1.di_schedule

    
    x_studio_prix = fields.Monetary(string='Prix (en milliers)')
    x_studio_montant = fields.Monetary(string='Montant CA', store=True, readonly=True, compute='di_compute_montant')
    x_studio_prix_kg = fields.Monetary(string='Prix au Kg')#, store=True, readonly=True, compute='_compute_montant')
    x_studio_transporteur_1 = fields.Many2one('delivery.carrier', string='Transporteur', ondelete='set null')
    x_studio_n_semaine = fields.Integer(string='N° semaine')

    di_unite_categorie_name = fields.Char(string="Nom Catégorie de l'unité", related='x_studio_unite.category_id.name', store=True)
    di_state_code = fields.Char(string="Code department", related='partner_id.state_id.code', store=True)
    di_schedule= fields.Char(string="Schedule", default=di_default_schedule)

    di_opportunity_state = fields.Selection([
            ('lost', 'Perdu'),
            ('win', 'Gagné'),
            ('miss', 'Infos manquantes')], 
        string='Opportunity State',
        compute='_compute_opportunity_state', store=True
        )
    di_opportunity_color = fields.Integer('Color Opportunity', compute='_compute_opportunity_state', default=0, store=True )
    
    

    @api.depends('x_studio_prix', 'x_studio_quantit_maxi_en_milliers','x_studio_quantit_mini_en_milliers', 'x_studio_poids_kg', 'x_studio_prix_kg','x_studio_unite', 'x_studio_article')
    def di_compute_montant(self):
        for line in self:
            if line.x_studio_quantit_maxi_en_milliers < line.x_studio_quantit_mini_en_milliers:
               line.x_studio_quantit_maxi_en_milliers = line.x_studio_quantit_mini_en_milliers
               
            if line.x_studio_unite.category_id.name == "Poids":
                line.x_studio_montant = line.x_studio_prix_kg * line.x_studio_poids_kg
                
                line.x_studio_quantit_mini_en_milliers = line.x_studio_poids_kg * line.x_studio_article.di_nb_bete_mini_kg / 1000
                line.x_studio_quantit_maxi_en_milliers = line.x_studio_poids_kg * line.x_studio_article.di_nb_bete_maxi_kg / 1000
                
            else:    
                line.x_studio_montant = line.x_studio_prix * line.x_studio_quantit_maxi_en_milliers
                
                if line.x_studio_article.di_nb_bete_maxi_kg !=0:
                    line.x_studio_poids_kg = line.x_studio_quantit_maxi_en_milliers / line.x_studio_article.di_nb_bete_maxi_kg * 1000
                else:
                    line.x_studio_poids_kg = 0    

            #if line.x_studio_poids_kg and line.x_studio_poids_kg!=0:
            #    line.x_studio_prix_kg = line.x_studio_prix / line.x_studio_poids_kg
            #else:
            #    line.x_studio_prix_kg = 0    
            
            
            ##x_studio_quantit_mini_en_milliers
            #for record in self:
            #  if record['x_studio_quantit_maxi_en_milliers'] < record.x_studio_quantit_mini_en_milliers:
            #    record['x_studio_quantit_maxi_en_milliers'] = record.x_studio_quantit_mini_en_milliers
    
    
    @api.depends('stage_id', 'probability', 'x_studio_article' )
    def di_compute_opportunity_state(self):
        for record in self:
            record.di_opportunity_state = False
            record.di_opportunity_color = 0

            if record.active == True and record.stage_id.is_won == True:
               record.di_opportunity_state = 'win'
               record.di_opportunity_color = 1
               
            else:   
                if record.active == False and record.probability == 0:
                    record.di_opportunity_state = 'lost'
                    record.di_opportunity_color = 4
                   
                else:
                    if record.x_studio_article == False:    
                        record.di_opportunity_state = 'miss'
                        record.di_opportunity_color = 3
                       

    def write(self, vals):
        result = super(DiCRMLead, self).write(vals)
        for record in self:
            #if 'color' in vals:
            _color = record.color
            if record.color == 2 or record.color == 9 or record.color == 10:
                _color = 0
            if record.active == True and record.stage_id.is_won == True:
                _color = 10         # Vert
            else:   
                if (record.active == False and record.probability == 0) or (record.stage_id.name.lower().find('perdu')!=-1):
                    _color = 9      # Rouge
                else:
                    if record.x_studio_article.id == False or record.x_studio_transporteur_1.id == False or record.x_studio_date_de_dpart == False or record.x_studio_site_de_depart.id == False or record.x_studio_lieu_de_livraison == False:    
                        _color = 2  # Orange              
            vals['color'] = _color
            
        result = super(DiCRMLead, self).write(vals)
            
                                
    @api.onchange('x_studio_article')           
    def di_onchange_article(self):
        if self.x_studio_article:
            self.x_studio_varit = self.x_studio_article.di_variete_id
            self.x_studio_taille = self.x_studio_article.di_taille_id
            self.x_studio_espece = self.x_studio_article.di_espece_id
            if self.x_studio_unite:
                if self.x_studio_unite.category_id != self.x_studio_article.uom_id.category_id:
                    raise UserError(_("Please don't change the category of the unity."))

            self.x_studio_unite = self.x_studio_article.uom_id

    @api.onchange('x_studio_unite')           
    def di_onchange_unite(self):
        if self.x_studio_unite and self.x_studio_article:
            if self.x_studio_unite.category_id != self.x_studio_article.uom_id.category_id:
                raise UserError(_("Please don't change the category of the unity."))

            
    def order_opportunity(self, date_order=False, type_doc='order'):
        params = [tuple(self.ids)]
        _crm = self.filtered(lambda opp: opp.active == True and opp.type != 'lead' and opp.stage_id.name.lower().find('perdu') == -1)
        #if len(self.ids) < 1:
        if len(_crm) < 1:
            raise UserError(_('Please select element (opportunity) from the list view.'))
        
        # Test 1 seul partner_id
        nombre = 0
        query = """SELECT count(distinct partner_id) 
                FROM crm_lead cl left join crm_stage st on st.id = cl.stage_id 
                where cl.active = True and cl.type != 'lead' and lower(st.name) not like 'perdu' and cl.id in %s"""
        self._cr.execute(query, tuple(params))
        #self._cr.execute(query)
        ids_p = [(r[0]) for r in self.env.cr.fetchall()]
        
        for count_partner in ids_p:
            nombre = count_partner
        if nombre > 1:
            raise UserError(_('Please select only 1 customer.'))

        # Test 1 seule date de départ
        nombre = 0
        query = """SELECT count(distinct x_studio_date_de_dpart) 
                FROM crm_lead cl left join crm_stage st on st.id = cl.stage_id  
                where cl.active = True and cl.type != 'lead' and lower(st.name) not like 'perdu' and  cl.id in %s"""
        self._cr.execute(query, tuple(params))
        #self._cr.execute(query)
        ids_d = [(r[0]) for r in self.env.cr.fetchall()]
        
        for count_date in ids_d:
            nombre = count_date
        if nombre > 1:
            raise UserError(_('Please select only 1 date of departure.'))

        # Test 1 seul site de départ
        nombre = 0
        query = """SELECT count(distinct sl.name) 
                FROM crm_lead cl left join crm_stage st on st.id = cl.stage_id  
                left join stock_location sl on sl.id = cl.x_studio_site_de_depart
                where cl.active = True and cl.type != 'lead' and lower(st.name) not like 'perdu' and  cl.id in %s"""
        self._cr.execute(query, tuple(params))
        #self._cr.execute(query)
        ids_e = [(r[0]) for r in self.env.cr.fetchall()]
        
        for count_site in ids_e:
            nombre = count_site
        if nombre > 1:
            raise UserError(_('Please select only 1 site of departure.'))

        # Un article sur chaque ligne
        query = """SELECT  count(distinct partner_id) FROM public.crm_lead cl left join crm_stage st on st.id = cl.stage_id  
                where (cl.active = True and cl.type != 'lead' and lower(st.name) not like 'perdu' and  cl.id in %s) 
                and ((x_studio_article is null or x_studio_article=0 ) OR (x_studio_transporteur_1 is null or x_studio_transporteur_1=0) OR (x_studio_site_de_depart is null) OR (x_studio_lieu_de_livraison is null) )
                """
        self._cr.execute(query, tuple(params))
        ids_i = [(r[0]) for r in self.env.cr.fetchall()]
        
        for count_item in ids_i:
            nombre = count_item
        if nombre >= 1:
            raise UserError(_('Opportunity with no item or no carrier or no starting location or no delivery location.'))
        
        
        # catégorie unité différente
        query = """
        SELECT pt.name, pt.default_code, x_studio_article, x_studio_unite , pt.uom_id, uom_c.category_id,  uom_pt.category_id
            FROM crm_lead cl
            left join crm_stage st on st.id = cl.stage_id 
            inner join product_product pp on x_studio_article= pp.id
            inner join product_template pt on pt.id = pp.product_tmpl_id
            inner join uom_uom uom_c on x_studio_unite = uom_c.id
            inner join uom_uom uom_pt on pt.uom_id = uom_pt.id

            where cl.active = True and cl.type != 'lead' and lower(st.name) not like 'perdu' and cl.id in %s 
            AND uom_c.category_id <>  uom_pt.category_id"""

        self._cr.execute(query, tuple(params))
        ids_cat = [(r[0],r[1],r[2],r[3],r[4],r[5],r[6]) for r in self.env.cr.fetchall()]
        
        for art_name, art_code, art_idc, unit_c, unit_pt, cat_c, cat_pt in ids_cat:
            refer=" "
            if art_code:
                refer = art_code
            
            raise UserError(_('Different Unity Category for the item ' + str(art_name) + '  ' + str(refer)))

         
        order_vals_list = []
        order_lines_vals = []
        order_item_sequence = 0
        orders = {}
        vals = {}
        origins = set()
        
        # Recherche Etapes 'Gagné'
        won_stage_ids = self.env['crm.stage'].search([('is_won', '=', True)]).ids
        won_stage_id = self.env['crm.stage'].search([('is_won', '=', True)], limit=1).id

        opportunities = self.sorted(lambda o: (o.partner_id, o.id)).filtered(lambda opp: opp.active == True and opp.type != 'lead' and opp.stage_id.name.lower().find('perdu') == -1)
        for opportunity in opportunities:
            # Recherche de l'entrepôt à partir de l'emplacement de l'opportunité
            entrepot = False
            if opportunity.x_studio_site_de_depart.id:
                query_args = {'id_location' : int(opportunity.x_studio_site_de_depart.id)}
                query = """ SELECT sw.id, sw.name, sl1.id, sl1.name, sl1.parent_path, sl2.id, sl2.name, sl2.parent_path
                        FROM public.stock_location sl1
                        INNER JOIN public.stock_location sl2 on sl1.location_id = sl2.id
                        INNER JOIN  public.stock_warehouse sw on sl2.location_id = sw.view_location_id
                        where sl1.id= %s """ % int(opportunity.x_studio_site_de_depart.id)
                self._cr.execute(query)
                ids_w = [(r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7]) for r in self.env.cr.fetchall()]
        
                for warehouse_id, warehouse_name, loc1_id, loc1_name, loc1_path, loc1_id, loc1_name, loc1_path in ids_w:
                    entrepot = warehouse_id
                        
            if order_item_sequence == 0:
                order_vals = {
                    'date_order': date_order,     
                    'partner_id': opportunity.partner_id.id,
                    'fiscal_position_id': opportunity.partner_id.property_account_position_id.id or False,
                    'payment_term_id': opportunity.partner_id.property_payment_term_id.id or False,
                    'user_id': opportunity.partner_id.user_id.id or False,
                    'team_id': opportunity.team_id.id or False,
                    'campaign_id': opportunity.campaign_id.id or False,
                    'medium_id': opportunity.medium_id.id or False,
                    'company_id': opportunity.company_id.id or opportunity.env.company.id,
                    'tag_ids': [(6, 0, opportunity.tag_ids.ids)],
            
                    'origin': opportunity.name,
                    'opportunity_id': opportunity.id,
                    'source_id': opportunity.source_id.id or False,
                    'carrier_id': opportunity.x_studio_transporteur_1.id or False,
                    'warehouse_id': entrepot or False,
                    'expected_date': opportunity.x_studio_date_de_livraison_prvue or False,
                    'commitment_date': opportunity.x_studio_date_de_dpart or False,
                    'di_lieu_livraison_1': opportunity.x_studio_lieu_de_livraison or False,
                    'di_schedule': opportunity.di_schedule or False,
                    'x_studio_n_semaine_1': opportunity.x_studio_n_semaine or False,
                    'di_date_depart': opportunity.x_studio_date_de_dpart or False,
                    'di_comment': opportunity.description or False,
                    }
                origins.add(order_vals['origin'])
                
                # Si client de type Prospect
                #if opportunity.partner_id.ref:
                refer = opportunity.partner_id.ref or 'P'
                if refer[:1] == "P" or refer == False:
                        # recherche dernier code client
                        sql_p = """SELECT max(ref) FROM res_partner WHERE ref like 'C%' """
                        self.env.cr.execute(sql_p)
                        ids_p = [(r[0]) for r in self.env.cr.fetchall()]
                        for ref in ids_p:
                            ref_no = ref[-5:]
                            new_no = int(ref_no) + 1
                            new_ref = "000000" + str(new_no)
                            new_ref_C = "C" + new_ref[-5:]
                        
                        partner = self.env['res.partner'].browse(opportunity.partner_id.id)
                        partner.update({'ref': new_ref_C})
                
            elif order_item_sequence > 0:
                    origins.add(opportunity.name)        #origins.add(order_vals['origin'])
                    
                    order_vals.update({
                    'opportunity_id': False,
                    #'origin': ', '.join(origins),
                    
                    })
                    #order_vals['origin'] = order_vals['origin']  + ', ' + opportunity.name
                    #order_vals['opportunity_id'] = False
                    
            # Lignes articles
            order_item_sequence += 1
            unite = opportunity.x_studio_unite.id or opportunity.x_studio_article.uom_id  or False
            cat_unite = "unite"
                        
            if opportunity.x_studio_unite:
               cat_unite =  opportunity.x_studio_unite.category_id.name
            elif opportunity.x_studio_article.uom_id:
                cat_unite =  opportunity.x_studio_article.uom_id.category_id.name   
            
            if opportunity.partner_id.lang:
                product = opportunity.x_studio_article.with_context(lang=opportunity.partner_id.lang)
            else:
                product = opportunity.x_studio_article
            
            
            prepared_line = {
            'display_type': False,
            'sequence': order_item_sequence,
            #'name': opportunity.x_studio_article.name or False,  #opportunity.name
            'name': product.name or False,
            'product_id': opportunity.x_studio_article.id or False,
            'product_uom': opportunity.x_studio_unite.id or opportunity.x_studio_article.uom_id.id  or False,
            'product_uom_qty': opportunity.x_studio_quantit_maxi_en_milliers or 0,
            'price_unit': opportunity.x_studio_prix or 0,
            'di_quantite_maxi': opportunity.x_studio_quantit_maxi_en_milliers or 0,
            'di_quantite_mini': opportunity.x_studio_quantit_mini_en_milliers or 0,
            'di_poids_kg': opportunity.x_studio_poids_kg or 0,
            'di_lieu_livraison': opportunity.x_studio_lieu_de_livraison or False,
            'di_schedule': opportunity.di_schedule or False,
            'di_warehouse_id': opportunity.x_studio_site_de_depart.id or False,
            'di_carrier_id': opportunity.x_studio_transporteur_1.id or False,
            'di_prix': opportunity.x_studio_prix or 0,
            'di_prix_kg': 0,
            'di_comment': opportunity.description or False,
            }
            
            #if opportunity.x_studio_unite.category_id.name == "Poids":
            if cat_unite == "Poids":
                prepared_line['product_uom_qty'] = opportunity.x_studio_poids_kg or 0
                prepared_line['price_unit'] = opportunity.x_studio_prix_kg or 0
                prepared_line['di_prix_kg'] = opportunity.x_studio_prix_kg or 0
                prepared_line['di_prix'] =  0
            
            if not opportunity.x_studio_article: 
                prepared_line['display_type'] = 'line_note'     # Ne doit pas se produire : test au préalable
                
            order_lines_vals.append(prepared_line)
            
            # MAJ de l'opportunité : stage_id = Gagné
            #if opportunity.stage_id.id != won_stage_id:
            opportunity.update({'stage_id' : won_stage_id, 'probability': 100, 'automated_probability': 100, 'date_closed' : fields.Datetime.now(), 'active':False  })
            
        # Write in Sale_order
        order_vals['order_line'] = [(0, 0, order_line_id) for order_line_id in order_lines_vals]
        order_vals_list.append(order_vals)
        if type_doc == 'order':
            sale_orders = self.env['sale.order'].sudo().with_context(default_state='sale').create(order_vals_list)    
        else:
            sale_orders = self.env['sale.order'].sudo().with_context(default_state='draft').create(order_vals_list)
            
        # Add delivery line
        
        for new_order in sale_orders:
            new_order._remove_delivery_line()
            # search carrier
            id_order =  new_order.id
            query_args = {'id_order' :id_order}
            query = """SELECT  distinct di_carrier_id FROM sale_order_line where  order_id = %(id_order) and di_carrier_id is not null """
            #self._cr.execute(query, query_args)
            self._cr.execute("SELECT  distinct di_carrier_id FROM sale_order_line where  order_id = %s and (di_carrier_id is not null or  di_carrier_id != 0)" % int(new_order.id))
            #self._cr.execute(query, (tuple(new_order.id),))
            ids_c = [(r[0]) for r in self.env.cr.fetchall()]
        
            for carrier_line in ids_c:
                carrier = self.env['delivery.carrier'].browse(carrier_line)
                #if carrier.delivery_type == "fixed":
                #    price = carrier.fixed_price
                #else: 
                total_line = total = weight = volume = quantity = 0
                total_delivery = 0.0
                
                for line in new_order.order_line.filtered(
                    lambda x: x.di_carrier_id.id == carrier_line):
                    if line.state == 'cancel':
                        continue
                    if line.is_delivery:
                        total_delivery += line.price_total
                    if not line.product_id or line.is_delivery:
                        continue
                    #qty = line.product_uom._compute_quantity(line.product_uom_qty, line.product_id.uom_id)
                    #weight += (line.product_id.weight or 0.0) * qty
                    qty = (line.di_quantite_maxi or 0.0)
                    weight += (line.di_poids_kg or 0.0) 
                    volume += (line.product_id.volume or 0.0) * qty
                    quantity += (line.di_quantite_maxi or 0.0)
                    total_line += (line.price_total or 0.0)

                #total = (new_order.amount_total or 0.0) - total_delivery
                total = total_line - total_delivery
                total = new_order.currency_id._convert(
                total, new_order.company_id.currency_id, new_order.company_id, new_order.date_order or fields.Date.today())
   
                price = 0.0
                price_dict = {'price': total, 'volume': volume, 'weight': weight, 'wv': volume * weight, 'quantity': quantity}
                if carrier.free_over and total >= carrier.amount:
                    price = 0.0
                else:   
                    if carrier.delivery_type == "fixed":
                        price = carrier.fixed_price
                    else:     
                        for line in carrier.price_rule_ids:
                            test = safe_eval(line.variable + line.operator + str(line.max_value), price_dict)
                            if test:
                                price = line.list_base_price + line.list_price * price_dict[line.variable_factor]
                               
                
                
                if price != 0.0:
                    company =new_order.company_id or False
                    if company.currency_id and company.currency_id != new_order.currency_id:
                        price = company.currency_id._convert(price, new_order.currency_id, company, fields.Date.today())

                    new_order._create_delivery_line(carrier, price)
        
            # Modification de l'emplacement dans les lignes du bon de livraison : stock.move.line
            self.env.cr.commit()
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
        return sale_orders
    
    def action_create_sale_order(self):
        if not self.partner_id:
            return self.env["ir.actions.actions"]._for_xml_id("sale_crm.crm_quotation_partner_action")
        else:
            order_opportunity = self.order_opportunity(fields.Date.context_today(self), 'order')
            
            action = self.env.ref('sale.action_orders').read()[0]   
            #order_ids = order_opportunity.ids
            #order = order_opportunity.ids[0]
            action['res_id'] = order_opportunity.ids[0]
            action['view_mode'] = 'form'
            form_view = [(self.env.ref('sale.view_order_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
        
            return action  
    
    def action_sale_quotations_new(self):
        if not self.partner_id:
            return self.env["ir.actions.actions"]._for_xml_id("sale_crm.crm_quotation_partner_action")
        else:
            order_opportunity = self.order_opportunity(fields.Date.context_today(self), 'quotation')
    
            action = self.env.ref('sale.action_quotations_with_onboarding').read()[0]   
            
            action['res_id'] = order_opportunity.ids[0]
            action['view_mode'] = 'form'
            form_view = [(self.env.ref('sale.view_order_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
        
            return action  
    
    
    def action_new_quotation(self):
        return self.order_opportunity(fields.Date.context_today(self))
