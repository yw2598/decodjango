from django.db import models

def product_image_upload_path(instance, filename):
    # instance 是 Product 实例
    # 注意 preset/model_number 里可能有特殊字符，建议处理下
    model_number = instance.model_number or "unknown"
    preset = instance.preset or "标配"
    return f"products/{model_number}/{preset}/{filename}"


class Product(models.Model):
    model_number = models.CharField(max_length=100, verbose_name="型号")
    product_type = models.CharField(max_length=100, verbose_name="梯型")
    style = models.CharField(max_length=100, blank=True, null=True, verbose_name="风格")  # 新增字段
    preset = models.CharField(max_length=100,blank=False,null=False,default="标配",verbose_name="预设配置")
    default = models.BooleanField(default=False, verbose_name="是否默认型号配置")
    configurations = models.JSONField(default=list, blank=True, verbose_name="产品配置")
    cop = models.ForeignKey('COP',on_delete=models.SET_NULL,blank=True,null=True,verbose_name="操纵箱（COP）")
    main_image = models.ImageField(upload_to=product_image_upload_path, blank=True, null=True, verbose_name="主图")
    detail_image_1 = models.ImageField(upload_to=product_image_upload_path, blank=True, null=True, verbose_name="细节图1")
    detail_image_2 = models.ImageField(upload_to=product_image_upload_path, blank=True, null=True, verbose_name="细节图2")
    detail_image_3 = models.ImageField(upload_to=product_image_upload_path, blank=True, null=True, verbose_name="细节图3")
    main_image_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="主图名称")
    detail_image_1_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="细节图1名称")
    detail_image_2_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="细节图2名称")
    detail_image_3_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="细节图3名称")

    def __str__(self):
        return f"{self.model_number} - {self.product_type}"


class StaticAsset(models.Model):
    file_name = models.CharField(max_length=255, unique=True, verbose_name="文件名")
    image = models.ImageField(upload_to='static_assets/', verbose_name="图片")

    def __str__(self):
        return self.file_name
    

class COP(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="COP名称")
    description = models.TextField(blank=True, null=True, verbose_name="描述")
    image = models.ImageField(upload_to='cops/', blank=True, null=True, verbose_name="COP图片")  # 新增字段

    def __str__(self):
        return self.name