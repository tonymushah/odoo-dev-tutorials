from odoo import fields, models


class PropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Real Estate Property Tag"
    _order = "name"

    name = fields.Char("Property Tag", required=True)
    _unique_name = models.Constraint("UNIQUE(name)", "The name must be unique")
