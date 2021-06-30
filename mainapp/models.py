from django.db import models
from django.db.models.fields.files import ImageField
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType

User=get_user_model()


#1 Category
#2 Product
#3 Cartproduct
#4 Cart
#5 Order
#----------
#6 Customer
#7 Specification

class Category(models.Model):
    name=models.CharField(max_length=255, verbose_name='Name category')
    slug=models.SlugField(unique=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    category=models.ForeignKey(Category, verbose_name='Category', on_delete=models.CASCADE)
    title = models.CharField(max_length=255, verbose_name='Name')
    slug=models.SlugField(unique=True)
    image=models.ImageField(verbose_name='Image')
    description= models.TextField(verbose_name='Descriptions', null=True)
    price=models.DecimalField(max_digits=9, decimal_places=2,verbose_name='Price')

    def __str__(self):
        return self.title 

class Cartproduct(models.Model):

    user=models.ForeignKey('Customer', verbose_name='Buyer', on_delete=models.CASCADE)
    cart=models.ForeignKey('Cart', verbose_name='Basket', on_delete=models.CASCADE, related_name='related_products')
    product=models.ForeignKey(Product,verbose_name='Goods', on_delete=models.CASCADE)
    qty=models.PositiveBigIntegerField(default=1)   
    final_price=models.DecimalField(max_digits=9, decimal_places=2,verbose_name='Total price')

    def __str__(self):
        return 'Product: {} (for the basket)'.format(self.product.title)

class Cart(models.Model):

    owner=models.ForeignKey('Customer', verbose_name='Owner', on_delete=models.CASCADE)
    products=models.ManyToManyField(Cartproduct, blank=True, related_name='related_cart')
    total_products=models.PositiveBigIntegerField(default=0)
    final_price=models.DecimalField(max_digits=9, decimal_places=2,verbose_name='Total price') 

    def __str__(self):
        return str(self.id)

class Customer(models.Model):

    user=models.ForeignKey(User, verbose_name='User',on_delete=models.CASCADE)  
    phone=models.CharField(max_length=20, verbose_name='Phone number')
    address=models.CharField(max_length=255, verbose_name='Address')

    def __str__(self):
        return 'Buyer: {} {}'.format(self.user.first_name, self.user.last_name)

class Specification(models.Model):

    content_type=models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id=models.PositiveBigIntegerField()
    name=models.CharField(max_length=255, verbose_name='Product name for characteristics')

    def __str__(self):
        return 'Characteristics for product: {}'.format(self.name)  
