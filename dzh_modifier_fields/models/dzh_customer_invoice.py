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
    user_send_mail = fields.Char(default="")

    @api.model
    def send_mail_notification(self):
        day_after = (datetime.now()+timedelta(days = 30)).strftime('%Y-%m-%d')
        day_after = datetime.strptime(day_after,'%Y-%m-%d')
        invoice_ids = self.env['account.invoice'].search([])
        invoice = []
        for invoice_id in invoice_ids:
            invoice_id.compute_end_date()
            if invoice_id.x_end_date:
                x_end_day = datetime.strptime(invoice_id.x_end_date,'%Y-%m-%d')
                if  x_end_day == day_after:
                    invoice.append(invoice_id.id)
        invoice_need_send_mail = self.env['account.invoice'].search([('id','in',invoice)])
        if invoice_need_send_mail:
            for invoice_send_mail in invoice_need_send_mail:
                self.send_mail(invoice_send_mail.user_id,invoice_send_mail)
                user_ids = self.env['res.users'].search([])
                for user_id in user_ids:
                    if user_id.re_notification or user_id.support_email:
                        self.send_mail(user_id, invoice_send_mail)

    def send_mail(self,user_id,invoice):
        email_from = invoice.company_id.email or 'Administrator <admin@example.com>'
        email_to = user_id.email
        subject = 'Subscription End Date of Invoices'
        # message = """
        #     <html>
        #         <body>
        #             <p>Dear %s,<br><br>
        #                 This invoice is approaching Subscription End Date in 1 month.<br>
        #                 Invoice : %s<br>
        #                 Sales Person : %s<br>
        #                 Subscription End Date : %s<br><br>
        #
        #                 Regards,<br>
        #                 DZH International
        #              </p>
        #         </body>
        #     </html>""" % (user_id.name,invoice.number,invoice.user_id.name,invoice.x_end_date)

        message = """
        <html>
            <body>
				<div style="font-family: 'Lucida Grande', Ubuntu, Arial, Verdana, sans-serif; font-size: 12px; color: rgb(34, 34, 34); background-color: #FFF; ">
					<p style="margin-left: 40px;">Dear %s,</p>

					<p style="border-left: 1px solid #8e0000; margin-left: 30px;">
					    <span style="margin-left: -130px;">
                           <strong>This invoice is approaching Subscription End Date in 1 month.</strong><br/>
                           Invoice: <strong>%s</strong><br/>
                           Sales Person: <strong>%s</strong><br/>
                           Subscription End Date: <strong>%s</strong><br/>
					    </span>
					</p>
					<br/>
					<span style="margin-left: -80px;">Regards,</span><br/>
					<span style="margin-left: -80px;"><strong>DZH International</strong></span>
				</div>
		    </body>
		<html>"""% (user_id.name,invoice.number,invoice.user_id.name,invoice.x_end_date)

        vals = {
            'state': 'outgoing',
            'subject': subject,
            'body_html': '<pre>%s</pre>' % message,
            'email_to': email_to,
            'email_from': email_from,
        }
        if vals:
            email_exist = False
            if invoice.user_send_mail:
                user_send_mails = invoice.user_send_mail.split('-')
                for user_send_mail in user_send_mails:
                    if int(user_send_mail) == user_id.id:
                        email_exist = True
            if not email_exist:
                email_id = self.env['mail.mail'].create(vals)
                if email_id:
                    email_id.send()
                    if invoice.user_send_mail:
                        user_send_mail = invoice.user_send_mail + '-' + str(user_id.id)
                    else:
                        user_send_mail = str(user_id.id)
                    invoice.write({'user_send_mail':user_send_mail})



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

