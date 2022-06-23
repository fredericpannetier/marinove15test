# See LICENSE file for full copyright and licensing details.
from odoo import http, _
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.exceptions import AccessError, MissingError
from collections import OrderedDict
from odoo.http import request


class DiPortalAccount(CustomerPortal):
    
    @http.route(['/my/invoices', '/my/invoices/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_invoices(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, **kw):
        values = super().portal_my_invoices(page, date_begin, date_end, sortby, filterby,**kw)
        lines = values.qcontext['invoices']
        lines = [i for i in lines if i.state != 'draft' and i.state != 'cancel']
        values.qcontext['invoices'] = lines
        return values
