{
    'name': 'App one',
    'depends': ['base', 'account', 'sale_management', 'mail', 'contacts', 'report_xlsx', 'sale_stock'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequences.xml',
        'views/base_menu.xml',
        'views/property_views.xml',
        'views/owner_views.xml',
        'views/tag_views.xml',
        'views/client_views.xml',
        # 'views/sale_order_views.xml',
        'views/res_partner_views.xml',
        'views/account_move_views.xml',
        'views/building_views.xml',
        'views/property_history_views.xml',
        'wizard/change_state_wizard_views.xml',
        'reports/property_report.xml',
        'reports/person_report.xml',
        'reports/sale_report.xml',
        'reports/invoice_report.xml',
        'reports/work_report.xml',
        'wizard/view_sale_order_report_wizard_form.xml',
        'wizard/res_partner_wizard_views.xml',

        'views/property_offers_views.xml',
        'views/person_views.xml',
        'views/related_person_views.xml',
        'views/gift_views.xml',
        'views/birthday_views.xml',
    ],
    'assets': {
        'web.report_assets_common': [
            'app_one/static/src/css/font.css'
        ],
        'web.assets_backend': [
            'app_one/static/src/css/proprty.css'


        ],

    },

    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
