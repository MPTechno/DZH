# -*- coding: utf-8 -*-

import math
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
from odoo import models, fields, api

class sales_pipeline_institutional_report(models.TransientModel):
    _name='sales.pipeline.conference.education.report'

    country = fields.Many2one('res.country', 'Country')
    currency = fields.Many2one('res.currency', 'Currency')
    sales_person = fields.Many2one('res.users', 'Sales Person')
    start_date = fields.Date(String="Start Date", required=True)
    end_date = fields.Date(String="End Date", required=True)
    invoice_ids = fields.Many2many('crm.lead')
    invoice_filter = [{}]
    date_filter = ['']

    @api.multi
    def print_report(self):
        self.ensure_one()

        data = {
            'ids': self.ids,
            'model': 'sales.pipeline.conference.education.report',
            'from': self.read(['start_date', 'end_date', 'country', 'sales_person'])[0]
        }

        conditions = [
            ('create_date', '>=', data['from']['start_date']),
            ('create_date', '<=', data['from']['end_date']),
            ('invoice_type', '=', 'event'),
        ]

        if data['from']['sales_person']:
            conditions.append(('user_id', '=', data['from']['sales_person'][0]))
        if data['from']['country']:
            partner_ids = self.env['res.partner'].search([('country_id', '=', data['from']['country'][0])])._ids
            conditions.append(('partner_id', 'in', partner_ids))

        self.date_filter[0] = 'Potential Revenue as at {}'.format(datetime.strptime(data['from']['end_date'], "%Y-%m-%d").strftime("%d %b %Y"))
        self.invoice_ids = self.env['crm.lead'].search(conditions, order='create_date asc')

        self.currency = self.env['res.currency'].search([('name','=','SGD')])
        self.invoice_filter[0] = {}
        for invoice in self.invoice_ids:
            if invoice.partner_id and invoice.partner_id.country_id:
                if invoice.partner_id.country_id.name in self.invoice_filter[0]:
                    self.invoice_filter[0][invoice.partner_id.country_id.name]['ids'].append(invoice.id)
                else:
                    self.invoice_filter[0][invoice.partner_id.country_id.name] = {
                        'ids': [invoice.id],
                    }

            return {
            'type': 'ir.actions.report.xml',
            'report_name': 'dzh_sales_conference_education_pipeline.sale_pipeline_conference_education_report',
        }

