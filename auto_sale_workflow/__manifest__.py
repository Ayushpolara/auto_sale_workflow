{
    "name": "Auto Sale Workflow",
    "version": "18.0.0.0.0",
    "category": "Sales",
    "summary": "Automate sales order confirmation, delivery validation, invoice generation and payment registration",
    "description": """
Auto Sale Workflow
==================
Streamline your sales process with automated workflows.

Features:
---------
* Auto Confirm and Validate Sales Orders
* Automatic Invoice Generation
* Auto Validate Invoices
* Auto Register Payments
* Configure Shipping/Invoice Policy per Order
* Select Sale/Payment Journal per Order
* Simple configuration in Sales Settings

This module helps businesses save time by automating repetitive sales operations.
    """,
    "author": "Ayush Polara",
    "website": "http://in.linkedin.com/in/ayush-polara-017b4b221",
    "license": "LGPL-3",
    "depends": ["sale_management", "stock", "account"],
    "data": [
        "security/ir.model.access.csv",
        "views/res_config_settings_views.xml",
        "views/sale_order_views.xml",
    ],
    "images": ["static/description/banner.gif"],
    "installable": True,
    "application": False,
    "auto_install": False,
    "price": 0.00,
    "currency": "EUR",
}
