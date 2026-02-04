from datetime import timedelta

from odoo import api, fields, models


class PropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "The Property Offers"

    price = fields.Float()
    status = fields.Selection(
        selection=[("accepted", "Accepted"), ("refused", "Refused")]
    )
    buyer_partner_id = fields.Many2one("res.partner", required=True, string="Buyer")
    property_id = fields.Many2one("estate.property", required=True, string="Property")
    validity = fields.Integer(default=7)
    date_deadline = fields.Date(
        compute="_compute_date_deadline", inverse="_inverse_date_deadline"
    )

    @api.depends("validity")
    def _compute_date_deadline(self):
        for offer in self:
            offer.date_deadline = offer.create_date + timedelta(days=offer.validity)

    def _inverse_date_deadline(self):
        for offer in self:
            t_delta = offer.date_deadline - offer.create_date.date()
            offer.validity = t_delta.days
