from django.shortcuts import render,redirect
from .models import *
from django.contrib import messages
import bcrypt
from django.db.models import Avg, Max, Min, Count
import datetime
from django.db.models import Q


# 打开主页
def home(request):
    if 'userID' in request.session:
        return redirect('/userHome/{}'.format(request.session['userID']))

    product = Product.objects.all()
    ad = Advertisement.objects.all()
    context = {
        'products': product,
        'ad': ad,
    }
    return render(request, 'home.html', context)

# 老板登陆页面
def bossRegLogPage(request):
    return render(request, 'bossRegLog.html')

# 老板注册
def bossReg(request):
    form = request.POST
    error = []
    exist_account = Boss.objects.filter(account=form['account'])
        
    if len(form['name'])<2:
        error.append("姓名最少包含2个文字")

    if len(form['password'])<6:
        error.append("密码最少6位数")

    if not form['password'] == form['password_comfirm']:
        error.append('您输入的密码与确认密码不相同')

    if len(exist_account)>0:
        error.append('这个账号已被注册')

    if error:
        for e in error:
            messages.error(request, e)       
    else:
        hashed_pw = bcrypt.hashpw(form['password'].encode(), bcrypt.gensalt())
        correct_hashed_pw = hashed_pw.decode('utf-8')
        new_boss = Boss.objects.create(bossName=form['name'],account=form['account'],password=correct_hashed_pw)
        request.session['userID']=new_boss.id

    return redirect('/mjdboss')

# 老板登陆
def bossLog(request):
    form = request.POST
    if form['account']:
        try:
            boss = Boss.objects.get(account=form['account'])
        except:
            messages.error(request, '这个账号还未注册')
            return redirect('/mjdboss')
    else:
        messages.error(request, '请输入账号')
        return redirect('/mjdboss')

    if form['password']:
        check = bcrypt.checkpw(request.POST['password'].encode(), boss.password.encode())
        if check:
            request.session['bossID'] = boss.id
            return redirect('/boss/{}'.format(request.session['bossID']))
        else:
            messages.error(request,'密码错误')
            return redirect('/mjdboss')
    else:
        messages.error(request,'请输入密码')
        return redirect('/mjdboss')
    

# 老板主页
def bossPage(request,bossID):
    if not 'bossID' in request.session:
        messages.error(request, '您需要先登陆')
        return redirect('/mjdboss')

    if not request.session['bossID'] == bossID:
        messages.error(request, '您没有权限访问该页面')
        return redirect('/boss/{}'.format(request.session['bossID']))
    boss = Boss.objects.get(id=bossID)
    products = Product.objects.all()
    todo = Confirmation.objects.filter(Q(paymentStatus=False) | Q(shippingStatus=False)).distinct().count() 
    context={
        'thisBoss': boss,
        'products': products,
        'todo': todo,
    }
    return render(request, 'bossPage.html', context)

# 搜索商品
def search(request):
    form = request.GET
    target = Product.objects.filter(name=form['search'])
    if not target:
        target = Product.objects.filter(category__contains=form['search'])

    if not target:
        for i in form['search']:
            if not target:
                target = Product.objects.filter(color__contains=i)
                 
    if 'bossID' in request.session:
        print('boss search')
        boss = Boss.objects.get(id=request.session['bossID'])
        todo = Confirmation.objects.filter(Q(paymentStatus=False) | Q(shippingStatus=False)).distinct().count() 
        context={
            'thisBoss': boss,
            'products': target,
            'todo': todo,
        }
        return render(request,'bossPage.html', context)
    
    if 'userID' in request.session:
        print('user search')
        user = User.objects.get(id=request.session['userID'])
        context={
            'thisUser': user,
            'products': target,
        }
        return render(request,'userHome.html', context)

    else:
        print('guest search')
        context={
            'products': target,
        }
        return render(request,'home.html', context)
    
    

# 添加新产品页面
def newProductPage(request,bossID):
    if not 'bossID' in request.session:
        messages.error(request, '您需要先登陆')
        return redirect('/mjdboss')
    if not request.session['bossID'] == bossID:
        messages.error(request, '您没有权限访问该页面')
        return redirect('/boss/{}'.format(request.session['bossID']))
    todo = Confirmation.objects.filter(Q(paymentStatus=False) | Q(shippingStatus=False)).distinct().count() 
    context={
        'thisBoss': Boss.objects.get(id=bossID),
        'todo':todo,
    }
    return render(request,'addProduct.html',context)

# 添加新商品
def addProduct(request,bossID):
    if not 'bossID' in request.session:
        messages.error(request, '您需要先登陆')
        return redirect('/mjdboss')
    if not request.session['bossID'] == bossID:
        messages.error(request, '您没有权限访问该页面')
        return redirect('/boss/{}'.format(request.session['bossID']))
    form = request.POST
    error = []
    cate = ''
          
    if len(form['name'])<1:
        error.append("请填写该商品的名称")
    if len(form['price'])<1:
        error.append("请填写该商品的价格")
    if len(form['color'])<1:
        error.append("请填写该商品的颜色")
    if len(form['size'])<1:
        error.append("请填写该商品的尺码")
    if len(form['quantity'])<1:
        error.append("请填写该商品的上架数量")
    if len(form['description'])<1:
        error.append("请填写该商品的简介")
    if form['cate0']:
        for i in range(4):
            if form['cate{}'.format(i)]:
                cate = cate + form['cate{}'.format(i)]
            if i<3:
                if form['cate{}'.format(i+1)]:
                    cate = cate + '/'  
    else:
        error.append('类别第一栏不能为空')  
    if not cate:
        error.append("请为该产品添加最少一种类别")
    if not request.FILES.get('img1'):
        error.append("请上传一张产品封面图片")
    if error:
        error.append("商品添加失败") 
        for e in error:
            messages.error(request, e)
    else:
        boss = Boss.objects.get(id = bossID)
        new_product = Product.objects.create(seller=boss, name=form['name'], category=cate, color=form['color'], price=form['price'], description=form['description'], img1=request.FILES['img1'])
        if request.FILES.get('img2'):
            new_product.img2 = request.FILES['img2']
            new_product.save()
        if request.FILES.get('img3'):
            new_product.img3 = request.FILES['img3']
            new_product.save()
        if request.FILES.get('img4'):
            new_product.img4 = request.FILES['img4']
            new_product.save()
        if request.FILES.get('img5'):
            new_product.img5 = request.FILES['img5']
            new_product.save()
        if request.FILES.get('img6'):
            new_product.img6 = request.FILES['img6']
            new_product.save()
        new_detail = ProductDetail.objects.create(product=new_product, size=form['size'], quantity=form['quantity'])    
    return redirect('/boss/newProductPage/{}'.format(bossID))

# 产品详情，老板页面
def bossProductDetailPage(request, productID, bossID):
    if not 'bossID' in request.session:
        messages.error(request, '您需要先登陆')
        return redirect('/mjdboss')
    if not request.session['bossID'] == bossID:
        messages.error(request, '您没有权限访问该页面')
        return redirect('/boss/{}'.format(request.session['bossID']))
    boss = Boss.objects.get(id=bossID)
    product = Product.objects.get(id=productID)
    detail = ProductDetail.objects.filter(product=Product.objects.get(id=productID))
    cate = Product.objects.get(id=productID).category.split('/')
    cate1 = cate[0]
    if len(cate) > 1:
        cate2 = cate[1]
    else:
        cate2 = ''
    if len(cate) > 2:
        cate3 = cate[2]
    else:
        cate3 = ''
    if len(cate) > 3:
        cate4 = cate[3]
    else:
        cate4 = ''

    todo = Confirmation.objects.filter(Q(paymentStatus=False) | Q(shippingStatus=False)).distinct().count() 

    context={
        'thisBoss': boss,
        'product': product,
        'detail': detail, 
        'cate1': cate1,
        'cate2': cate2,
        'cate3': cate3,
        'cate4': cate4,
        'todo':todo,
    }
    return render(request, 'bossProductDetail.html',context)

# 更新产品信息
def updateProduct(request, productID):
    if not 'bossID' in request.session:
        messages.error(request, '您需要先登陆')
        return redirect('/mjdboss')

    form = request.POST
    error = []
    this_product = Product.objects.get(id=productID)
    if form['name']:
        this_product.name = form['name']
    if form['price']:
        this_product.price = form['price']
    if form['color']:
        this_product.color = form['color']

    cate = ''
    if form['cate0']:
        for i in range(4):
            if form['cate{}'.format(i)]:
                cate = cate + form['cate{}'.format(i)]
            if i<3:
                if form['cate{}'.format(i+1)]:
                    cate = cate + '/'  
    else:
        error.append('类别第一栏不能为空')       
    if cate:
        this_product.category = cate
    
    if form['description']:
        this_product.description = form['description']

    if error:   
        error.append("更商品详情存失败")
        for e in error:
            messages.error(request, e)
    else:
        this_product.save()

    return redirect('/boss/product/detail/{}'.format(productID) + '/{}'.format(request.session['bossID']))

# 添加新的产品尺码
def addSize(request, productID):
    if not 'bossID' in request.session:
        messages.error(request, '您需要先登陆')
        return redirect('/mjdboss')

    form = request.POST
    error = []
    this_product = Product.objects.get(id=productID)
    exist_product = ProductDetail.objects.filter(product=this_product)
    exist_size = []
    for i in exist_product:
        if i.size == form['size']:
            exist_size.append(i.size)
    if len(form['size'])<1:
        error.append("请填写该商品的尺码")
    if len(exist_size)>0:
        error.append("这个尺码已经存在")
    if len(form['quantity'])<1:
        error.append("请填写该尺码的上架数量")
    else:
        if int(form['quantity'])<0:
            error.append("上架数量必须大于0")

    if error:
        error.append("添加新尺码失败") 
        for e in error:
            messages.error(request, e)
    else:
        new_detail = ProductDetail.objects.create(product=this_product, quantity=form['quantity'], size=form['size'])

    return redirect('/boss/product/detail/{}'.format(productID) + '/{}'.format(request.session['bossID']))

# 删除产品尺码
def deleteSize(request, sizeID):
    if not 'bossID' in request.session:
        messages.error(request, '您需要先登陆')
        return redirect('/mjdboss')

    size = ProductDetail.objects.get(id=sizeID)
    size.delete()
    return redirect('/boss/product/detail/{}'.format(size.product.id) + '/{}'.format(request.session['bossID']))

# 更新商品上架数量
def updateQuantity(request, productID, detailID):
    if not 'bossID' in request.session:
        messages.error(request, '您需要先登陆')
        return redirect('/mjdboss')

    form = request.POST
    this_quantity = ProductDetail.objects.get(id=detailID)
    error = []
    if form['quantity']:
        if int(form['quantity']) > -1:
            this_quantity.quantity = form['quantity']
            this_quantity.save()
        else:
            error.append("新的货存数量必须大于等于0")
    
    if error:   
        error.append("更新货存失败")
        for e in error:
            messages.error(request, e)
    return redirect('/boss/product/detail/{}'.format(productID) + '/{}'.format(request.session['bossID']))

# 更新产品图片
def updateImg(request, productID, imgID):
    if not 'bossID' in request.session:
        messages.error(request, '您需要先登陆')
        return redirect('/mjdboss')

    error = []
    if not request.FILES.get('img'):
        error.append("上传图片不能为空")
        if error:
            error.append("更新产品信息失败") 
            for e in error:
                messages.error(request, e)
    else:
        this_product = Product.objects.get(id=productID)
        if imgID == 1:
            this_product.img1 = request.FILES['img']
            
        if imgID == 2:
            this_product.img2 = request.FILES['img']
            
        if imgID == 3:
            this_product.img3 = request.FILES['img']
            
        if imgID == 4:
            this_product.img4 = request.FILES['img']
            
        if imgID == 5:
            this_product.img5 = request.FILES['img']
            
        if imgID == 6:
            this_product.img6 = request.FILES['img']

        this_product.save()
       
    return redirect('/boss/product/detail/{}'.format(productID) + '/{}'.format(request.session['bossID']))

# 删除产品图片
def deleteImg(request, productID, imgID):
    if not 'bossID' in request.session:
        messages.error(request, '您需要先登陆')
        return redirect('/mjdboss')

    this_product = Product.objects.get(id=productID)
    if imgID == 2:
        img = this_product.img2
    if imgID == 3:
        img = this_product.img3
    if imgID == 4:
        img = this_product.img4
    if imgID == 5:
        img = this_product.img5
    if imgID == 6:
        img = this_product.img6
    img.delete()
    return redirect('/boss/product/detail/{}'.format(productID) + '/{}'.format(request.session['bossID']))

# 删除产品
def deleteProduct(request, productID, bossID):
    if not 'bossID' in request.session:
        messages.error(request, '您需要先登陆')
        return redirect('/mjdboss')

    product = Product.objects.get(id=productID)
    detail = ProductDetail.objects.filter(product=product)
    product.delete()
    detail.delete()
    return redirect('/boss/{}'.format(bossID))

# 编辑老板账户页面
def editBossAccountPage(request, bossID):
    if not 'bossID' in request.session:
        messages.error(request, '您需要先登陆')
        return redirect('/mjdboss')
    if not request.session['bossID'] == bossID:
        messages.error(request, '您没有权限访问该页面')
        return redirect('/boss/{}'.format(request.session['bossID']))
    
    account = Boss.objects.get(id=bossID)
    todo = Confirmation.objects.filter(Q(paymentStatus=False) | Q(shippingStatus=False)).distinct().count() 
    context = {
        'thisBoss': account,
        'todo':todo,
    }
    return render(request, 'bossEditAccount.html', context)

# 编辑商城页面
def webAdmin(request,bossID):
    if not 'bossID' in request.session:
        messages.error(request, '您需要先登陆')
        return redirect('/mjdboss')
    if not request.session['bossID'] == bossID:
        messages.error(request, '您没有权限访问该页面')
        return redirect('/boss/{}'.format(request.session['bossID']))
    
    boss = Boss.objects.get(id=bossID)
    server = ServiceInfo.objects.all()
    ad = Advertisement.objects.all()
    payment = Payment.objects.all()
    todo = Confirmation.objects.filter(Q(paymentStatus=False) | Q(shippingStatus=False)).distinct().count() 
    check = ''
    if len(payment)>1:
        check = 'ok'
    context = {
        'thisBoss': boss,
        'server': server,
        'ad': ad,
        'payment': payment,
        'check': check,
        'todo':todo,
    }
    return render(request, 'webAdmin.html', context)

# 添加客服
def addService(request, bossID):
    if not 'bossID' in request.session:
        messages.error(request, '您需要先登陆')
        return redirect('/mjdboss')
    if not request.session['bossID'] == bossID:
        messages.error(request, '您没有权限访问该页面')
        return redirect('/boss/{}'.format(request.session['bossID']))

    form = request.POST
    error = []
    if len(form['name'])<1:
        error.append("请填客服名称")
    if not request.FILES.get('img'):
        error.append("请上传客服二维码")
    if error:
        error.append("客服添加失败") 
        for e in error:
            messages.error(request, e)
    else:
        new_server = ServiceInfo.objects.create(name=form['name'], qrCode=request.FILES['img'])
    return redirect('/boss/webadmin/{}'.format(bossID))

# 删除客服
def deleteService(request, serviceID, bossID):
    if not 'bossID' in request.session:
        messages.error(request, '您需要先登陆')
        return redirect('/mjdboss')
    if not request.session['bossID'] == bossID:
        messages.error(request, '您没有权限访问该页面')
        return redirect('/boss/{}'.format(request.session['bossID']))
    check = ServiceInfo.objects.all()
    if len(check)>1:
        server = ServiceInfo.objects.get(id=serviceID)
        server.delete()
    
    return redirect('/boss/webadmin/{}'.format(bossID))

# 添加海报
def addAdvert(request,bossID):
    if not 'bossID' in request.session:
        messages.error(request, '您需要先登陆')
        return redirect('/mjdboss')
    if not request.session['bossID'] == bossID:
        messages.error(request, '您没有权限访问该页面')
        return redirect('/boss/{}'.format(request.session['bossID']))

    error = []
    if not request.FILES.get('img'):
        error.append("请上一张海报")

    if error:
        error.append("海报添加失败") 
        for e in error:
            messages.error(request, e)
    else:
        new_ad = Advertisement.objects.create(ad=request.FILES['img'])
    
    return redirect('/boss/webadmin/{}'.format(bossID))

# 删除海报
def deleteAd(request, adID, bossID):
    if not 'bossID' in request.session:
        messages.error(request, '您需要先登陆')
        return redirect('/mjdboss')
    if not request.session['bossID'] == bossID:
        messages.error(request, '您没有权限访问该页面')
        return redirect('/boss/{}'.format(request.session['bossID']))
    check = Advertisement.objects.all()
    if len(check)>1:
        ad = Advertisement.objects.get(id=adID)
        ad.delete()
    return redirect('/boss/webadmin/{}'.format(bossID))

# 收款安全页面
def paymentSecurity(request, bossID):
    if not 'bossID' in request.session:
        messages.error(request, '您需要先登陆')
        return redirect('/mjdboss')
    if not request.session['bossID'] == bossID:
        messages.error(request, '您没有权限访问该页面')
        return redirect('/boss/{}'.format(request.session['bossID']))
    boss = Boss.objects.get(id=bossID)
    todo = Confirmation.objects.filter(Q(paymentStatus=False) | Q(shippingStatus=False)).distinct().count() 
    context = {
        'thisBoss': boss,
        'todo':todo,
    }
    return render(request, 'paymentAdmin.html', context)

# 创建收款密码
def createSecuriry(request, bossID):
    if not 'bossID' in request.session:
        messages.error(request, '您需要先登陆')
        return redirect('/mjdboss')

    if not request.session['bossID'] == bossID:
        messages.error(request, '您没有权限访问该页面')
        return redirect('/boss/{}'.format(request.session['bossID']))

    form = request.POST
    error = []
    check = PaymentSecurity.objects.all()
    if len(check)>0:
        error.append("收款密码已被创建")
    else:
        if len(form['password'])<6:
            error.append("密码最少6位数")
        if not form['password'] == form['password_comfirm']:
            error.append('您输入的密码与确认密码不相同')
    if error:
        error.append("收款密码创建失败") 
        for e in error:
            messages.error(request, e)
        return redirect('/payment/password/{}'.format(bossID))
    else:
        hashed_pw = bcrypt.hashpw(form['password'].encode(), bcrypt.gensalt())
        correct_hashed_pw = hashed_pw.decode('utf-8')
        new_security = PaymentSecurity.objects.create(password=correct_hashed_pw)

    return redirect('/boss/webadmin/{}'.format(bossID))

# 更改收款密码
def updateSecuriry(request, bossID):
    if not 'bossID' in request.session:
        messages.error(request, '您需要先登陆')
        return redirect('/mjdboss')

    if not request.session['bossID'] == bossID:
        messages.error(request, '您没有权限访问该页面')
        return redirect('/boss/{}'.format(request.session['bossID']))

    form = request.POST
    error = []
    security = PaymentSecurity.objects.first()
    check = bcrypt.checkpw(request.POST['password'].encode(), security.password.encode())
    
    if check:
        if len(form['newPassword'])<6:
            error.append("密码最少6位数")
        if not form['newPassword'] == form['password_comfirm']:
            error.append('您输入的密码与确认密码不相同')
    else:
        error.append('收款密码错误')
        error.append('请先输入正确的收款密码再进行其他操作')

    if error:
        error.append("收款密码更新失败") 
        for e in error:
            messages.error(request, e)
        return redirect('/payment/password/{}'.format(bossID))
    else:
        hashed_pw = bcrypt.hashpw(form['newPassword'].encode(), bcrypt.gensalt())
        correct_hashed_pw = hashed_pw.decode('utf-8')
        security.password = correct_hashed_pw
        security.save()

    return redirect('/boss/webadmin/{}'.format(bossID))

# 添加收款二维码
def addPayment(request, bossID):
    if not 'bossID' in request.session:
        messages.error(request, '您需要先登陆')
        return redirect('/mjdboss')

    if not request.session['bossID'] == bossID:
        messages.error(request, '您没有权限访问该页面')
        return redirect('/boss/{}'.format(request.session['bossID']))

    error = []
    security = PaymentSecurity.objects.first()
    check = bcrypt.checkpw(request.POST['password'].encode(), security.password.encode())
    
    if not check:
        error.append('收款密码错误')
        error.append('请先输入正确的收款密码后再上传收款二维码')
    if not request.FILES.get('img'):
            error.append('请上传收款二维码')

    if error:
        error.append("收款二维码添加失败") 
        for e in error:
            messages.error(request, e)
    else:
        new_payment = Payment.objects.create(qrCode=request.FILES['img'])

    return redirect('/boss/webadmin/{}'.format(bossID))

# 删除收款二维码
def deletePayment(request, payID, bossID):
    if not 'bossID' in request.session:
        messages.error(request, '您需要先登陆')
        return redirect('/mjdboss')

    if not request.session['bossID'] == bossID:
        messages.error(request, '您没有权限访问该页面')
        return redirect('/boss/{}'.format(request.session['bossID']))

    payment = Payment.objects.get(id=payID)
    payment.delete()
    return redirect('/boss/webadmin/{}'.format(bossID))

# 更新老板账户
def updateBossAccount(request, bossID):
    if not 'bossID' in request.session:
        messages.error(request, '您需要先登陆')
        return redirect('/mjdboss')

    if not request.session['bossID'] == bossID:
        messages.error(request, '您没有权限访问该页面')
        return redirect('/boss/{}'.format(request.session['bossID']))

    form = request.POST
    boss = Boss.objects.get(id=bossID)
    check = bcrypt.checkpw(request.POST['oldPassword'].encode(), boss.password.encode())
    error = []
    if check:
        if form['name']:
            if len(form['name'])<2:
                error.append("姓名最少包含2个文字")
            else:
                boss.bossName = form['name']
        
        if form['account']:
            exist_account = Boss.objects.filter(account=form['account'])
            if len(exist_account)>0:
                if form['account'] == boss.account:
                    error.append("您正在使用这个账户，无需更新")
                else:
                    error.append('这个账号已被注册')
            else:
                boss.account = form['account']
        
        if form['newPassword']:
            if len(form['newPassword'])<6:
                error.append("密码最少6位数")
            else:  
                if not form['newPassword'] == form['password_comfirm']:
                    error.append('您输入的新密码与确认密码不相同')
                else:
                    hashed_pw = bcrypt.hashpw(form['newPassword'].encode(), bcrypt.gensalt())
                    correct_hashed_pw = hashed_pw.decode('utf-8')
                    boss.password = correct_hashed_pw    
    else:
        error.append('密码错误，请输入正确密码后再进行其他操作')

    if error:
        error.append('账户信息更新失败')
        for e in error:
            messages.error(request, e)
    else:
        boss.save()

    return redirect('/boss/editAccountPage/{}'.format(bossID))

# 老板订单管理页面
def bossOrderPage(request, bossID):
    if not 'bossID' in request.session:
        messages.error(request, '您需要先登陆')
        return redirect('/mjdboss')

    if not request.session['bossID'] == bossID:
        messages.error(request, '您没有权限访问该页面')
        return redirect('/boss/{}'.format(request.session['bossID']))

    boss = Boss.objects.get(id=bossID)
    order = Confirmation.objects.all().order_by('-created_at')
    todo = Confirmation.objects.filter(Q(paymentStatus=False) | Q(shippingStatus=False)).distinct().count() 
    context = {
        'thisBoss': boss,
        'order': order,
        'todo':todo,
    }
    return render(request,'bossOrder.html', context)

# 搜索订单
def searchOrder(request, bossID):
    if not 'bossID' in request.session:
        messages.error(request, '您需要先登陆')
        return redirect('/mjdboss')

    if not request.session['bossID'] == bossID:
        messages.error(request, '您没有权限访问该页面')
        return redirect('/boss/{}'.format(request.session['bossID']))

    form = request.GET
    boss = Boss.objects.get(id=bossID)
    order = Confirmation.objects.filter(comfirmNumber=form['search'])
    todo = Confirmation.objects.filter(Q(paymentStatus=False) | Q(shippingStatus=False)).distinct().count() 
    context = {
        'thisBoss': boss,
        'order': order,
        'todo':todo,
    }
    return render(request,'bossOrder.html', context)

def searchPay(request,bossID):
    if not 'bossID' in request.session:
        messages.error(request, '您需要先登陆')
        return redirect('/mjdboss')

    if not request.session['bossID'] == bossID:
        messages.error(request, '您没有权限访问该页面')
        return redirect('/boss/{}'.format(request.session['bossID']))

    boss = Boss.objects.get(id=bossID)
    order = Confirmation.objects.filter(paymentStatus=False)
    todo = Confirmation.objects.filter(Q(paymentStatus=False) | Q(shippingStatus=False)).distinct().count() 
    context = {
        'thisBoss': boss,
        'order': order,
        'todo':todo,
    }
    return render(request,'bossOrder.html', context)

def searchShip(request,bossID):
    if not 'bossID' in request.session:
        messages.error(request, '您需要先登陆')
        return redirect('/mjdboss')

    if not request.session['bossID'] == bossID:
        messages.error(request, '您没有权限访问该页面')
        return redirect('/boss/{}'.format(request.session['bossID']))

    boss = Boss.objects.get(id=bossID)
    order = Confirmation.objects.filter(shippingStatus=False)
    todo = Confirmation.objects.filter(Q(paymentStatus=False) | Q(shippingStatus=False)).distinct().count() 
    context = {
        'thisBoss': boss,
        'order': order,
        'todo':todo,
    }
    return render(request,'bossOrder.html', context)

# 老板查看订单详情
def bossOrderDetail(request, orderID, bossID):
    if not 'bossID' in request.session:
        messages.error(request, '您需要先登陆')
        return redirect('/mjdboss')

    if not request.session['bossID'] == bossID:
        messages.error(request, '您没有权限访问该页面')
        return redirect('/boss/{}'.format(request.session['bossID']))

    boss = Boss.objects.get(id=bossID)
    comfirm = Confirmation.objects.get(id=orderID)
    detail = SoldItem.objects.filter(sale=comfirm)
    paymentNumber = ''
    for i in range(5):
        paymentNumber += str(comfirm.comfirmNumber)[i]
    
    itemCount = 0
    for i in detail:
        itemCount += i.quantity

    todo = Confirmation.objects.filter(Q(paymentStatus=False) | Q(shippingStatus=False)).distinct().count() 

    context = {
        'thisBoss': boss,
        'comfirm': comfirm,
        'detail': detail,
        'itemCount': itemCount,
        'paymentNumber': paymentNumber,
        'todo':todo,
    }
    return render(request,'bossOrderDetail.html', context)

# 更新收款状态
def updatePayStatus(request, orderID, bossID):
    if not 'bossID' in request.session:
        messages.error(request, '您需要先登陆')
        return redirect('/mjdboss')

    if not request.session['bossID'] == bossID:
        messages.error(request, '您没有权限访问该页面')
        return redirect('/boss/{}'.format(request.session['bossID']))

    order = Confirmation.objects.get(id=orderID)
    order.paymentStatus = request.POST['tf']
    order.save()

    return redirect('/boss/orderDetail/{}'.format(orderID) + '/{}'.format(bossID))

# 更新发货状态
def updateShipStatus(request, orderID, bossID):
    if not 'bossID' in request.session:
        messages.error(request, '您需要先登陆')
        return redirect('/mjdboss')

    if not request.session['bossID'] == bossID:
        messages.error(request, '您没有权限访问该页面')
        return redirect('/boss/{}'.format(request.session['bossID']))

    order = Confirmation.objects.get(id=orderID)

    if not order.paymentStatus == True:
        messages.error(request, '请先确认收款后再更新发货状态')
    else:
        order.shippingStatus = request.POST['tf']
        order.save()

    return redirect('/boss/orderDetail/{}'.format(orderID) + '/{}'.format(bossID))

# 删除订单
def deleteOrder(request, orderID, bossID):
    if not 'bossID' in request.session:
        messages.error(request, '您需要先登陆')
        return redirect('/mjdboss')

    if not request.session['bossID'] == bossID:
        messages.error(request, '您没有权限访问该页面')
        return redirect('/boss/{}'.format(request.session['bossID']))
    form = request.POST
    boss = Boss.objects.get(id=bossID)
    check = bcrypt.checkpw(form['password'].encode(), boss.password.encode())
    
    if check:
        order = Confirmation.objects.get(id=orderID)
        sale = SoldItem.objects.filter(sale=order)
        order.delete()
        sale.delete()
        return redirect('/boss/orders/{}'.format(bossID))
    else:
        messages.error(request, '密码错误，删除失败')
        return redirect('/boss/orderDetail/{}'.format(orderID) + '/{}'.format(bossID))

# 财务报告页面
def reportPage(request, bossID):
    if not 'bossID' in request.session:
        messages.error(request, '您需要先登陆')
        return redirect('/mjdboss')
    if not request.session['bossID'] == bossID:
        messages.error(request, '您没有权限访问该页面')
        return redirect('/boss/{}'.format(request.session['bossID']))

    boss = Boss.objects.get(id=bossID)
    todo = Confirmation.objects.filter(Q(paymentStatus=False) | Q(shippingStatus=False)).distinct().count() 
    userCount = User.objects.all().count()
    bossCount = Boss.objects.all().count()
    productCount = Product.objects.all().count()
    saleCount = Confirmation.objects.all().count()
    sale = Confirmation.objects.all()
    soldItem = SoldItem.objects.all()
    soldItemCount = 0
    maxSale = 0
    minSale = 1000
    totalSale = 0
    for i in sale:
        totalSale += i.salePrice
        if i.salePrice > maxSale:
            maxSale = i.salePrice
        if i.salePrice < minSale:
            minSale = i.salePrice

    for i in soldItem:
        soldItemCount += i.quantity

    now = datetime.datetime.now()

    day = now-datetime.timedelta(days=1)
    dayTrade = Confirmation.objects.filter(created_at__gte=day, created_at__lte=now)
    day2 = now-datetime.timedelta(days=2)
    day2Trade =Confirmation.objects.filter(created_at__gte=day2, created_at__lte=day)
    daySale = 0
    day2Sale = 0
    for i in dayTrade:
        daySale += i.salePrice
    for i in day2Trade:
        day2Sale += i.salePrice

    week = now-datetime.timedelta(days=7)
    weekTrade = Confirmation.objects.filter(created_at__gte=week, created_at__lte=now)
    week2 = now-datetime.timedelta(days=14)
    week2Trade =Confirmation.objects.filter(created_at__gte=week2, created_at__lte=week)
    weekSale = 0
    week2Sale = 0
    for i in weekTrade:
        weekSale += i.salePrice
    for i in week2Trade:
        week2Sale += i.salePrice

    month= now-datetime.timedelta(days=30)
    monthTrade = Confirmation.objects.filter(created_at__gte=month, created_at__lte=now)
    month2 = now-datetime.timedelta(days=60)
    month2Trade =Confirmation.objects.filter(created_at__gte=month2, created_at__lte=month)
    monthSale = 0
    month2Sale = 0
    for i in monthTrade:
        monthSale += i.salePrice
    for i in month2Trade:
        month2Sale += i.salePrice


    season = now-datetime.timedelta(days=90)
    seasonTrade = Confirmation.objects.filter(created_at__gte=season, created_at__lte=now)
    season2 = now-datetime.timedelta(days=180)
    season2Trade =Confirmation.objects.filter(created_at__gte=season2, created_at__lte=season)
    seasonSale = 0
    season2Sale = 0
    for i in seasonTrade:
        seasonSale += i.salePrice
    for i in season2Trade:
        season2Sale += i.salePrice
    
    context = {
        'thisBoss': boss,
        'userCount': userCount,
        'bossCount': bossCount,
        'productCount': productCount,
        'totalSale': totalSale,
        'saleCount': saleCount,
        'maxSale': maxSale,
        'soldItemCount': soldItemCount,
        'minSale': minSale,
        'avgSale': round(totalSale/saleCount, 2),
        'dayTradeCount': len(dayTrade),
        'daySale': daySale,
        'day2Sale': day2Sale,
        'weekTradeCount': len(weekTrade),
        'weekSale': weekSale,
        'week2Sale': week2Sale,
        'monthTradeCount': len(monthTrade),
        'monthSale': monthSale,
        'month2Sale': month2Sale,
        'seasonTradeCount': len(seasonTrade),
        'seasonSale': seasonSale,
        'season2Sale': season2Sale,
        'todo':todo,
    }
    return render(request, 'report.html', context)

# 用户注册登陆页面
def userLogRegPage(request):
    return render(request, 'userLogReg.html')

# 用户注册
def userReg(request):
    form = request.POST
    error = []
    exist_account = User.objects.filter(account=form['account'])
    exist_phone = User.objects.filter(phone=form['phone'])

    if len(form['name'])<2:
        error.append("姓名最少包含2个文字")

    if len(form['account'])<1:
        error.append("请填写自定义账号")

    if len(form['phone'])<11:
        error.append("手机号码不符合规格，请填写11位数手机号")
    
    if not len(form['year'])==4:
        error.append("出生年份不符合规格，如：1990")
    
    if not len(form['month'])==2:
        error.append("出生月份不符合规格，如：01")
    else:
        if int(form['month'])>12:
            error.append("出生月份不符合规格,请从01至12间选择")

    if not len(form['day'])==2:
        error.append("出生日期不符合规格，如：01")
    else:
        if int(form['day'])>31:
            error.append("出生日期不符合规格,请从01至31间选择")
    
    if len(form['password'])<6:
        error.append('密码最少6位数')

    if not form['password'] == form['password_comfirm']:
        error.append('您输入的密码与确认密码不相同')

    if len(exist_account)>0:
        error.append('这个账号已被注册')

    if len(exist_phone)>0:
        error.append('这个手机已被注册')

    if error:
        error.append('注册失败')
        for e in error:
            messages.error(request, e)           
    else:
        dob = form['year']+'/'+form['month']+'/'+form['day']   
        hashed_pw = bcrypt.hashpw(form['password'].encode(), bcrypt.gensalt())
        correct_hashed_pw = hashed_pw.decode('utf-8')
        new_user = User.objects.create(userName=form['name'],account=form['account'], phone=form['phone'], dateOfBirth = dob, password=correct_hashed_pw)
        request.session['userID']=new_user.id
        print('hi')
        return redirect('/userHome/{}'.format(request.session['userID']))
        
    return redirect('/userLogRegPage')

# 用户登陆
def userLog(request):
    form = request.POST
    if form['account']:
        try:
            try:
                user = User.objects.get(account=form['account'])
            except:
                user = User.objects.get(phone=form['account'])
        except:
            messages.error(request, '这个账号/手机还未注册')
            return redirect('/userLogRegPage')
    else:
        messages.error(request, '请输入账号')
        return redirect('/userLogRegPage')

    if form['password']:
        check = bcrypt.checkpw(request.POST['password'].encode(), user.password.encode())
        if check:
            request.session['userID'] = user.id
            return redirect('/userHome/{}'.format(request.session['userID']))
        else:
            messages.error(request,'密码错误')
            return redirect('/userLogRegPage')
    else:
        messages.error(request,'请输入密码')
        return redirect('/userLogRegPage')

# 用户主页
def userHome(request,userID):
    if not 'userID' in request.session:
        messages.error(request, '您需要先登陆')
        return redirect('/userLogRegPage')
    if not request.session['userID'] == userID:
        messages.error(request, '您没有权限访问该页面')
        return redirect('/userHome/{}'.format(request.session['userID']))
    user = User.objects.get(id=userID)
    product = Product.objects.all()
    ad = Advertisement.objects.all()
    context={
        'thisUser':user,
        'products': product,
        'ad': ad,
    }
    return render(request,'userHome.html',context)

# 用户商品详情页面
def userProductDetail(request,productID,userID):
    if not 'userID' in request.session:
        messages.error(request, '您需要先登陆')
        return redirect('/userLogRegPage')
    if not request.session['userID'] == userID:
        messages.error(request, '您没有权限访问该页面')
        return redirect('/userHome/{}'.format(request.session['userID']))

    user = User.objects.get(id=userID)
    product = Product.objects.get(id=productID)
    searchCate = product.category.split('/')[0]
    maylike1 = Product.objects.filter(color__contains=product.color).exclude(id=product.id).first()
    maylike2 = Product.objects.filter(category__contains=searchCate).exclude(id=product.id).first()
    maylike3 = Product.objects.filter(color__contains=product.color).exclude(id=product.id).last()
    checkLike = ProductLike.objects.filter(likeUser=user).filter(likeProduct=product)

    size = ProductDetail.objects.filter(product=product)
    
    context = {
        'thisUser':user,
        'product': product,
        'maylike1': maylike1,
        'maylike2': maylike2,
        'maylike3': maylike3,
        'liked': checkLike,
        'size': size,
    }
    return render(request, 'productDetail.html',context)

# 查看产品图片（大图）
def viewIMG(request, productID, userID, imgID):
    if not 'userID' in request.session:
        messages.error(request, '您需要先登陆')
        return redirect('/userLogRegPage')
    if not request.session['userID'] == userID:
        messages.error(request, '您没有权限访问该页面')
        return redirect('/userHome/{}'.format(request.session['userID']))

    product = Product.objects.get(id=productID)

    if imgID == 1:
        img = product.img1 

    if imgID == 2:
        img= product.img2
            
    if imgID == 3:
        img= product.img3
            
    if imgID == 4:
        img= product.img4
            
    if imgID == 5:
        img= product.img5
            
    if imgID == 6:
        img= product.img6

    context = {
        'img':img,
        'product':product,
        'user': userID,
    }
    return render(request,'img.html',context)

# 用户收藏
def likeProduct(request,productID,userID):
    if not 'userID' in request.session:
        return redirect('/userLogRegPage')
    if not request.session['userID'] == userID:
        return redirect('/userHome/{}'.format(request.session['userID']))
    product = Product.objects.get(id=productID)
    user = User.objects.get(id=userID)
    new_like = ProductLike.objects.create(likeProduct=product,likeUser=user)
    return redirect('/user/product/detail/{}'.format(productID) + '/{}'.format(userID))

# 用户取消收藏
def unlikeProduct(request,productID,userID):
    if not 'userID' in request.session:
        return redirect('/userLogRegPage')
    if not request.session['userID'] == userID:
        return redirect('/userHome/{}'.format(request.session['userID']))
    product = Product.objects.get(id=productID)
    user = User.objects.get(id=userID)
    unlike = ProductLike.objects.filter(likeUser=user).filter(likeProduct=product)
    unlike.delete()
    return redirect('/user/product/detail/{}'.format(productID) + '/{}'.format(userID))

# 用户收藏页面
def myFavoritesPage(request, userID):
    if not 'userID' in request.session:
        return redirect('/userLogRegPage')
    if not request.session['userID'] == userID:
        return redirect('/userHome/{}'.format(request.session['userID']))

    user = User.objects.get(id=userID)
    likedProduct = ProductLike.objects.filter(likeUser=user)
    context={
        'thisUser':user,
        'likedProduct': likedProduct,
    }
    return render(request,'myFavorites.html',context)

# 用户客服页面
def servicePage(request,userID):
    if not 'userID' in request.session:
        return redirect('/userLogRegPage')
    if not request.session['userID'] == userID:
        return redirect('/userHome/{}'.format(request.session['userID']))

    user = User.objects.get(id=userID)
    server = ServiceInfo.objects.all()
    context = {
        'thisUser': user,
        'server': server,
    }
    return render(request,'service.html',context)

# 用户信息页面
def myAccount(request, userID):
    if not 'userID' in request.session:
        return redirect('/userLogRegPage')
    if not request.session['userID'] == userID:
        return redirect('/userHome/{}'.format(request.session['userID']))
    
    user = User.objects.get(id=userID)
    address = UserAddress.objects.filter(user=user)
    dob = user.dateOfBirth
    context = {
        'thisUser': user,
        'address': address,
        'year': dob.split('/')[0],
        'month': dob.split('/')[1],
        'day': dob.split('/')[2],
    }
    return render(request, 'editAccount.html', context)

# 更新用户信息
def updateUserAccount(request, userID):
    if not 'userID' in request.session:
        return redirect('/userLogRegPage')
    if not request.session['userID'] == userID:
        return redirect('/userHome/{}'.format(request.session['userID']))
    form = request.POST
    error = []
    user = User.objects.get(id=userID)
    check = bcrypt.checkpw(request.POST['password'].encode(), user.password.encode())
    dob = ''
    if check:
        if form['name']:
            if len(form['name'])<2:
                error.append("姓名最少包含2个文字")
            else:
                user.userName = form['name']
        if form['account']:
            exist_account = User.objects.filter(account=form['account'])
            if len(exist_account)>0:
                error.append('这个账号已被注册')
            else:
                user.account = form['account']
        if form['phone']:
            exist_phone = User.objects.filter(phone=form['phone'])
            if len(exist_phone)>0:
                error.append('这个手机已被注册')
            else:
                if len(form['phone'])<11:
                    error.append("手机号码不符合规格，请填写11位数手机号")
                else:
                    user.phone = form['phone']
        if form['newPassword']:
            if len(form['newPassword'])<6:
                error.append('新密码最少6位数')
            else:
                if not form['newPassword'] == form['password_comfirm']:
                    error.append('您输入的新密码与确认密码不相同')
                else:
                    hashed_pw = bcrypt.hashpw(form['newPassword'].encode(), bcrypt.gensalt())
                    correct_hashed_pw = hashed_pw.decode('utf-8')
                    user.password = correct_hashed_pw
        if form['year']:
            if not len(form['year'])==4:
                error.append("出生年份不符合规格，如：1990")
            else:
                year = form['year']
        else:
            year = user.dateOfBirth.split('/')[0]

        if form['month']:
            if not len(form['month'])==2:
                error.append("出生月份不符合规格，如：01")
            else:
                if int(form['month'])>12:
                    error.append("出生月份不符合规格,请从01至12间选择")
                else:
                    month = form['month']
        else:
            month = user.dateOfBirth.split('/')[1]

        if form['day']:
            if not len(form['day'])==2:
                error.append("出生日期不符合规格，如：01")
            else:
                if int(form['day'])>31:
                    error.append("出生日期不符合规格,请从01至31间选择")
                else:
                    day = form['day']
        else:
            day = user.dateOfBirth.split('/')[2]   
    else:
        error.append('请输入正确的当前密码后再进行其它操作')

    if error:
        error.append('账户信息更新失败')
        for e in error:
            messages.error(request, e)
    else:
        dob = year+'/'+ month +'/'+ day
        user.dateOfBirth = dob
        user.save()
    return redirect('/user/myaccount/{}'.format(userID))

# 用户添加地址
def addAddress(request, userID):
    if not 'userID' in request.session:
        return redirect('/userLogRegPage')
    if not request.session['userID'] == userID:
        return redirect('/userHome/{}'.format(request.session['userID']))
    form = request.POST
    error = []
    user = User.objects.get(id=userID)
    if len(form['country'])<1:
        error.append('请正确填写国家名称，如: 中国')
    if len(form['province'])<1:
        error.append('请正确填写省份名称，如: 广东省')
    if len(form['city'])<1:
        error.append('请正确填写城市名称，如: 广州市')
    if len(form['street'])<1:
        error.append('请正确填写街道名称，如: 东风西路123号')
    if len(form['room'])<1:
        error.append('请正确填写房间号，如: 12号')
    if len(form['zipcode'])<5:
        error.append('请正确填写邮政编号，如: 529300')

    if error:
        error.append('添加邮递地址失败')
        for e in error:
            messages.error(request, e)
    else:
        new_address = UserAddress.objects.create(user=user, country=form['country'], province=form['province'], city=form['city'], street=form['street'], room=form['room'], zipcode=form['zipcode'])
        print('yes!')
    return redirect('/user/myaccount/{}'.format(userID))

# 用户删除地址
def deleteAddress(request, addressID, userID):
    if not 'userID' in request.session:
        return redirect('/userLogRegPage')
    if not request.session['userID'] == userID:
        return redirect('/userHome/{}'.format(request.session['userID']))
    address = UserAddress.objects.get(id=addressID)
    address.delete()
    return redirect('/user/myaccount/{}'.format(userID))

# 用户选购页面
def shoppingPage(request, productID, userID):
    if not 'userID' in request.session:
        return redirect('/userLogRegPage')
    if not request.session['userID'] == userID:
        return redirect('/userHome/{}'.format(request.session['userID']))

    user = User.objects.get(id=userID)
    product = Product.objects.get(id=productID)
    productDetail = ProductDetail.objects.filter(product=product)
    context = {
        'thisUser': user,
        'product': product,
        'detail': productDetail,
    }
    return render(request, 'shopping.html', context)

# 加入购物车
def addItemToCart(request, userID):
    if not 'userID' in request.session:
        return redirect('/userLogRegPage')
    if not request.session['userID'] == userID:
        return redirect('/userHome/{}'.format(request.session['userID']))
    
    user = User.objects.get(id=userID)
    item = ProductDetail.objects.get(id=request.POST['size'])
    price = item.product.price * int(request.POST['quantity'])
    new_cart = ShoppingCart.objects.create(customer=user, item=item, itemQuantity=request.POST['quantity'], price=price)
    return redirect('/user/mycart/{}'.format(userID))

# 购物车移除商品
def deleteItemFromCart(request, itemID, userID):
    if not 'userID' in request.session:
        return redirect('/userLogRegPage')
    if not request.session['userID'] == userID:
        return redirect('/userHome/{}'.format(request.session['userID']))

    item = ShoppingCart.objects.get(id=itemID)
    item.delete()
    return redirect('/user/mycart/{}'.format(userID))

# 购物车页面
def myShoppingCart(request, userID):
    if not 'userID' in request.session:
        return redirect('/userLogRegPage')
    if not request.session['userID'] == userID:
        return redirect('/userHome/{}'.format(request.session['userID']))
    error = []
    user = User.objects.get(id=userID)
    item = ShoppingCart.objects.filter(customer=user)
    count = len(item)
    itemCount = 0
    total = 0
    print(item)
    for i in item:
        if i.item.quantity < i.itemQuantity:
            error.append(i.item.product.name)
        else:
            itemCount += i.itemQuantity
            total += i.price
    context = {
        'thisUser': user,
        'cartItem': item,
        'count': count,
        'itemCount': itemCount,
        'total': total,
        'error': error,
    }
    return render(request,'shoppingCart.html', context)

# 买单页面
def checkoutPage(request, userID):
    if not 'userID' in request.session:
        return redirect('/userLogRegPage')
    if not request.session['userID'] == userID:
        return redirect('/userHome/{}'.format(request.session['userID']))
    user = User.objects.get(id=userID)
    item = ShoppingCart.objects.filter(customer=user)
    count = len(item)
    itemCount = 0
    total = 0

    for i in item:
        itemCount += i.itemQuantity
        total += i.price

    address = UserAddress.objects.filter(user=user)
    context = {
        'thisUser': user,
        'cartItem': item,
        'count': count,
        'itemCount': itemCount,
        'total': total,
        'address': address,
    }
    return render(request, 'checkout.html', context)

# redirect to 支付页面
def checkoutRedirect(request, userID):
    if not 'userID' in request.session:
        return redirect('/userLogRegPage')
    if not request.session['userID'] == userID:
        return redirect('/userHome/{}'.format(request.session['userID']))
    return redirect('/user/payment/{}'.format(userID) + '/{}'.format(request.POST['address']))

# 支付页面
def payment(request, userID, addressID):
    if not 'userID' in request.session:
        return redirect('/userLogRegPage')
    if not request.session['userID'] == userID:
        return redirect('/userHome/{}'.format(request.session['userID']))

    user = User.objects.get(id=userID)
    paymentMethod = Payment.objects.all()
    item = ShoppingCart.objects.filter(customer=user)
    address = addressID
    total = 0
    for i in item:
        total += i.price

    context = {
        'thisUser': user,
        'method': paymentMethod,
        'total': total,
        'address': address,
    }
    return render(request, 'payment.html', context)

# 生产订单
def generateOrder(request, userID):
    if not 'userID' in request.session:
        return redirect('/userLogRegPage')
    if not request.session['userID'] == userID:
        return redirect('/userHome/{}'.format(request.session['userID']))
    error = []
    form = request.POST
    user = User.objects.get(id=userID)
    item = ShoppingCart.objects.filter(customer=user)
    total = 0
    comfirmNum = form['number'] + user.phone
    check = Confirmation.objects.filter(comfirmNumber = comfirmNum)
    for i in item:
        total += i.price
    if check:
        error.append('这个订单已经生产，请到订单信息页面查询')
    if not len(form['number']) == 5:
        error.append('请输入单号后5位')
    if not form['number'] == form['number_comform']:
        error.append('转账单号与确认单号不相符')

    if error:
        error.append('生产订单失败')
        for e in error:
            messages.error(request, e)
        return redirect('/user/payment/{}'.format(userID) + '/{}'.format(form['address']))
    else:
        address = UserAddress.objects.get(id=form['address'])
        new_address = address.country + "," +  address.province + "," + address.city + "," + address.street + "," + address.room + "," + address.zipcode
        new_comfirm = Confirmation.objects.create(comfirmNumber=comfirmNum, buyer=user, salePrice=total, shippingAddress=new_address, shippingStatus=False)
        print(new_comfirm)
        for i in item:
            product = ProductDetail.objects.get(id=i.item.id)
            product.quantity = product.quantity - i.itemQuantity
            product.save()
            sold = SoldItem.objects.create(sale=new_comfirm, soldProduct=i.item.product.name, quantity=i.itemQuantity, size=i.item.size, color=i.item.product.color)
            print(sold)

        clearCart = ShoppingCart.objects.filter(customer=user)
        clearCart.delete()
    return redirect('/user/orderInfo/{}'.format(userID))

# 订单页面
def orderPage(request, userID):
    if not 'userID' in request.session:
        return redirect('/userLogRegPage')
    if not request.session['userID'] == userID:
        return redirect('/userHome/{}'.format(request.session['userID']))

    user = User.objects.get(id=userID)
    comfirm = Confirmation.objects.filter(buyer=user).order_by('-created_at')

    context = {
        'thisUser': user,
        'order': comfirm,
    
    }
    return render(request, 'userOrders.html', context)

# 用户订单详情页面
def orderDetail(request, orderID, userID):
    if not 'userID' in request.session:
        return redirect('/userLogRegPage')
    if not request.session['userID'] == userID:
        return redirect('/userHome/{}'.format(request.session['userID']))

    user = User.objects.get(id=userID)
    comfirm = Confirmation.objects.get(id=orderID)
    detail = SoldItem.objects.filter(sale=comfirm)
    itemCount = 0
    for i in detail:
        itemCount += i.quantity
    context = {
        'thisUser': user,
        'comfirm': comfirm,
        'detail': detail,
        'itemCount': itemCount,
    }

    return render(request,'userOrderDetail.html', context)

# 登出
def logout(request,ID):
    if 'bossID' in request.session:
        request.session.clear()
        return redirect('/mjdboss')
    else:
        request.session.clear()
        return redirect('/')
       