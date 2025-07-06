from odoo import models, fields, api
from datetime import datetime, timedelta

class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Real Estate Property"

    name = fields.Char(required=True)
    description = fields.Text()
    postcode = fields.Char()
    
    date_availability = fields.Date(copy=False, default = lambda self: datetime.now() + timedelta(days=90))
    
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
            ('north', 'North'),
            ('south', 'South'),
            ('east', 'East'),
            ('west', 'West'),
        ]
    )

    active = fields.Boolean('Active', default = False)
    state = fields.Selection(
        selection=[
            ('new','New'), 
            ('offer_received','Offer Received'), 
            ('offer_accepted','Offer Accepted'),
            ('sold','Sold'), 
            ('canceled','Canceled')
        ],
        required = True,
        copy=False,
        default = 'new'
    )
    
    property_type_id = fields.Many2one('estate.property.type', string= 'Property Type')
    salesperson_id = fields.Many2one('res.users', string='Salesperson', default=lambda self: self.env.user)
    buyer_id = fields.Many2one('res.partner', string='Buyer', copy=False)
    tag_ids = fields.Many2many(
        'estate.property.tag',
        string='Tags',
        widget='many2many_tags'
    )

    offer_ids = fields.One2many(
        'estate.property.offer',
        'property_id',
        string='Offers'
    )

    total_area = fields.Integer(
        string = 'Total Area(sqm)',
        compute='_compute_total_area',
        store=True
    )
    @api.depends('living_area', 'garden_area')
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area+record.garden_area

    best_price = fields.Float(
        string = "Best Offer",
        computer = '_compute_best_price',
        store=True
    )

    @api.depends('offer_ids.price')
    def _compute_best_price(self):
        for property in self:
            property.best_price=max(property.offer_ids.mapped('price')) if property.offer_ids else 0.0
            