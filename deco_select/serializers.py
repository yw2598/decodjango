from rest_framework import serializers
from .models import Product,COP,UserSelection

class COPSerializer(serializers.ModelSerializer):
    class Meta:
        model = COP
        fields = ['id', 'name', 'description', 'image']  # 按你需要返回哪些字段

class ProductSerializer(serializers.ModelSerializer):
    cop = COPSerializer()  # 用嵌套序列化器替换原来默认的id
    class Meta:
        model = Product
        fields = '__all__'

def create(self, validated_data):
    product_id = validated_data.pop('product_id')
    product = Product.objects.get(id=product_id)

    return UserSelection.objects.create(
        product=product,
        **validated_data,
        snapshot_model_number=product.model_number,
        snapshot_product_type=product.product_type,
        snapshot_style=product.style,
        snapshot_preset=product.preset,
        snapshot_default=product.default,
    )
