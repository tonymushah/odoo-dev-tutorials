from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError


def date_availability_default():
    current_date = fields.Date().today()
    return current_date + timedelta(weeks=13)


class Property(models.Model):
    _name = "estate.property"
    _description = "The Real Estate Property"
    _check_expected_price = models.Constraint(
        "CHECK(expected_price > 0)", "the expected price should be strictly positive"
    )
    _check_selling_price = models.Constraint(
        "CHECK(selling_price > 0)", "the selling price should be strictly positive"
    )

    name = fields.Char("Property name", required=True)
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(copy=False, default=date_availability_default())
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True, copy=False)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection(
        selection=[
            ("north", "North"),
            ("south", "South"),
            ("east", "East"),
            ("west", "West"),
        ]
    )
    active = fields.Boolean(default=True)
    state = fields.Selection(
        selection=[
            ("new", "New"),
            ("offer_received", "Offer Received"),
            ("offer_accepted", "Offer Accepted"),
            ("sold", "Sold"),
            ("cancelled", "Cancelled"),
        ],
        default="new",
    )
    property_type_id = fields.Many2one("estate.property.type", string="Type")
    saleperson_user_id = fields.Many2one(
        "res.users", string="Salesperson", default=lambda self: self.env.user
    )
    buyer_partner_id = fields.Many2one("res.partner", "Buyer", copy=False)
    tag_ids = fields.Many2many("estate.property.tag", string="Tags")
    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Offers")
    total_area = fields.Integer(compute="_compute_total_area")
    best_price = fields.Float(compute="_compute_best_price")

    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.depends("offer_ids.price")
    def _compute_best_price(self):
        for record in self:
            offer_prices = record.offer_ids.mapped("price")

            record.best_price = max(offer_prices) if offer_prices else 0

    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = "north"
        else:
            self.garden_area = None
            self.garden_orientation = None

    def sold_estate_property(self):
        for property in self:
            match property.state:
                case "sold":
                    raise UserError(_("Cannot sell a property twice."))
                case "canceled":
                    raise UserError(_("Cannot sell a cancelled property."))
                case _def:
                    property.state = "sold"
        return True
        # raise UserError(_("Not yet implemented"))

    def cancel_estate_property(self):
        for property in self:
            match property.state:
                case "sold":
                    raise UserError(_("Cannot cancel a sold property."))
                case "canceled":
                    raise UserError(_("Cannot cancel a property twice."))
                case _def:
                    property.state = "canceled"
        return True
        # raise UserError(_("Not yet implemented"))
