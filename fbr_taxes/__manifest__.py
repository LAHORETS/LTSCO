# -*- coding: utf-8 -*-
{
    'name': "FBR Taxes",

    'summary': """
       Tax calculaion for unregistered suppliers""",

    'description': """
        Tax calculaion for unregistered suppliers
    """,

    'author': "Hunain AK",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'purchase', 'account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
    ],
    # only loaded in demonstration mode

}
