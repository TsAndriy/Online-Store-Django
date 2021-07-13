from django.urls import path

from .views import BaseViev, ProductDetailView, CategoryDetailViev

urlpatterns = [
    path('', BaseViev.as_view(), name='base'),
    path('products/<str:ct_model>/<str:slug>/', ProductDetailView.as_view(), name='product_detail'),
    path('category/<str:slug>/', CategoryDetailViev.as_view(), name='category_detail')
]