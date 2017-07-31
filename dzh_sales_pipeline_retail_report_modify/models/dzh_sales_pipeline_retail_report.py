from odoo import models, fields, api

class sale_pipeline_retail(models.TransientModel):
    _name='sale.pipeline.retail.report'

    country = fields.Many2one('res.country', 'Country')
    sales_person = fields.Many2one('res.users', 'Sales Person')
    start_date = fields.Date(String="Start Date", required = True)
    end_date = fields.Date(String="End Date", required = True)
    invoice_ids = fields.Many2many('account.invoice')
    product_ids = fields.Many2many('account.invoice.line')
    country_ids = fields.Many2many('res.country')


    @api.multi
    def print_report(self):
        self.ensure_one()
        data = {
            'ids': self.ids,
            'model': 'ipt.month.id.report',
            'from': self.read(['start_date', 'end_date', 'sales_person','country'])[0]
        }
        conditions = []
        if data['from']['start_date']:
            conditions.append(('create_date', '>=', data['from']['start_date']))
        if data['from']['end_date']:
            conditions.append(('create_date', '<=', data['from']['end_date']))
        if data['from']['sales_person']:
            conditions.append(('user_id','=',data['from']['sales_person'][0]))
        if data['from']['country']:
            partner_ids = self.env['res.partner'].search([('country_id','=',data['from']['country'][0])])._ids
            conditions.append(('partner_id','in',partner_ids))
            self.country_ids = self.env['res.country'].browse(data['from']['country'][0])
        market_segment_retail = self.env['market.segment'].search([('name','=','Retail')])
        partner_ids = self.env['res.partner'].search([('market_segment_id','=',market_segment_retail.id)])
        conditions.append(('partner_id','in',partner_ids._ids))
        self.invoice_ids = self.env['account.invoice'].search(conditions)

        if not data['from']['country']:
            country_ids = []
            country_ids.append(self.env['res.country'].search([('code','=','SG')]).id)
            for invoice in self.invoice_ids:
                if invoice.partner_id.country_id.id:
                    esixt = False
                    for item in country_ids:
                        if item == invoice.partner_id.country_id.id:
                            esixt = True
                    if not esixt:
                        country_ids.append(invoice.partner_id.country_id.id)
            self.country_ids = self.env['res.country'].browse(country_ids)
        self.product_ids = self.env['account.invoice.line'].search([('invoice_id','in',self.invoice_ids._ids)])

        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'dzh_sales_pipeline_retail_report_modify.sale_pipeline_retail_report',
        }

