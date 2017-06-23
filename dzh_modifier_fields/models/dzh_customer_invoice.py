# -*- coding: utf-8 -*-
from odoo import fields, models, api
from datetime import datetime, timedelta


class account_invoice(models.Model):
    _inherit = 'account.invoice'

    @api.depends('x_subscription_period', 'x_month_number')
    def compute_end_date(self):
        if not self.x_subscription_period:
            return
        month = self.x_month_number or 0
        start = datetime.strptime(self.x_subscription_period, '%Y-%m-%d')
        add_month = month % 12
        add_years = int(month / 12) + (int(start.month) + add_month) / 12
        end_month = (int(start.month) + add_month) % 12 if (int(start.month) + add_month) / 12 > 0  else int(
            start.month) + add_month
        end_year = start.year + add_years
        end_day = start.day
        while True:
            end_format = '%s-%s-%s' % (end_year, end_month, end_day)
            try:
                self.x_end_date = datetime.strptime(end_format, '%Y-%m-%d')
                break
            except:
                end_day -= 1

    @api.onchange('partner_id')
    def onchange_partner_id_sale_order(self):
        if self.partner_id and self.partner_id.id:
            if self.invoice_line_ids and len(self.invoice_line_ids) > 0:
                self.invoice_line_ids.write({'partner_from_io': self.partner_id.id})
        return

    x_subscription_period = fields.Date('Subscription Period', default=fields.Datetime.now)
    x_end_date = fields.Date("End Date", compute=compute_end_date)
    x_contact_term = fields.Text('Contract Term')
    x_month_number = fields.Integer('Number of Month', default=0)
    cr_number = fields.Text('CR Number')


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"
    
    account_user_id = fields.Many2many("dzh.partner.user",id1='invoice_line_id', id2='account_user_id', string="User ID")
    subscription_period = fields.Date('Subscription Period')
    start_date = fields.Datetime("Start Date" , default=fields.Datetime.now)
    end_date = fields.Datetime("End Date" , default=fields.Datetime.now)
    partner_from_io = fields.Many2one('res.partner', string='Partner ID')

    @api.model
    def default_get(self, fields):
        res = super(AccountInvoiceLine, self).default_get(fields)
        if self._context.get('invoice_order_partner_id', False):
            res['partner_from_io'] = self._context.get('invoice_order_partner_id', False)
        return res

