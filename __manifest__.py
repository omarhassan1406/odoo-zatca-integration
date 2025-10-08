# __manifest__.py
{
    'name': 'ZATCA eInvoicing Integration',
    'version': '0.1.0',
    'summary': 'Integrate Odoo 17 with ZATCA (Fatoora)',
    'category': 'Accounting',
    'author': 'Omar Hassan',
    'license': 'AGPL-3',
    'depends': ['account', 'base'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_cron.xml',
        'views/res_config_settings_views.xml',
        'views/account_move_views.xml',
    ],
    'application': False,
}
