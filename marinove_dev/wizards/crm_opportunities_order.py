# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class OpportunityDevis(models.TransientModel):
    """
        Create order from opportunities.
    """

    _name = 'wiz.opportunity.order'
    _description = 'Create Orders from Opportunities'

    @api.model
    def default_get(self, fields):
        """ Use active_ids from the context to fetch the leads/opps to order.
            In order to get merged, these leads/opps can't be in 'Dead' or 'Closed'
        """
        record_ids = self._context.get('active_ids')
        result = super(OpportunityDevis, self).default_get(fields)

        if record_ids:
            if 'opportunity_ids' in fields:
                opp_ids = self.env['crm.lead'].browse(record_ids).filtered(lambda opp: opp.probability > 0).ids
                result['opportunity_ids'] = [(6, 0, opp_ids)]

        return result

    #opportunity_ids = fields.One2many('crm.lead', 'id', string='Leads/Opportunities', copy=True, auto_join=True)
    opportunity_ids = fields.Many2many('crm.lead', 'wiz_opportunity_rel', 'merge_id', 'opportunity_id', string='Leads/Opportunities')
    date_order = fields.Datetime('Date Order', default=lambda self: fields.Date.today())
    

    def action_create_order(self):
        self.ensure_one()
        
        order_opportunity = self.opportunity_ids.order_opportunity(self.date_order, 'order')
        
        action = self.env.ref('sale.action_orders').read()[0]   #     sale.action_orders  // sale.action_quotations_with_onboarding
        #order_ids = order_opportunity.ids
        if len( order_opportunity.ids) == 1:
            #order =  order_ids[0]
            action['res_id'] = order_opportunity.ids[0]
            action['view_mode'] = 'form'
            form_view = [(self.env.ref('sale.view_order_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
        else:
            action['domain'] = [('id', 'in', order_opportunity.ids)]
            #action['view_id'] = 'sale.order.form'
            action['view_mode'] = 'form'
       
        return action  
    
    def action_create_quotation(self):
        self.ensure_one()
        
        order_opportunity = self.opportunity_ids.order_opportunity(self.date_order, 'quotation')
        
        action = self.env.ref('sale.action_quotations_with_onboarding').read()[0]   
       
        if len( order_opportunity.ids) == 1:
            #order =  order_ids[0]
            action['res_id'] = order_opportunity.ids[0]
            action['view_mode'] = 'form'
            form_view = [(self.env.ref('sale.view_order_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
        else:
            action['domain'] = [('id', 'in', order_opportunity.ids)]
            action['view_mode'] = 'form'
       
        return action  
