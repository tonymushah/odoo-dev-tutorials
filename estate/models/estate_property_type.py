from odoo import fields, models


class PropertyType(models.Model):
    _name = "estate.property.type"
    _description = "The Real Estate Property Types"

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    property_ids = fields.One2many(
        "estate.property", "property_type_id", string="Properties"
    )
