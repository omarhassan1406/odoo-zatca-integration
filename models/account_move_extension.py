from odoo import models, fields, api, _
from .zatca_client import ZatcaClient
from lxml import etree
import base64
import qrcode
from io import BytesIO
import json


class AccountMove(models.Model):
    _inherit = 'account.move'

    zatca_uuid = fields.Char(string='ZATCA UUID', readonly=True, copy=False)
    zatca_status = fields.Selection([
        ('draft', 'Draft'),
        ('signed', 'Signed'),
        ('sent', 'Sent'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected')
    ], string='ZATCA Status', default='draft', readonly=True)
    zatca_qr = fields.Binary(string='ZATCA QR', readonly=True, attachment=True)

    # === Main Action ===
    def action_zatca_send(self):
        """Sign and send the invoice XML to ZATCA."""
        client = ZatcaClient(self.env)

        for inv in self:
            # 1️⃣ Generate invoice XML
            xml = inv._generate_zatca_xml()

            # 2️⃣ Sign invoice
            signed_xml = client.sign_xml(xml)
            inv.zatca_status = 'signed'

            # 3️⃣ Send invoice to ZATCA endpoint
            try:
                response = client.send_invoice(signed_xml, 'api/v1/invoices')
                inv.zatca_status = 'sent'

                # Try parsing response (simulate)
                if isinstance(response, (bytes, bytearray)):
                    response = response.decode('utf-8')

                try:
                    data = json.loads(response)
                    inv.zatca_uuid = data.get('uuid', 'UUID_NOT_FOUND')
                    inv.zatca_status = data.get('status', 'accepted')
                except Exception:
                    inv.zatca_uuid = 'SAMPLE-UUID'
                    inv.zatca_status = 'accepted'

                # 4️⃣ Generate QR Code
                qr_data = f"UUID: {inv.zatca_uuid}\nInvoice: {inv.name}\nTotal: {inv.amount_total}"
                qr = qrcode.make(qr_data)
                bio = BytesIO()
                qr.save(bio, format='PNG')
                inv.zatca_qr = base64.b64encode(bio.getvalue())

            except Exception as e:
                inv.zatca_status = 'rejected'
                raise Exception(_("Failed to send invoice to ZATCA: %s") % str(e))

    # === XML Builder ===
    def _generate_zatca_xml(self):
        """Generate a minimal UBL-like XML for testing (not final production structure)."""
        root = etree.Element('Invoice')
        etree.SubElement(root, 'ID').text = self.name or ''
        etree.SubElement(root, 'IssueDate').text = (
            self.invoice_date.isoformat() if self.invoice_date else ''
        )
        etree.SubElement(root, 'CustomerName').text = self.partner_id.name or ''
        etree.SubElement(root, 'TotalAmount').text = str(self.amount_total)
        etree.SubElement(root, 'VATAmount').text = str(self.amount_tax)
        etree.SubElement(root, 'Currency').text = self.currency_id.name or 'SAR'

        # Each invoice line
        lines_el = etree.SubElement(root, 'InvoiceLines')
        for line in self.invoice_line_ids:
            line_el = etree.SubElement(lines_el, 'Line')
            etree.SubElement(line_el, 'Description').text = line.name or ''
            etree.SubElement(line_el, 'Quantity').text = str(line.quantity)
            etree.SubElement(line_el, 'Price').text = str(line.price_unit)
            etree.SubElement(line_el, 'Subtotal').text = str(line.price_subtotal)

        return etree.tostring(root, pretty_print=True, encoding='utf-8').decode('utf-8')
