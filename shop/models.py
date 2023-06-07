from django.db import models
from django.contrib.auth.models import User


class Product(models.Model):
    product_id = models.AutoField
    product_name = models.CharField(max_length=50)
    category = models.CharField(max_length=50, default="")
    subcategory = models.CharField(max_length=50, default="")
    label = models.CharField(max_length=50, default="")
    price = models.IntegerField(default=0)
    desc = models.CharField(max_length=5000)
    pub_date = models.DateField()
    main_image = models.ImageField(upload_to="shop/images", default="")
    image2 = models.ImageField(upload_to="shop/images/", default="", blank=True)
    image3 = models.ImageField(upload_to="shop/images/", default="", blank=True)
    image4 = models.ImageField(upload_to="shop/images/", default="", blank=True)
    size = models.JSONField(default=[])
    color = models.JSONField(default=[])
    material = models.CharField(max_length=200, default="")
    care = models.CharField(max_length=200, default="")

    objects = models.manager

    def __str__(self):
        return self.product_name


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=100, null=True)
    objects = models.manager

    def __str__(self):
        return str(self.id)

    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        return total

    def get_cart_items(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total

    def get_wishlist_total(self):
        wishlistitems = self.wishlistitem_set.all()
        total = sum([item.get_total for item in wishlistitems])
        return total

    def get_wishlist_items(self):
        wishlistitems = self.wishlistitem_set.all()
        total = sum([item.quantity for item in wishlistitems])
        return total


class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    color = models.CharField(max_length=50, null=True, )
    size = models.CharField(max_length=50, null=True, )
    date_added = models.DateTimeField(auto_now_add=True)
    objects = models.manager

    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total


class WishlistItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    color = models.CharField(max_length=50, null=True, )
    size = models.CharField(max_length=50, null=True, )
    date_added = models.DateTimeField(auto_now_add=True)
    objects = models.manager

    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total


class ShippingAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    address = models.CharField(max_length=200, null=True)
    city = models.CharField(max_length=200, null=True)
    state = models.CharField(max_length=200, null=True)
    zipcode = models.CharField(max_length=200, null=True)
    date_added = models.DateTimeField(auto_now_add=True)
    objects = models.manager

    def __str__(self):
        return self.address
