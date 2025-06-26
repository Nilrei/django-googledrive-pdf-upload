import os
import tempfile
from django.shortcuts import render
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from django.conf import settings
from .gdrive import run_upload_flow
import logging


# Configure module-level logger (can be overridden by Django logging config)
logger = logging.getLogger(__name__)

def generate_pdf(title: str) -> str:
    # generate temp folder with save path
    temp_dir = tempfile.gettempdir()
    filename = f"{title.replace(' ', '_')}.pdf"
    pdf_path = os.path.join(temp_dir, filename)

    c = canvas.Canvas(pdf_path)
    c.drawString(100, 750, f"PDF Title: {title}")
    c.save()
    return pdf_path


def upload_pdf_view(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        pdf_path = generate_pdf(title)
        file_id = run_upload_flow(
            credentials_path=settings.GDRIVE_CREDENTIALS,
            order_number=title,
            pdf_path=pdf_path,
            parent_folder_id=settings.GDRIVE_PARENT_ID  # oder None
        )
        return HttpResponse(f"Uploaded PDF with ID: {file_id}")
    return render(request, 'googleuploader/form.html')
