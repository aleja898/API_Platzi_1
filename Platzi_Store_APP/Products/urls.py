from django.urls import path
from . import views

# URLs de la aplicación products
urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.consult_products, name='consult_products'),
    path('products/create/', views.create_product, name='create_product'),
    path('products/<int:pk>/', views.detail_product, name='detail_product'),
    path('products/<int:pk>/update/', views.update_product, name='update_product'),
    path('products/<int:pk>/delete/', views.delete_product, name='delete_product'),
]