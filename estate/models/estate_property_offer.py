from odoo import fields, models


class PropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "The Property Offers"

    price = fields.Float()
    status = fields.Selection(
        selection=[("accepted", "Accepted"), ("refused", "Refused")]
    )
    buyer_partner_id = fields.Many2one("res.partner", required=True, string="Buyer")
    property_id = fields.Many2one("estate.property", required=True, string="Property")
