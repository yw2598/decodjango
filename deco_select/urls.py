from django.urls import path
from . import views
from django.http import JsonResponse
from .wx_token_service import start_wx_token_thread
from .views import login_view, register_view  
# 启动时运行线程
start_wx_token_thread()

def get_token(request):
    from django.core.cache import cache
    token = cache.get("wx_access_token")
    return JsonResponse({"token": token})

urlpatterns = [
    path('add_product/', views.add_product, name='add_product'),
    path('', views.home, name='home'),
    path('api/products', views.product_detail_by_model_number),   
    path('api/product_search', views.product_search, name='product_search'),
    path('api/static_asset', views.get_static_asset, name='get_static_asset'),
    path('api/products/<int:product_id>/', views.product_detail_by_id),  # 根据 id 查询单个产品
    path('api/save_user_selection', views.save_user_selection),  # 保存用户选择接口
    path('api/user_selection_summary', views.user_selection_top_products, name='user_selection_summary'),
    path("api/wechat/token", get_token),
    path("api/wechat/login", login_view),
    path("api/wechat/register", register_view),

]



# 媒体文件开发环境支持（仅开发时需要）
from django.conf import settings
from django.conf.urls.static import static
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

