from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    enable_zatca = fields.Boolean(
        string="Enable ZATCA Integration",
        config_parameter='zatca_integration.enable_zatca',
        help="Enable or disable integration with ZATCA"
    )
    zatca_mode = fields.Selection(
        [('sandbox', 'Sandbox'), ('production', 'Production')],
        string="Mode",
        config_parameter='zatca_integration.mode',
        default='sandbox',
        help="Select Sandbox for testing or Production for live transactions"
    )
    zatca_sandbox_url = fields.Char(
        string="ZATCA Sandbox URL",
        config_parameter='zatca_integration.sandbox_url',
        help="The ZATCA endpoint for testing (Sandbox)"
    )
    zatca_username = fields.Char(
        string="ZATCA Username",
        config_parameter='zatca_integration.username',
        help="Username for ZATCA API"
    )
    zatca_certificate_path = fields.Char(
        string="ZATCA Certificate Path",
        config_parameter='zatca_integration.certificate_path',
        help="Path of the PFX certificate file used for signing"
    )
    zatca_certificate_password = fields.Char(
        string="Certificate Password",
        config_parameter='zatca_integration.cert_password',
        help="Password for the PFX certificate file"
    )