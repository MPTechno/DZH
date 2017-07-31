from odoo import models, fields, api

class sales_cancel_report(models.TransientModel):
    _name='sales.cancel.report'

    country = fields.Many2one('res.country','Country')
    sales_person = fields.Many2one('res.users','Sales Person')
    start_date = fields.Date(String="Start Date", required = True)
    end_date = fields.Date(String="End Date", required = True)
    invoice_refund_ids = fields.Many2many('account.invoice')
    country_ids = fields.Many2many('res.country')
    # currency_ids = fields.Many2many('res.currency.rate')
    product_ids = fields.Many2many('account.invoice.line')

    @api.multi
    def print_report(self):
        self.ensure_one()
        data = {
            'ids': self.ids,
            'model': 'sales.cancel.report',
            'from': self.read(['start_date', 'end_date', 'country', 'sales_person'])[0]
        }
        conditions = [('type','=','out_refund')]
        if data['from']['start_date']:
            conditions.append(('date_invoice', '>=', data['from']['start_date']))
        if data['from']['end_date']:
            conditions.append(('date_invoice', '<=', data['from']['end_date']))
        if data['from']['sales_person']:
            conditions.append(('user_id', '=', data['from']['sales_person'][0]))
        if data['from']['country']:
            partner_ids = self.env['res.partner'].search([('country_id','=',data['from']['country'][0])])._ids
            conditions.append(('partner_id','in',partner_ids))
            self.country_ids = self.env['res.country'].browse(data['from']['country'][0])
        self.invoice_refund_ids = self.env['account.invoice'].search(conditions,order='create_date asc')
        if not data['from']['country']:
            country_ids = []
            for invoice in self.invoice_refund_ids:
                if invoice.partner_id.country_id.id:
                    esixt = False
                    for item in country_ids:
                        if item == invoice.partner_id.country_id.id:
                            esixt = True
                    if not esixt:
                        country_ids.append(invoice.partner_id.country_id.id)
            self.country_ids = self.env['res.country'].browse(country_ids)
        # self.currency_ids = self.env['res.currency.rate'].search([])
        self.product_ids = self.env['account.invoice.line'].search([])
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'sales_cancellation_report_reusable.sales_cancel_report',
        }

