# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # ----------------------------------------------------------
    # Configuration Fields for Automatic Workflow
    # ----------------------------------------------------------
    auto_workflow_enabled = fields.Boolean(
        string='Enable Auto Workflow',
        help='Enable automatic workflow for this order',
        default=True
    )

    auto_validate_delivery_order = fields.Boolean(
        string='Auto Validate Delivery',
        help='Automatically validate delivery orders',
        default=True
    )

    auto_invoice_policy = fields.Selection(
        [
            ('none', 'No Automatic Invoice'),
            ('create', 'Create Invoice'),
            ('post', 'Create and Post Invoice'),
            ('register', 'Create, Post and Register Payment'),
        ],
        string='Auto Invoice Policy',
        default='none',
        help='Invoice generation policy for this order'
    )

    payment_journal_id = fields.Many2one(
        'account.journal',
        string='Payment Journal',
        domain="[('type', 'in', ['bank', 'cash'])]",
        help='Journal for automatic payment registration'
    )

    # ----------------------------------------------------------
    # Onchange Method
    # ----------------------------------------------------------
    @api.onchange('auto_workflow_enabled')
    def _onchange_auto_workflow_enabled(self):
        """
        Load default settings from system parameters when auto workflow is enabled.
        """
        if self.auto_workflow_enabled:
            ICP = self.env['ir.config_parameter'].sudo()
            self.auto_validate_delivery_order = ICP.get_param(
                'auto_sale_workflow.auto_validate_delivery', default=False
            )
            self.auto_invoice_policy = ICP.get_param(
                'auto_sale_workflow.auto_invoice_action', default='none'
            )

    # ----------------------------------------------------------
    # Override Sale Order Confirmation
    # ----------------------------------------------------------
    def action_confirm(self):
        """
        Override action_confirm to trigger automatic workflow based on configuration.
        """
        res = super(SaleOrder, self).action_confirm()

        for order in self:
            if order.auto_workflow_enabled:
                order._execute_auto_workflow()

        return res

    # ----------------------------------------------------------
    # Automatic Workflow Execution
    # ----------------------------------------------------------
    def _execute_auto_workflow(self):
        """
        Execute automatic workflow for the sale order:
        1. Auto validate delivery orders
        2. Auto create/post/register invoice based on policy
        """
        self.ensure_one()

        if self.auto_validate_delivery_order:
            self._auto_validate_delivery()

        if self.auto_invoice_policy != 'none':
            self._auto_create_invoice()

    # ----------------------------------------------------------
    # Delivery Order Automation
    # ----------------------------------------------------------
    def _auto_validate_delivery(self):
        """
        Automatically validate all draft or confirmed delivery orders.
        """
        self.ensure_one()

        for picking in self.picking_ids:
            if picking.state in ['draft', 'waiting', 'confirmed', 'assigned']:
                # Ensure all move lines have quantities
                for move in picking.move_ids:
                    for move_line in move.move_line_ids:
                        move_line.quantity = move_line.quantity
                    if not move.move_line_ids:
                        move._action_assign()
                        for move_line in move.move_line_ids:
                            move_line.quantity = move_line.quantity

                # Validate the picking, ignore UserError for already validated pickings
                try:
                    picking.button_validate()
                except UserError:
                    pass

    # ----------------------------------------------------------
    # Invoice Automation
    # ----------------------------------------------------------
    def _auto_create_invoice(self):
        """
        Automatically create, post, and register payment for the invoice
        based on the auto_invoice_policy.
        """
        self.ensure_one()

        if self.invoice_status != 'to invoice':
            return

        # Create invoice(s) for the sale order
        invoice = self._create_invoices()
        if not invoice:
            return

        # Post invoice if policy requires
        if self.auto_invoice_policy in ['post', 'register'] and invoice.state == 'draft':
            invoice.action_post()

        # Register payment if policy requires
        if self.auto_invoice_policy == 'register':
            self._auto_register_payment(invoice)

    # ----------------------------------------------------------
    # Payment Registration Automation
    # ----------------------------------------------------------
    def _auto_register_payment(self, invoice):
        """
        Automatically register payment for the invoice using a payment register wizard.
        """
        self.ensure_one()

        if not invoice or invoice.payment_state == 'paid':
            return

        # Determine the payment journal to use
        payment_journal = self.payment_journal_id or self.env['account.journal'].search([
            ('type', 'in', ['bank', 'cash']),
            ('company_id', '=', self.company_id.id)
        ], limit=1)

        if not payment_journal:
            return

        # Create and process payment
        payment_register = self.env['account.payment.register'].with_context(
            active_model='account.move',
            active_ids=invoice.ids,
        ).create({
            'journal_id': payment_journal.id,
            'amount': invoice.amount_residual,
            'payment_date': fields.Date.context_today(self),
        })

        payment_register.action_create_payments()
