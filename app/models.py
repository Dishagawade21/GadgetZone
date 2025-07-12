from django.db import models
from viewflow.fields import CompositeKey


class Category(models.Model):
    id = models.TextField(primary_key=True)
    name = models.TextField()

    class Meta:
        db_table = 'tblCategory'


class Subcategory(models.Model):
    id = models.TextField(primary_key=True)
    master = models.TextField()
    name = models.TextField()

    class Meta:
        db_table = 'tblSubcategory'


class Brand(models.Model):
    id = models.TextField(primary_key=True)
    name = models.TextField()

    class Meta:
        db_table = 'tblBrand'


class Product(models.Model):
    id = models.TextField(primary_key=True)
    master = models.TextField()
    sub = models.TextField()
    brand = models.TextField()
    name = models.TextField()
    mrp = models.FloatField()
    discount = models.IntegerField()
    price = models.FloatField()
    description = models.TextField()
    # done a change here
    productCount = models.IntegerField() 

    class Meta:
        db_table = 'tblProduct'


class User(models.Model):
    id = models.TextField(primary_key=True)
    name = models.TextField()
    email = models.TextField()
    mobile = models.TextField()
    address = models.TextField()
    password = models.TextField()

    class Meta:
        db_table = 'tblUser'


class Cart(models.Model):
    id = CompositeKey(columns=['uid', 'pid'])
    uid = models.TextField()
    pid = models.TextField()
    name = models.TextField()
    description = models.TextField()
    price = models.FloatField()
    qty = models.IntegerField()
    total = models.FloatField()

    class Meta:
        db_table = 'tblCart'
        unique_together = (('uid', 'pid'),)


class Order(models.Model):
    id = models.TextField(primary_key=True)
    date = models.TextField()
    uid = models.TextField()
    ordertotal = models.FloatField()
    bname = models.TextField()
    baddress = models.TextField()
    bcontact = models.TextField()

    class Meta:
        db_table = 'tblOrder'


class OrderDetails(models.Model):
    id = CompositeKey(columns=['orderid', 'pid'])
    orderid = models.TextField()
    pid = models.TextField()
    name = models.TextField()
    description = models.TextField()
    price = models.FloatField()
    qty = models.IntegerField()
    total = models.FloatField()
    status = models.TextField()

    class Meta:
        db_table = 'tblOrderDetails'
        unique_together = (('orderid', 'pid'),)


class Feedback(models.Model):
    id = models.TextField(primary_key=True)
    date = models.TextField()
    pname = models.TextField()
    uid = models.TextField()
    message = models.TextField()
    rating = models.TextField()

    class Meta:
        db_table = 'tblFeedback'
