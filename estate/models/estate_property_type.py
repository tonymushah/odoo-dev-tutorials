from odoo import api, fields, models


class PropertyType(models.Model):
    _name = "estate.property.type"
    _description = "The Real Estate Property Types"
    _order = "sequence, name"

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    property_ids = fields.One2many(
        "estate.property", "property_type_id", string="Properties"
    )
    sequence = fields.Integer("Sequence", default=1)
    property_offer_ids = fields.One2many(related="property_ids.offer_ids")
    offer_count = fields.Integer(compute="_compute_offer_count")

    @api.depends("property_offer_ids")
    def _compute_offer_count(self):
        for prop_type in self:
            prop_type.offer_count = (
                len(prop_type.property_offer_ids) if prop_type.property_offer_ids else 0
            )
