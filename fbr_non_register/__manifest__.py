# -*- coding: utf-8 -*-
{
    'name': "FBR Non Register",
    'summary': """This module is for non register companies to calculate taxes""",
    'description': """This module is for non register companies to calculate taxes """,
    'author': "My Company",
    'website': "http://www.yourcompany.com",
    'category': 'Tools',
    'version': '0.1',
    'depends': ['base', 'sale_management', 'account', 'purchase'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/inherit_sale_order.xml',
        'views/inherit_purchase_order.xml',
        'data/data_account.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
