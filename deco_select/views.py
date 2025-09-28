from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Product,UserSelection
from .forms import ProductForm
from datetime import datetime,timedelta
# --------- DRF 相关导入 ----------
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .serializers import ProductSerializer  # 注意：文件名是 serializer.py
from django.views.decorators.csrf import csrf_exempt
from .utils import login_by_code, register_user
import json
from django.http import JsonResponse
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
    通过 model_number 查询多个产品的详细信息（包含图片链接）
    查询参数名叫 type，但实际查 model_number 字段
    """
    model_number = request.GET.get('type')
    if not model_number:
        return Response({"msg": "type 参数必填", "code": 400, "data": None})
    
    # 使用 filter 来返回多个匹配的产品
    products = Product.objects.filter(model_number=model_number)
    
    # 如果没有找到任何产品，返回 404 错误
    if not products.exists():
        return Response({"msg": "Product not found", "code": 404, "data": None})
    
    # 使用序列化器将查询结果序列化
    serializer = ProductSerializer(products, many=True, context={'request': request})
    
    return Response({
        "data": serializer.data,
        "msg": "获取成功",
        "code": 200
    })

@api_view(['GET'])
def product_detail_by_id(request, product_id):
    """
    根据产品 id 查询产品的详细信息，确保返回唯一的产品
    """
    try:
        # 使用 get_object_or_404 方法根据 product_id 获取唯一的产品
        product = Product.objects.get(id=product_id)
        
        # 使用序列化器将查询结果序列化
        serializer = ProductSerializer(product)
        
        return Response({
            "data": serializer.data,
            "msg": "获取成功",
            "code": 200
        })
    
    except Product.DoesNotExist:
        # 如果没有找到该 id 对应的产品，返回 404 错误
        return Response({
            "msg": "Product not found",
            "code": 404,
            "data": None
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

from django.db import transaction
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import UserSelection, Product

@api_view(['POST'])
def save_user_selection(request):
    """
    接收用户的选择数据，保存到数据库（写入快照）
    参数:
      - user_id: 用户ID (int)
      - product_id: 产品ID (int)
    """
    user_id = request.data.get('user_id')
    product_id = request.data.get('product_id')

    # 参数校验
    if user_id is None or product_id is None:
        return Response({"msg": "user_id 和 product_id 参数必填", "code": 400, "data": None},
                        status=status.HTTP_400_BAD_REQUEST)
    try:
        user_id = int(user_id)
        product_id = int(product_id)
    except (TypeError, ValueError):
        return Response({"msg": "user_id 与 product_id 必须为整数", "code": 400, "data": None},
                        status=status.HTTP_400_BAD_REQUEST)

    # 查 Product，拿到用于快照的数据
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({"msg": "无效的 product_id", "code": 404, "data": None},
                        status=status.HTTP_404_NOT_FOUND)

    # 写入：外键 + 快照（timestamp 用 auto_now_add，无需手动传）
    with transaction.atomic():
        user_selection = UserSelection.objects.create(
            user_id=user_id,
            product=product,
            snapshot_model_number=product.model_number,
            snapshot_product_type=product.product_type,
            snapshot_style=product.style,
            snapshot_preset=product.preset,
            snapshot_default=product.default,
        )

    return Response({
        "msg": "选择数据已保存",
        "code": 200,
        "data": {
            "id": user_selection.id,
            "user_id": user_selection.user_id,
            "product_id": user_selection.product_id,
            "timestamp": user_selection.timestamp,  # auto_now_add 自动生成
            # 也可返回快照字段，便于前端立即使用
            "snapshot": {
                "model_number": user_selection.snapshot_model_number,
                "product_type": user_selection.snapshot_product_type,
                "style": user_selection.snapshot_style,
                "preset": user_selection.snapshot_preset,
                "default": user_selection.snapshot_default,
            }
        }
    }, status=status.HTTP_200_OK)

from django.utils.dateparse import parse_datetime, parse_date
from django.utils import timezone

from django.db.models import Count, Max
def _parse_to_aware_dt(s, default_tz):
    if not s:
        return None
    dt = parse_datetime(s)
    if dt is not None:
        return timezone.make_aware(dt, default_tz) if timezone.is_naive(dt) else dt
    d = parse_date(s)
    if d is not None:
        dt = timezone.datetime(d.year, d.month, d.day, 0, 0, 0)
        return timezone.make_aware(dt, default_tz)
    return None

@api_view(['GET'])
def user_selection_top_products(request):
    """
    统计所有用户在时间范围内的选配 TopN，并返回完整产品信息。
    可选参数：
      - start: 起始时间（ISO 或 YYYY-MM-DD），默认 end-365d
      - end:   结束时间（ISO 或 YYYY-MM-DD），默认 now
      - mode:  'count'（默认）| 'recent'
      - top:   Top N（默认5，最大50）
      - product_type: 梯型过滤（默认不过滤，精确匹配；可按需改成 icontains）
    """
    mode = (request.GET.get('mode') or 'count').lower()
    if mode not in ('count', 'recent'):
        mode = 'count'

    tz = timezone.get_current_timezone()
    now = timezone.now()
    end = _parse_to_aware_dt(request.GET.get('end'), tz) or now
    start = _parse_to_aware_dt(request.GET.get('start'), tz) or (end - timedelta(days=365))

    # Top N
    try:
        top_n = int(request.GET.get('top', '5'))
    except ValueError:
        top_n = 5
    top_n = max(1, min(top_n, 50))

    # ✅ 可选的梯型过滤
    product_type = request.GET.get('product_type')  # 例如 '客梯'、'货梯' 等

    # 基础筛选（所有用户）
    base_qs = UserSelection.objects.filter(
        timestamp__gte=start,
        timestamp__lte=end,
    )
    if product_type:
        # 精确匹配：product__product_type=product_type
        # 如果想要模糊匹配可改成：product__product_type__icontains=product_type
        base_qs = base_qs.filter(product__product_type=product_type)

    # 聚合：每个 product 的次数与最近一次时间
    agg = base_qs.values('product').annotate(
        sel_count=Count('id'),
        last_time=Max('timestamp'),
    )
    if mode == 'recent':
        agg = agg.order_by('-last_time', '-sel_count')
    else:
        agg = agg.order_by('-sel_count', '-last_time')

    # 统计信息（未截断前）
    total_count = base_qs.count()
    total_products = agg.count()

    rows = list(agg[:top_n])
    if not rows:
        return Response({
            "msg": "无记录",
            "code": 200,
            "data": {
                "start": start.isoformat(),
                "end": end.isoformat(),
                "mode": mode,
                "top": top_n,
                "product_type": product_type,
                "total_count": 0,
                "total_products": 0,
                "items": []
            }
        })

    # 序列化产品详情（保持排序）
    product_ids = [r['product'] for r in rows]
    product_map = Product.objects.in_bulk(product_ids)

    items = []
    for r in rows:
        p = product_map.get(r['product'])
        if not p:
            continue
        pdata = ProductSerializer(p, context={'request': request}).data
        items.append({
            "product": pdata,
            "count": r['sel_count'],
            "last_time": r['last_time'].isoformat(),
        })

    return Response({
        "msg": "获取成功",
        "code": 200,
        "data": {
            "start": start.isoformat(),
            "end": end.isoformat(),
            "mode": mode,
            "top": top_n,
            "product_type": product_type,  # 回显
            "total_count": total_count,
            "total_products": total_products,
            "items": items
        }
    }, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    登录接口：
    前端传 code (wx.login)，后端换 openid 并查数据库
    """
    if request.method != "POST":
        return JsonResponse({"success": False, "msg": "仅支持 POST"})

    try:
        body = json.loads(request.body)
    except Exception:
        return JsonResponse({"success": False, "msg": "请求体不是合法 JSON"})

    code = body.get("code")
    if not code:
        return JsonResponse({"success": False, "msg": "缺少 code 参数"})

    result = login_by_code(code)
    return JsonResponse(result)


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """
    注册接口：
    前端传 code (wx.login) + phone_code (wx.getPhoneNumber) + username
    后端解密并写入数据库
    """
    if request.method != "POST":
        return JsonResponse({"success": False, "msg": "仅支持 POST"})

    try:
        body = json.loads(request.body)
    except Exception:
        return JsonResponse({"success": False, "msg": "请求体不是合法 JSON"})

    code = body.get("code")
    phone_code = body.get("phone_code")
    username = body.get("username", "未命名用户")

    if not code or not phone_code:
        return JsonResponse({"success": False, "msg": "缺少 code 或 phone_code"})

    result = register_user(code, phone_code, username)
    return JsonResponse(result)