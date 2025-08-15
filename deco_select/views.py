from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Product
from .forms import ProductForm

# --------- DRF 相关导入 ----------
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import ProductSerializer  # 注意：文件名是 serializer.py

# ========== 主页 ==========
def home(request):
    return render(request, 'deco_select/home.html')  # home.html 请确保存在

# ========== 添加产品页面 ==========
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('success')  # 跳转到添加成功页面（需要配置）
    else:
        form = ProductForm()
    return render(request, 'deco_select/add_product.html', {'form': form})

# ========== 根据 model_number 查询产品 RESTful 接口 ==========
@api_view(['GET'])
def product_detail_by_model_number(request):
    """
    通过 model_number 查询产品详细信息（包含图片链接）
    查询参数名叫 type，但实际查 model_number 字段
    """
    model_number = request.GET.get('type')
    if not model_number:
        return Response({"msg": "type 参数必填", "code": 400, "data": None})
    try:
        product = Product.objects.get(model_number=model_number)
    except Product.DoesNotExist:
        return Response({"msg": "Product not found", "code": 404, "data": None})
    serializer = ProductSerializer(product, context={'request': request})
    return Response({
        "data": serializer.data,
        "msg": "获取成功",
        "code": 200
    })


@api_view(['GET'])
def product_search(request):
    """
    根据 product_type 和 style 查询产品列表（单值），兼容参数名大小写、去首尾空格
    """
    qp = request.query_params  # == request.GET
    product_type = (qp.get('ProductType') or qp.get('product_type') or qp.get('productType') or '').strip()
    style = (qp.get('Style') or qp.get('style') or '').strip()

    qs = Product.objects.all()
    if product_type:
        qs = qs.filter(product_type__iexact=product_type)  # 如需区分大小写改为 exact
    if style:
        qs = qs.filter(style__iexact=style)  # 如需区分大小写改为 exact

    model_list = [
        {
            "id": p.id,
            "model_number": p.model_number,
            "main_image": request.build_absolute_uri(p.main_image.url) if p.main_image else None,
            "preset": p.preset,
            "default": p.default,
        }
        for p in qs.only('id', 'model_number', 'main_image', 'preset', 'default')
    ]

    return Response({
        "data": {"modelList": model_list},
        "msg": "获取成功",
        "code": 200
    })

from .models import StaticAsset

@api_view(['GET'])
def get_static_asset(request):
    file_name = request.GET.get('file_name')
    if not file_name:
        return Response({
            "data": None,
            "msg": "file_name参数必填",
            "code": 400
        })
    try:
        asset = StaticAsset.objects.get(file_name=file_name)
    except StaticAsset.DoesNotExist:
        return Response({
            "data": None,
            "msg": "未找到该静态资源",
            "code": 404
        })

    data = {
        "file_name": asset.file_name,
        "image_url": request.build_absolute_uri(asset.image.url) if asset.image else None
    }
    return Response({
        "data": data,
        "msg": "获取成功",
        "code": 200
    })