from jinja2 import Environment, FileSystemLoader
from xhtml2pdf import pisa
import os

def generate_invoice_pdf(invoice):
    # Create the output directory if it doesn't exist
    if not os.path.exists('invoices'):
        os.makedirs('invoices')

    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('invoice_template.html')

    total_amount = sum([item['quantity'] * item['unit_price'] for item in invoice.items])

    html = template.render(
        invoice_id=invoice.id,
        client_name=invoice.client_name,
        client_address=invoice.client_address,
        invoice_date=invoice.invoice_date,
        due_date=invoice.due_date,
        items=invoice.items,
        total_amount=total_amount
    )

    file_path = f"invoices/invoice_{invoice.id}.pdf"
    with open(file_path, "w+b") as result_file:
        pisa_status = pisa.CreatePDF(html, dest=result_file)
    return pisa_status.err
