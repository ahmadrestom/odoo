from odoo import models, fields, api, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare, float_is_zero

class EstateProperty(models.Model):
    #Define the model name in odooo
    _name = "estate.property"
    #Description of the model
    _description = "Real Estate Property"

    _order = 'id desc' #newest proeprties first

    _sql_constraints = [
        ('check_expected_price', 'CHECK(expected_price > 0)', 
         'Property expected price must be strictly positive'),
        ('check_selling_price', 'CHECK(selling_price >= 0)', 
         'Property selling price must be positive'),
    ]

    #Basic fields
    name = fields.Char(required=True)  #Property name/title
    description = fields.Text()  #Description of the property
    postcode = fields.Char()  #Postal code of the property location
    
    #Availabilitiy date with default set to 90 days from now
    date_availability = fields.Date(copy=False, default=lambda self: datetime.now() + timedelta(days=90), required=False)
    
    #Prices fields
    expected_price = fields.Float(required=True)  #Required expected selling price
    selling_price = fields.Float(readonly=True, copy=False)  #Final selling price (read-only, can't be changed)
    # Property characteristics
    bedrooms = fields.Integer(default=2)  #Number of bedrooms, default 2 rooms
    living_area = fields.Integer()  #interior living area in square meter
    facades = fields.Integer()  #Number of  facades
    garage = fields.Boolean()  #Whether the property has a garage or  not
    garden = fields.Boolean()  # Whether the property has a garden
    garden_area = fields.Integer()  #Garden area in square meters
    garden_orientation = fields.Selection(
        selection=[ #where the garden is facing
            ('north', 'North'), 
            ('south', 'South'), 
            ('east', 'East'),   
            ('west', 'West'),   
        ]
    )

    #Status fields
    active = fields.Boolean('Active', default=True)  #Whether property is active, default inactive
    state = fields.Selection(
        selection=[
            ('new','New'),  #newly created property
            ('offer_received','Offer Received'),  #At least one offer received
            ('offer_accepted','Offer Accepted'),  #Offer has been accepted
            ('sold','Sold'),  #Property has been sold
            ('canceled','Canceled')  #Property sale canceled
        ],
        string='Status',
        required=True,
        copy=False,  
        default='new'
    )
    
    #relationship fields
    property_type_id = fields.Many2one('estate.property.type', string='Property Type')  #Link to property type
    salesperson_id = fields.Many2one('res.users', string='Salesperson', default=lambda self: self.env.user) #Default to current user
    buyer_id = fields.Many2one('res.partner', string='Buyer', copy=False)  #who bought the property??
    tag_ids = fields.Many2many(
        'estate.property.tag',
        string='Tags',  # Field label
        widget='many2many_tags'  #Display as tags in the UI
    )

    #One to many relationship with offers
    offer_ids = fields.One2many(
        'estate.property.offer',  #related model
        'property_id',  #Inverse field name in the offer model
        string='Offers'  #Field label
    )

    #Computed field for total area (living + garden)
    total_area = fields.Integer(
        string='Total Area(sqm)',  #Field label
        compute='_compute_total_area',#computation method
        store=True  #store in database for performance
    )
    
     #Method to compute total area
    @api.depends('living_area', 'garden_area')  #Triggers when these fields change
    def _compute_total_area(self):
        for record in self:  #Loop through all records
            record.total_area = record.living_area + record.garden_area  #sum living and garden areas

    #field for the best offer price
    best_price = fields.Float(
        string="Best Offer",  #field label
        compute='_compute_best_price',
        store=True  #store database
    )

    # Method to compute the best offer price
    @api.depends('offer_ids.price')  #trigger when offer prices change
    def _compute_best_price(self):
        for property in self:  #oop through all properties
            #get max offer price if offers exist else 0 is the answer
            property.best_price = max(property.offer_ids.mapped('price')) if property.offer_ids else 0.0

    @api.onchange('garden') #Decorator that triggers this method whenever garden is modified in view
    def _onchange_garden(self):
        """ Set default garden area and orientation when garden is checked """
        for record in self:#looop through all records 
            if record.garden:  #check if the garden checkbox is checked 
                record.garden_area = 10 #set default value when garden exists  as 10sqm
                record.garden_orientation = 'north' #default orientation
            else: # when garden is unchecked reset values
                record.garden_area= 0
                record.garden_orientation = False

    def action_cancel(self):
        for property in self:
            if property.state == 'sold':
                raise UserError("Sold properties cannot be cancelled.")
            property.state = 'canceled'
        return True

    def action_sold(self):
        for property in self:
            if property.state == 'canceled':
                raise UserError("canceled properties cannot be sold.")
            property.state = 'sold'
        return True

    @api.constrains('selling_price', 'expected_price')
    def _check_selling_price(self):
        for property in self:
            if not float_is_zero(property.selling_price, precision_digits=2):  # Only check if sell price not zero
                min_price = property.expected_price * 0.9
                if float_compare(property.selling_price, min_price, precision_digits=2) < 0:
                    raise ValidationError(
                        f"selling price cannot be lower than 90% of expected price"
                        f"Minimum allowed: {min_price:.2f}"
                    )

    @api.ondelete(at_uninstall=False)
    def _prevent_deletion_if_not_new_or_cancelled(self):
        for property in self:
            if property.state not in ('new', 'canceled'):
                raise UserError(_("You cannot delete a property that is not in 'New or 'Cancelled' statet'"))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            property_id = vals.get('property_id')
            if property_id:
                property = self.env['estate.property'].browse(property_id)

                existing_offers = property.offer_ids.mapped('price')
                if existing_offers and vals.get('price', 0) <= max(existing_offers):
                    raise UserError(_("You cannot create an offer with a lower amount than existing offers The minimum offer is %s") % max(existing_offers))
                if property.state == 'new':
                    property.write({'state': 'offer_received'})

        return super().create(vals_list)
    

    def action_print_offers_report(self):
        return self.env.ref('estate.action_property_offers_report').report_action(self)