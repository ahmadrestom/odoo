from odoo import models, fields

class EstatePropertyTag(models.Model):
    _name = 'estate.property.tag'  #model name in the system
    _description = 'Real Estate Property Tag'

    name = fields.Char(required=True)  #field for tag name
    color = fields.Integer(string='Color Index')

    # sort tags A to Z by default
    _order = 'name asc'

    #prevents duplicate tag names in database
    _sql_constraints = [
        ('unique_tag_name', 'UNIQUE(name)',  #database level constraint
         'Property tag name must be unique'),  # error message users will see
    ]