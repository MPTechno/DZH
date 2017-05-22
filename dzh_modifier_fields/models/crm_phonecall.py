# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class CrmPhonecall(models.Model):
    _inherit = "crm.phonecall"

    market_segment_id = fields.Many2one(
        comodel_name='market.segment.dzh',
        string='Market Segment'
    )
    member_type_id = fields.Many2one(
         comodel_name='member.type.dzh',
         string='Member Type'
    )
    product_ids = fields.Many2many(
         'product.product', 
         'rel_product_product', 
         'phone_call_id', 'product_id', 
         'Products')
    country_id = fields.Many2one(
         comodel_name='res.country',
         string='Country')
