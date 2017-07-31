from odoo import models, fields, api

class month_id_report(models.TransientModel):
    _name='ipt.month.id.report'

    country = fields.Many2one('res.country','Country')
    start_date = fields.Date(String="Start Date", required = True)
    end_date = fields.Date(String="End Date", required = True)
    user_ids = fields.Many2many('dzh.partner.user')
    customer_ids = fields.Many2many('res.partner')
    country_ids = fields.Many2many('res.country')
    market_segment_ids = fields.Many2many('market.segment')

    @api.multi
    def print_report(self):
        self.ensure_one()
        data = {
            'ids': self.ids,
            'model': 'ipt.month.id.report',
            'from': self.read(['start_date', 'end_date', 'country'])[0]
        }
        conditions = [('customer','=',True)]
        if data['from']['start_date']:
            conditions.append(('create_date', '>=', data['from']['start_date']))
        if data['from']['end_date']:
            conditions.append(('create_date', '<=', data['from']['end_date']))
        if data['from']['country']:
            partner_ids = self.env['res.partner'].search([('country_id','=',data['from']['country'][0])])._ids
            conditions.append(('id','in',partner_ids))
            self.country_ids = self.env['res.country'].browse(data['from']['country'][0])
        self.customer_ids = self.env['res.partner'].search(conditions)
        if not data['from']['country']:
            country_ids = []
            for customer in self.customer_ids:
                if customer.country_id.id:
                    esixt = False
                    for item in country_ids:
                        if item == customer.country_id.id:
                            esixt = True
                    if not esixt:
                        country_ids.append(customer.country_id.id)
            self.country_ids = self.env['res.country'].browse(country_ids)
        self.user_ids = self.env['dzh.partner.user'].search([('dzh_partner_id','in',self.customer_ids._ids)])
        self.market_segment_ids = self.env['market.segment'].search([])

        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'ipt_month_id_report_modify.ipt_month_id_report_modify',
        }

