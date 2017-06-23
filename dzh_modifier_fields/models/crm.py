# -*- coding: utf-8 -*-
from odoo import fields, models

class CRMLead(models.Model):
    _inherit = 'crm.lead'

    market_segment_id = fields.Many2one('market.segment', string="Market Segment")
    member_type_id = fields.Many2one('member.type', string="Member Type")
    dzh_user = fields.Char('User ID')
    dzh_check_box = fields.Boolean(string="Trial Account")
    dzh_user_id = fields.Char('User ID')
    start_date= fields.Date('Start Date')
    end_date = fields.Date('End Date')
    product_id = fields.Many2many('product.product', string="Product")
    currency_id = fields.Many2one("res.currency", "Currency")

class MarketSegmet(models.Model):
    _name = 'market.segment'

    name = fields.Char('Name')

class MemberType(models.Model):
    _name = 'member.type'

    name = fields.Char('Name')
