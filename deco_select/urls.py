from django.urls import path
from . import views

urlpatterns = [
    path('add_product/', views.add_product, name='add_product'),
    path('', views.home, name='home'),
    path('api/products', views.product_detail_by_model_number),   
    path('api/product_search', views.product_search, name='product_search'),
    path('api/static_asset', views.get_static_asset, name='get_static_asset'),
]

# 媒体文件开发环境支持（仅开发时需要）
from django.conf import settings
from django.conf.urls.static import static
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
