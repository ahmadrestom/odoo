from odoo import models, fields, api

class EstatePropertyType(models.Model):
    _name = 'estate.property.type'
    _description = 'Real Estate Property Type'

    #orders types by sequence number firstthen alphabetically
    _order = 'sequence, name'

    name = fields.Char(required=True)
    
    sequence = fields.Integer(
        string='Sequence',  #shows as "Sequence" in UI
        default=10,  #lets you insert items between existing ones
        help="Used to order property types" 
    )

    #blocks duplicate type names at database
    _sql_constraints = [
        ('unique_type_name', 'UNIQUE(name)',  #creates a db constrant
         'type names must be unique'),  #error message
    ]
    property_ids = fields.One2many(
        'estate.property',  #links to properties table
        'property_type_id',  #the field in properties that points back here
        string='Properties'  #label for the ui
    )

    offer_ids = fields.One2many(
        'estate.property.offer',
        'property_type_id',
        string='Offers'
    )

    offer_count = fields.Integer(
        string='Offer Count',
        compute='_compute_offer_count',
        store=True
    )

    @api.depends('offer_ids')
    def _compute_offer_count(self):
        for record in self:
            record.offer_count = len(record.offer_ids)