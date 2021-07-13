import sys
from django.db import models
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.urls import reverse
from sys import *
from PIL import Image
from io import BytesIO

User=get_user_model()

def get_models_for_count(*model_names):
    return [models.Count(model_name) for model_name in model_names]

def get_product_url(obj, viewname,): 
    ct_model = obj.__class__._meta.model_name
    return reverse(viewname, kwargs={'ct_model': ct_model, 'slug': obj.slug})


class MinResolutionErrorException(Exception):
    pass

class MaxResolutionErrorException(Exception):
    pass

class LatestProductsManager:

    @staticmethod
    def get_products_for_main_page(*args, **kwargs):
        with_respect_to=kwargs.get('with_respect_to')
        products=[]
        ct_models= ContentType.objects.filter(model__in=args)
        for ct_model in ct_models:
            model_products= ct_model.model_class()._base_manager.all().order_by('-id')[:5]
            products.extend(model_products)
        if with_respect_to:
            ct_model=ContentType.objects.filter(model=with_respect_to)
            if ct_model.exists():
                if with_respect_to in args:
                    return sorted(
                        products, key=lambda x: x.__class__._meta.model_name.startswith(with_respect_to), reverse=True
                        )
        return products 


class LatestProducts:

    objects=LatestProductsManager()

class CategoryManager(models.Manager):

    CATEGORY_NAME_COUNT_NAME={
        'Notebooks': 'notebook__count',
        'Smartphones': 'smartphone__count'
    }

    def get_queryset(self):
        return super().get_queryset()
    
    def get_categories_for_left_sidebar(self):
        models = get_models_for_count('notebook', 'smartphone')
        qs = list(self.get_queryset().annotate(*models).values())
        return [dict(name=c['name'], slug=c['slug'], count=c[self.CATEGORY_NAME_COUNT_NAME[c['name']]]) for c in qs]

class Category(models.Model):
    name=models.CharField(max_length=255, verbose_name='Name category')
    slug=models.SlugField(unique=True)
    objects = CategoryManager()

    def __str__(self):
        return self.name

class Product(models.Model):

    MIN_RESOLUTION=(400,400)
    MAX_RESOLUTION=(800,800)
    MAX_IMAGE_SIZE=3145728

    class Meta:
        abstract=True
    
    category=models.ForeignKey(Category, verbose_name='Category', on_delete=models.CASCADE)
    title = models.CharField(max_length=255, verbose_name='Name')
    slug=models.SlugField(unique=True)
    image=models.ImageField(verbose_name='Image')
    description= models.TextField(verbose_name='Descriptions', null=True)
    price=models.DecimalField(max_digits=9, decimal_places=2,verbose_name='Price')

    def __str__(self):
        return self.title

#____________________________________#
    def save(self, *args, **kwargs):
        # image = self.image
        # img = Image.open(image)
        # min_height, min_width= self.MIN_RESOLUTION
        # max_height, max_width= self.MAX_RESOLUTION=(800,800)
        # if img.height < min_height or img.width < min_width:
        #     raise MinResolutionErrorException('Resolution image less minimum!')
        # if img.height > max_height or img.width > max_width:
        #     raise MaxResolutionErrorException('Resolution image more maximum!') 
        image=self.image
        img= Image.open(image)
        new_img=img.convert('RGB')
        resize_new_img=new_img.resize((200,200),Image.ANTIALIAS)
        filestream=BytesIO()
        resize_new_img.save(filestream, 'JPEG', quality=90)
        filestream.seek(0)
        name= '{}.{}'.format(*self.image.name.split('.'))
        self.image=InMemoryUploadedFile(
            filestream, 'ImageField', name, 'jpeg/image', sys.getsizeof(filestream), None
        )

        super().save(*args, **kwargs)
#____________________________________#

class Notebook(Product):
    diagonal = models.CharField(max_length=255, verbose_name='Diagonal')
    display_type = models.CharField(max_length=255, verbose_name='Diagonal type')
    processor_freq = models.CharField(max_length=255, verbose_name='Processor frequency')
    ram = models.CharField(max_length=255, verbose_name='RAM')
    video = models.CharField(max_length=255, verbose_name='Video card')
    time_withoud_charge= models.CharField(max_length=255, verbose_name='Time work battery')

    def __str__(self):
        return "{} : {}".format(self.category.name, self.title)
    
    def get_absolute_url(self):
        return get_product_url(self, 'product_detail')

class Smartphone(Product):

    diagonal = models.CharField(max_length=255, verbose_name='Diagonal')
    display_type = models.CharField(max_length=255, verbose_name='Diagonal type')
    resolution = models.CharField(max_length=255, verbose_name='Resolution')
    accum_volume = models.CharField(max_length=255, verbose_name='Battery volume')
    ram = models.CharField(max_length=255, verbose_name='RAM')
    sd = models.BooleanField(default=True, verbose_name='SD card availability')
    sd_volume_max = models.CharField(
        max_length=255, null=True, blank=True, verbose_name='Max volume SD card'
    )
    main_cam_md = models.CharField(max_length=255, verbose_name='Main camera')
    frontal_cam_mp = models.CharField(max_length=255, verbose_name='Frontal camera')

    def __str__(self):
        return '{} : {}'.format(self.category.name, self.title)
    
    def get_absolute_url(self):
        return get_product_url(self, 'product_detail')

    # @property
    # def sd(self):
    #     if self.sd:
    #         return 'Yes'
    #     return 'No'

class CartProduct(models.Model):

    user=models.ForeignKey('Customer', verbose_name='Buyer', on_delete=models.CASCADE)
    cart=models.ForeignKey('Cart', verbose_name='Basket', on_delete=models.CASCADE, related_name='related_products')
    content_type=models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id=models.PositiveIntegerField()
    content_object=GenericForeignKey('content_type', 'object_id')
    qty=models.PositiveIntegerField(default=1)   
    final_price=models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Total price')

    def __str__(self):
        return "Product: {} (for the basket)".format(self.content_object.title)

class Cart(models.Model):

    owner=models.ForeignKey('Customer', verbose_name='Owner', on_delete=models.CASCADE)
    products=models.ManyToManyField(CartProduct, blank=True, related_name='related_cart')
    total_products=models.PositiveBigIntegerField(default=0)
    final_price=models.DecimalField(max_digits=9, decimal_places=2,verbose_name='Total price')
    in_order= models.BooleanField(default=False)
    for_anonymous_user= models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)

class Customer(models.Model):

    user=models.ForeignKey(User, verbose_name='User',on_delete=models.CASCADE)  
    phone=models.CharField(max_length=20, verbose_name='Phone number')
    address=models.CharField(max_length=255, verbose_name='Address')

    def __str__(self):
        return "Buyer: {} {}".format(self.user.first_name, self.user.last_name)

