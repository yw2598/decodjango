from django.contrib import admin
from .models import Product
from .models import StaticAsset,COP
# 需要先安装 django-json-widget：pip install django-json-widget
from django_json_widget.widgets import JSONEditorWidget
from django.db import models

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'model_number', 'product_type','preset', 'main_image','cop')
    search_fields = ('model_number', 'product_type')
    formfield_overrides = {
        models.JSONField: {'widget': JSONEditorWidget},
    }
    fieldsets = (
        (None, {
            'fields': (
                'model_number', 
                'product_type', 
                'style', 
                'preset',         # ← 加在这里
                'default',    
                'cop',      
                'configurations'
            )
        }),
        ('图片', {
            'fields': (
                'main_image', 'main_image_name',
                'detail_image_1', 'detail_image_1_name',
                'detail_image_2', 'detail_image_2_name',
                'detail_image_3', 'detail_image_3_name'
            )
        }),
    )


@admin.register(StaticAsset)
class StaticAssetAdmin(admin.ModelAdmin):
    list_display = ('file_name', 'image')



@admin.register(COP)
class COPAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'image')
    search_fields = ('name',)