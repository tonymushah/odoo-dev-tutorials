from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class PropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "The Property Offers"
    _order = "price desc"

    price = fields.Float()
    _check_price = models.Constraint(
        "CHECK(price > 0)", "the offer price must be strictly positive"
    )
    status = fields.Selection(
        selection=[("accepted", "Accepted"), ("refused", "Refused")]
    )
    buyer_partner_id = fields.Many2one("res.partner", required=True, string="Buyer")
    property_id = fields.Many2one("estate.property", required=True, string="Property")
    validity = fields.Integer(default=7)
    date_deadline = fields.Date(
        compute="_compute_date_deadline", inverse="_inverse_date_deadline"
    )
    property_type_id = fields.Many2one(
        related="property_id.property_type_id", store=True
    )
    hide_offer = fields.Boolean(
        compute="_compute_hide_offer", copy=False, default=False, store=True
    )

    @api.depends("validity", "create_date")
    def _compute_date_deadline(self):
        for offer in self:
            if offer.create_date:
                offer.date_deadline = offer.create_date + timedelta(days=offer.validity)

    @api.depends("status", "property_id.state")
    def _compute_hide_offer(self):
        for offer in self:
            # if offer.hide_offer:
            state = offer.property_id.state
            status = offer.status
            # print(status)
            if (state != "new" and state != "offer_received") or status:
                offer.hide_offer = True

    def _inverse_date_deadline(self):
        for offer in self:
            if offer.date_deadline:
                t_delta = offer.date_deadline - offer.create_date.date()
                offer.validity = t_delta.days

    def accept_offer_action(self):
        for offer in self:
            match offer.property_id.state:
                case "offer_accepted" | "sold" | "cancelled":
                    raise UserError(
                        _(
                            "The property already has an accepted offer or sold or cancelled"
                        )
                    )

            match offer.status:
                case "accepted":
                    raise UserError(_("Cannot accept an already accepted offer."))
                case "refused":
                    raise UserError(_("Cannot accept an already refused offer."))
                case _def:
                    offer.status = "accepted"
                    offer.property_id.buyer_partner_id = offer.buyer_partner_id
                    offer.property_id.selling_price = offer.price
                    offer.property_id.state = "offer_accepted"

        return True

    def refuse_offer_action(self):
        for offer in self:
            match offer.property_id.state:
                case "offer_accepted" | "sold" | "cancelled":
                    raise UserError(
                        _(
                            "The property already has an accepted offer or sold or cancelled"
                        )
                    )
            match offer.status:
                case "accepted":
                    raise UserError(_("Cannot refuse an already accepted offer."))
                case "refused":
                    raise UserError(_("Cannot refuse an already refused offer."))
                case _def:
                    offer.status = "refused"
        return True

    @api.model
    def create(self, vals):
        for property in self.env["estate.property"].browse(
            map(lambda val: val["property_id"], vals)
        ):
            if property.state == "new":
                property.state = "offer_received"
        return super().create(vals)
