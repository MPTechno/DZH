# -*- coding: utf-8 -*-
from odoo import fields, models


class account_invoice(models.Model):
    _inherit = 'account.invoice'

    cr_number = fields.Text('CR Number')
