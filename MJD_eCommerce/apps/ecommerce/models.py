from django.db import models

# 老板信息
class Boss(models.Model):
    bossName = models.CharField(max_length=100)
    account = models.CharField(max_length=255)
    password = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# 用户信息
class User(models.Model):
    userName = models.CharField(max_length=100)
    account = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    dateOfBirth = models.CharField(max_length=12)
    password = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class UserAddress(models.Model):
    user = models.ForeignKey(User, related_name="userAddress", on_delete=models.CASCADE)
    country = models.CharField(max_length=50)
    province = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    street = models.CharField(max_length=100)
    room = models.CharField(max_length=50)
    zipcode = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# 产品信息
class Product(models.Model):
    seller = models.ForeignKey(Boss, related_name="seller", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=100) 
    color = models.CharField(max_length=10)
    price = models.DecimalField(max_digits=11, decimal_places=2)
    description = models.TextField()
    img1 = models.ImageField(upload_to='media/')
    img2 = models.ImageField(upload_to='media/', null=True, blank=True)
    img3 = models.ImageField(upload_to='media/', null=True, blank=True)
    img4 = models.ImageField(upload_to='media/', null=True, blank=True)
    img5 = models.ImageField(upload_to='media/', null=True, blank=True)
    img6 = models.ImageField(upload_to='media/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class ProductDetail(models.Model):
    product = models.ForeignKey(Product, related_name="productInDetail", on_delete=models.CASCADE)
    quantity = models.IntegerField()
    size = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# 购物车
class ShoppingCart(models.Model):
    customer = models.ForeignKey(User, related_name="shoppingCustomer", on_delete=models.CASCADE)
    item = models.ForeignKey(ProductDetail, related_name="inCartItem", on_delete=models.CASCADE)
    itemQuantity = models.IntegerField()
    price = models.DecimalField(max_digits=11, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


# 产品评论
class ProductReview(models.Model):
    reviewProduct = models.ForeignKey(Product, related_name="reviewProduct", on_delete=models.CASCADE)
    reviewer = models.ForeignKey(User, related_name="reviewer", on_delete=models.CASCADE)
    rate = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class ProductLike(models.Model):
    likeProduct = models.ForeignKey(Product, related_name="likeProduct", on_delete=models.CASCADE)
    likeUser = models.ForeignKey(User, related_name="likeUser", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


# 交易记录 
class Confirmation(models.Model):
    comfirmNumber = models.CharField(max_length=255)
    buyer = models.ForeignKey(User, related_name="buyer", on_delete=models.CASCADE)
    salePrice = models.DecimalField(max_digits=9, decimal_places=2)
    shippingAddress = models.TextField()
    paymentStatus = models.BooleanField(default=False)
    shippingStatus = models.BooleanField(default=False) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class SoldItem(models.Model):
    sale = models.ForeignKey(Confirmation, related_name="productSold", on_delete=models.CASCADE)
    soldProduct = models.CharField(max_length=255)
    quantity = models.IntegerField()
    size = models.CharField(max_length=10)
    color = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# 客服
class ServiceInfo(models.Model):
    name = models.CharField(max_length=100)
    qrCode= models.ImageField(upload_to='media/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# 广告
class Advertisement(models.Model):
    ad = models.ImageField(upload_to='media/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# 收款二维码
class Payment(models.Model):
    qrCode = models.ImageField(upload_to='media/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class PaymentSecurity(models.Model):
    password = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


