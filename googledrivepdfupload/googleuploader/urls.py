from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_pdf_view, name='upload_pdf'),
]
