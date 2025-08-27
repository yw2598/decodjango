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

    ceiling = models.CharField(max_length=255, blank=True, null=True, verbose_name="吊顶")
    side_wall = models.CharField(max_length=255, blank=True, null=True, verbose_name="侧壁")
    rear_wall = models.CharField(max_length=255, blank=True, null=True, verbose_name="后壁")
    floor = models.CharField(max_length=255, blank=True, null=True, verbose_name="地坪")
    front_wall = models.CharField(max_length=255, blank=True, null=True, verbose_name="前壁")

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
    

class UserSelection(models.Model):
    user_id = models.IntegerField(verbose_name="用户ID", db_index=True)
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="选择时间", db_index=True)

    # 只保留一个 product 字段！先允许可空，迁移后回填再改非空
    product = models.ForeignKey(
        'Product',
        on_delete=models.PROTECT,
        verbose_name="产品",
        db_index=True,
        null=True,
        blank=True,
    )

    # 快照字段，先允许可空，回填后可再改为非空
    snapshot_model_number = models.CharField(max_length=100, null=True, blank=True, verbose_name="快照-型号")
    snapshot_product_type = models.CharField(max_length=100, null=True, blank=True, verbose_name="快照-梯型")
    snapshot_style = models.CharField(max_length=100, null=True, blank=True, verbose_name="快照-风格")
    snapshot_preset = models.CharField(max_length=100, null=True, blank=True, verbose_name="快照-预设配置")
    snapshot_default = models.BooleanField(default=False, verbose_name="快照-是否默认")

    class Meta:
        verbose_name = "用户选配记录"
        verbose_name_plural = "用户选配记录"
        ordering = ['-timestamp']

    def __str__(self):
        return f"User {self.user_id} -> Product {self.product_id} @ {self.timestamp:%Y-%m-%d %H:%M:%S}"
