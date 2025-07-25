{
    'name': 'Estate',
    'version': '1.0',
    'application': True,
    'summary': 'First Odoo module',
    'description': 'Creating modules in Odoo',
    'author': 'Ahmad Restom',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/estate_property_views.xml',
        'views/estate_property_type_views.xml',
        'views/estate_property_tag_views.xml',
        'views/estate_property_offer_views.xml',
        'views/res_users_views.xml',
        'report/estate_property_reports.xml',
        'report/estate_property_templates.xml',
        'views/estate_menus.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': False
}