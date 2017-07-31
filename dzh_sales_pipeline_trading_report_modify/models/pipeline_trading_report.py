import math
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api
from datetime import datetime, timedelta

class pipeline_trading(models.TransientModel):
    _name = 'pipeline.trading.report'

    start_date = fields.Date()
    end_date = fields.Date()
    country_id = fields.Many2one(comodel_name='res.country')
    user_id = fields.Many2one(comodel_name='res.users')
    pipeline_ids = fields.Many2many('crm.lead')
    country_ids = fields.Many2many('res.country')
    date_filter = ['']

    @api.multi
    def print_trading_report(self, context=None):
        self.ensure_one()

        data = {
            'ids': self.ids,
            'model': 'pipeline.trading.report',
            'from': self.read(['start_date', 'end_date', 'country_id', 'user_id'])[0]
        }
        # condition for all table
        conditions = []
        conditions.append(('invoice_type', 'in', ('trading_gts','trading_dzh')))
        conditions.append(('market_segment_id', '=', 'Corporate Retail'))

        if data['from']['start_date']:
            conditions.append(('create_date', '>=', data['from']['start_date']))
        if data['from']['end_date']:
            conditions.append(('create_date', '<=', data['from']['end_date']))
        if data['from']['country_id']:
            partner_ids = self.env['res.partner'].search([('country_id', '=', data['from']['country_id'][0])])._ids
            conditions.append(('partner_id', 'in', partner_ids))
            self.country_ids = self.env['res.country'].browse(data['from']['country_id'][0])
        if data['from']['user_id']:
            conditions.append(('user_id', '=', data['from']['user_id'][0]))

        self.date_filter[0] = 'Potential Revenue as at {}'.format(datetime.strptime(data['from']['end_date'], "%Y-%m-%d").strftime("%d %b %Y"))
        self.pipeline_ids = self.env['crm.lead'].search(conditions)
        if not data['from']['country_id']:
            country_id = []
            country_id.append(self.env['res.country'].search([('code','=','SG')]).id)
            if self.pipeline_ids and self.pipeline_ids.ids:
                for id in self.pipeline_ids:
                    if id.partner_id.country_id.id:
                        esixt = False
                        for item in country_id:
                            if item == id.partner_id.country_id.id:
                                esixt = True
                        if not esixt:
                            country_id.append(id.partner_id.country_id.id)
            self.country_ids = self.env['res.country'].browse(country_id)

        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'dzh_sales_pipeline_trading_report_modify.pipeline_trading_report',
        }
