from rest_framework import serializers
from .models import Product,COP

class COPSerializer(serializers.ModelSerializer):
    class Meta:
        model = COP
        fields = ['id', 'name', 'description', 'image']  # 按你需要返回哪些字段

class ProductSerializer(serializers.ModelSerializer):
    cop = COPSerializer()  # 用嵌套序列化器替换原来默认的id
    class Meta:
        model = Product
        fields = '__all__'

