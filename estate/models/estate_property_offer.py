from odoo import models, fields, api
from datetime import timedelta, datetime
from odoo.exceptions import UserError

class EstatePropertyOffer(models.Model):
    _name = 'estate.property.offer'  #model name
    _description = 'Real Estate Property Offer'  #description

    _order= 'price desc'#highest offers first

    _sql_constraints = [
        ('check_offer_price', 'CHECK(price > 0)', 
         'offer price must be strictly positive'),
    ]

    price = fields.Float()  #price
    status = fields.Selection(
        selection=[
        ('accepted', 'Accepted'),
        ('refused', 'Refused')
    ],
        copy=False  #dont copy status
    )
    partner_id = fields.Many2one('res.partner', required = True)  #who made the offer
    property_id = fields.Many2one('estate.property', required=True)  #which house

    validity = fields.Integer(string = "Validity(days)", default = 7)  #how long offer lasts
    date_deadline = fields.Date(  #when the offer expires
        string = "Deadline",
        compute='_compute_date_deadline',
        inverse='_inverse_date_deadline',
        store=True
    )
    property_type_id = fields.Many2one(
        'estate.property.type',
        string='Property Type',
        related='property_id.property_type_id',
        store=True,
        readonly=True
    )

    @api.depends('create_date', 'validity')
    def _compute_date_deadline(self):
        for offer in self:  # loop thru offers
            if offer.create_date:  #if offer exists in db
                offer.date_deadline = offer.create_date.date()+timedelta(days=offer.validity)
            else:  # for new records
                offer.date_deadline = fields.Date.today()+ timedelta(days=offer.validity)

    def _inverse_date_deadline(self):
        for offer in self:
            if offer.create_date and offer.date_deadline:  #safety check
                create_date = fields.Date.from_string(offer.create_date.date())
                deadline = fields.Date.from_string(offer.date_deadline)
                offer.validity = (deadline - create_date).days  #calculate days if date changed

    def action_accept(self):#when click accept button
        for offer in self:
            if offer.property_id.state == 'sold':  #cant accept if sold
                raise UserError("cant accept offer for already sold property")
            accepted_offers= offer.property_id.offer_ids.filtered(
                lambda o: o.status == 'accepted' and o.id != offer.id
            )
            if accepted_offers:
                raise UserError("Only one offer can be accepted per property")
            
            offer.status = 'accepted'  #update status
            offer.property_id.write({  #update the property
                'buyer_id': offer.partner_id.id,  #set buyer
                'selling_price': offer.price,  # set price
                'state': 'offer_accepted'  #change property state
            })
        return True
    
    def action_refuse(self):  #when click refuse button
        for offer in self:
            if offer.status == 'accepted':  #if was accepted before
                offer.property_id.write({
                    'buyer_id': False,
                    'selling_price': 0  #reset price
                })
            offer.status = 'refused'  #update status
        return True