from odoo import models

class EstateProperty(models.Model):
    _inherit = "estate.property"

    def action_sold(self):
        print("action_sold overridden")
        res = super().action_sold()

        for property in self:
            if not property.buyer_id:
                raise ValueError("Buyer is required to create an invoice")
            commission = property.selling_price * 0.06
            
            invoice_vals = {
                'partner_id': property.buyer_id.id,
                'move_type': 'out_invoice',
                'invoice_line_ids': [
                    (0, 0, {
                        'name': f'Commission for {property.name}',
                        'quantity': 1,
                        'price_unit': commission,
                    }),
                    (0, 0, {
                        'name': 'Administrative fees',
                        'quantity': 1,
                        'price_unit': 100.00,
                    }),
                ]
            }
            self.env['account.move'].create(invoice_vals)
        return res