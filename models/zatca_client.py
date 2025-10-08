import base64
import requests
from odoo import models
from signxml import XMLSigner
from lxml import etree
from cryptography.hazmat.primitives.serialization import pkcs12

class ZatcaClient:
    def __init__(self, env):
        self.env = env
        IrConfig = env['ir.config_parameter'].sudo()

        # اقرأ متغيّرات الإعدادات
        self.mode = IrConfig.get_param('zatca_integration.mode', 'sandbox')
        self.base_url = IrConfig.get_param('zatca_integration.sandbox_url') or 'https://sandbox.zatca.gov.sa/e-invoices'
        self.cert_password = IrConfig.get_param('zatca_integration.cert_password') or ''

        # تحميل الشهادة من attachment
        attachment = env['ir.attachment'].search([('name', '=', 'zatca_cert.p12')], limit=1)
        if not attachment:
            raise ValueError("ZATCA certificate not found in attachments (zatca_cert.p12)")
        self.cert_bytes = base64.b64decode(attachment.datas)

    def sign_xml(self, xml_str: str) -> bytes:
        """توقيع XML رقمياً باستخدام شهادة ZATCA."""
        if not self.cert_bytes:
            raise Exception('ZATCA certificate missing.')
        p12 = pkcs12.load_key_and_certificates(
            self.cert_bytes,
            self.cert_password.encode() if self.cert_password else None
        )
        private_key, cert, _ = p12
        root = etree.fromstring(xml_str.encode('utf-8'))
        signer = XMLSigner(method="enveloped", signature_algorithm='rsa-sha256')
        signed_xml = signer.sign(root, key=private_key, cert=cert)
        return etree.tostring(signed_xml, xml_declaration=True, encoding='utf-8')

    def send_invoice(self, signed_xml_bytes: bytes, endpoint: str):
        """إرسال الفاتورة الموقعة إلى ZATCA (sandbox أو production)."""
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        headers = {'Content-Type': 'application/xml'}
        try:
            response = requests.post(url, data=signed_xml_bytes, headers=headers, timeout=30)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise Exception(f"ZATCA request failed: {str(e)}")
        return response.text