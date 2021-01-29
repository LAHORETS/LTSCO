# -*- coding: utf-8 -*-
{
    'name': "Partner Tax Code",
    'name_vi_VN': 'Mã số thuê đối tác',

    'summary': """Search partner by Tax Identification Number""",
    'summary_vi_VN': """Tìm kiếm đối tác theo mã số thuế""",

    'description': """
Key Features
============

1. Search partner by Tax Identification Number
    
Editions Supported
==================
1. Community Edition
2. Enterprise Edition

    """,

    'description_vi_VN': """
Các tính năng chính
=================

1. Tìm kiếm đối tác theo mã số thuế

Ấn bản được Hỗ trợ
==================
1. Ấn bản Community
2. Ấn bản Enterprise

    """,

    'author': "T.V.T Marine Automation (aka TVTMA),Viindoo",
    'website': 'https://viindoo.com',
    'live_test_url': 'https://v13demo-int.erponline.vn',
    'support': 'apps.support@viindoo.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Sales',
    'version': '1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/res_partner.xml',
    ],

    'installable': True,
    'application': False,
    'auto_install': True,
    'price': 0.0,
    'currency': 'EUR',
    'license': 'OPL-1',
}
