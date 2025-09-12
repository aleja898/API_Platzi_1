from django.urls import path
from . import views


app_name = 'Products'

# URLs de la aplicación products
urlpatterns = [
    path('', views.home, name='home'),
    path('catalog/', views.catalog, name='catalog'),
    path('catalog/<int:product_id>/', views.product_detail, name='product_detail'),
    path('catalog/add/', views.product_add, name='product_add'),
    path('catalog/<int:product_id>/edit/', views.product_edit, name='product_edit'),
    path('catalog/<int:product_id>/delete/', views.product_delete, name='product_delete'),
]