# add the faas callback view's url here
from django.urls import path
from faas.views import faas_callback_view

urlpatterns = [
    path('callback/', faas_callback_view, name='faas-callback'),
]
