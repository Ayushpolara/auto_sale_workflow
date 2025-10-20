# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # ----------------------------------------------------------
    # Automatic Delivery Validation
    # ----------------------------------------------------------
    auto_validate_delivery = fields.Boolean(
        string='Auto Validate Delivery',
        config_parameter='auto_sale_workflow.auto_validate_delivery',
        help='Automatically validate delivery orders on Sales Order confirmation.'
    )

    # ----------------------------------------------------------
    # Automatic Invoice Policy
    # ----------------------------------------------------------
    auto_invoice_action = fields.Selection(
        [
            ('none', 'No Automatic Invoice'),
            ('create', 'Create Invoice'),
            ('post', 'Create and Post Invoice'),
            ('register', 'Post and Register Payment'),
        ],
        string='Auto Sale Invoice',
        default='none',
        config_parameter='auto_sale_workflow.auto_invoice_action',
        help=(
            'Automatically generate invoice, post it, '
            'and optionally register payment on Sales Order confirmation.'
        )
    )
