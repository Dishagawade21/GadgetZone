from datetime import datetime

from django.core import serializers
from django.db import IntegrityError, DatabaseError
from django.db.models import Min, Max
from django.http import JsonResponse, HttpResponse, HttpResponseNotAllowed, HttpResponseServerError
from django.shortcuts import render, redirect
from django.db import models

from app.models import *
import pandas as pd

# making change here for pdf

from reportlab.pdfgen import canvas
from io import BytesIO
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle ,Paragraph 


# import for decrease quantity

import sqlite3

# making feedback change here

# Connect to SQLite database
# conn = sqlite3.connect('dbEcomm.sqlite3')
# c = conn.cursor()

# Create a feedback table if not exists
# c.execute('''CREATE TABLE IF NOT EXISTS feedback
#              (id INTEGER PRIMARY KEY AUTOINCREMENT,
#              rating INT,
#              comments TEXT)''')

# Get user input from HTML response
# rating = int(request.POST.get('rating'))
# comments = request.POST.get('message')

# Insert feedback into the database
# c.execute("INSERT INTO feedback (rating, comments) VALUES (?, ?)", (rating, comments))

# Commit changes and close connection
# conn.commit()
# conn.close()




# making decrese product change here

def decrease_product_quantity(request):
    # Connect to SQLite database
    conn = sqlite3.connect('dbEcomm.sqlite3')
    cursor = conn.cursor()
    # Fetch the current quantity from the database
    name=request.POST.get('name')
    cursor.execute("SELECT productCount FROM tblProduct WHERE name = ?", (name,))
    result = cursor.fetchone()
    current_quantity = result[0]

    productCount=request.POST.get('qty')
    updated_quantity=0
    # Decrease the current quantity by the purchased quantity
    updated_quantity = current_quantity - int(productCount)

    # Update the database with the new quantity
    cursor.execute("UPDATE tblProduct SET productCount=? where name=?", (updated_quantity,name))
    conn.commit()

    # Close the database connection
    cursor.close()
    conn.close()
    
    # Return a response indicating the quantity has been decreased
    # return render(viewusercart)
    # return render(request, 'app/details.html',)
    return redirect(product_details)


def decrease_product_quantity(request):
    # Connect to SQLite database
    conn = sqlite3.connect('dbEcomm.sqlite3')
    cursor = conn.cursor()
    # Fetch the current quantity from the database
    name=request.POST.get('name')
    cursor.execute("SELECT productCount FROM tblProduct WHERE name = ?", (name,))
    result = cursor.fetchone()
    current_quantity = result[0]

    productCount=request.POST.get('qty')
    updated_quantity=0
    # Decrease the current quantity by the purchased quantity
    updated_quantity = current_quantity - int(productCount)

    # Update the database with the new quantity
    cursor.execute("UPDATE tblProduct SET productCount=? where name=?", (updated_quantity,name))
    conn.commit()

    # Close the database connection
    cursor.close()
    conn.close()
    
    # Return a response indicating the quantity has been decreased
    # return render(viewusercart)
    # return render(request, 'app/details.html',)
    return redirect(product_details)



# for generating pdf's

def generate_pdf(request):
    # Retrieve data from SQLite database
    data = OrderDetails.objects.all()  # Replace OrderDetails with your actual model name

    # Create a list to store table data with column names as the first row
    table_data = [['PID', 'Name', 'Price', 'Qty', 'Total', 'Status']]  # Add column names here
    for row in data:
        table_data.append([row.pid, row.name, row.price, row.qty, row.total, row.status])  # Replace field1, field2, field3 with your actual field names

    # Create a PDF document
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="mytable.pdf"'  # Replace mytable.pdf with your desired file name
    doc = SimpleDocTemplate(response, pagesize=landscape(letter))

    # Create a table with table data
    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), '#1e90ff'),  # Header row background color
        ('TEXTCOLOR', (0, 0), (-1, 0), '#ffffff'),  # Header row text color
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Table data alignment
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Header row font
        ('FONTSIZE', (0, 0), (-1, 0), 14),  # Header row font size
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),  # Header row bottom padding
        ('BACKGROUND', (0, 1), (-1, -1), '#f8f8f8'),  # Table data background color
        ('GRID', (0, 0), (-1, -1), 1, '#000000')  # Table grid color
    ]))

    # Add table to the PDF document and build it    
    doc.build([table])

    return response

# till here





def index(request):
    try:
        products = Product.objects.all().order_by('?')[:4]
        return render(request, 'app/index.html', {'products': products})
    except Exception as ex:
        return render(request, 'app/index.html', {'message': ex})


def login(request):
    try:
        if request.method == 'POST':
            email = str(request.POST.get("email")).strip()
            password = str(request.POST.get("password")).strip()
            user = User.objects.get(email=email)
            uid = user.id
            if user.password == password:
                request.session['id'] = uid
                if uid == '201222043313':
                    request.session['alogin'] = True
                    return redirect(add_subcategory)
                else:
                    request.session['ulogin'] = True
                    if 'cart' in request.session:
                        save_cart(request.session['cart'], uid)
                    load_cart(request, uid)
                    return redirect(view_user_cart)
            else:
                message = 'Invalid username or password'
                return render(request, 'app/login.html', {'message': message})
        else:
            request.session['alogin'] = False
            request.session['ulogin'] = False
            return render(request, 'app/login.html')
    except User.DoesNotExist:
        message = 'Invalid username or password'
    except Exception as ex:
        message = ex
    return render(request, 'app/login.html', {'message': message})


def add_category(request):
    if 'alogin' in request.session and request.session['alogin']:
        if request.method == 'POST':
            try:
                cid = datetime.now().strftime('%d%m%y%I%M%S')
                category = Category()
                category.id = cid
                category.name = str(request.POST.get('name')).strip()
                category.save(force_insert=True)
                message = 'Category details added successfully'
            except Exception as ex:
                message = ex
            return render(request, 'admin/addcategory.html', {'message': message})
        else:
            return render(request, 'admin/addcategory.html')
    else:
        return redirect(login)


def add_subcategory(request):
    if 'alogin' in request.session and request.session['alogin']:
        try:
            categories = Category.objects.all()
            if request.method == 'POST':
                cid = datetime.now().strftime('%d%m%y%I%M%S')
                subcategory = Subcategory()
                subcategory.id = cid
                subcategory.master = str(request.POST.get('master')).strip()
                subcategory.name = str(request.POST.get('name')).strip()
                subcategory.save(force_insert=True)
                message = 'Subcategory details added successfully'
            else:
                return render(request, 'admin/addsubcategory.html', {'categories': categories})
        except Exception as ex:
            categories = None
            message = ex
        return render(request, 'admin/addsubcategory.html', {'categories': categories, 'message': message})
    else:
        return redirect(login)


def add_brand(request):
    if 'alogin' in request.session and request.session['alogin']:
        if request.method == 'POST':
            try:
                bid = datetime.now().strftime('%d%m%y%I%M%S')
                brand = Brand()
                brand.id = bid
                brand.name = str(request.POST.get('name')).strip()
                brand.save(force_insert=True)
                message = 'Brand details added successfully'
            except Exception as ex:
                message = ex
            return render(request, 'admin/addbrand.html', {'message': message})
        else:
            return render(request, 'admin/addbrand.html')
    else:
        return redirect(login)


def add_product(request):
    if 'alogin' in request.session and request.session['alogin']:
        message = ''
        try:
            categories = Category.objects.all()
            brands = Brand.objects.all()
            if request.method == 'POST':
                if request.FILES:
                    pid = datetime.now().strftime('%d%m%y%I%M%S')
                    photo = request.FILES['photo1']
                    with open(f'media/products/{pid}1.jpg', 'wb') as fw:
                        fw.write(photo.read())
                    photo = request.FILES['photo2']
                    with open(f'media/products/{pid}2.jpg', 'wb') as fw:
                        fw.write(photo.read())
                    photo = request.FILES['photo3']
                    with open(f'media/products/{pid}3.jpg', 'wb') as fw:
                        fw.write(photo.read())
                    product = Product()
                    product.id = pid
                    product.master = str(request.POST.get('master')).strip()
                    product.sub = str(request.POST.get('sub')).strip()
                    product.brand = str(request.POST.get('brand')).strip()
                    product.name = str(request.POST.get('name')).strip()
                    product.mrp = float(request.POST.get('mrp'))
                    product.discount = int(request.POST.get('discount'))
                    product.price = float(request.POST.get('price'))
                    product.description = request.POST.get('description')

                    # i made a change here to add producCount
                    product.productCount = int(request.POST.get('productcount'))
                    
                    product.save(force_insert=True)
                    message = 'Product details added successfully'
                else:
                    raise Exception('Photo uploading error')
        except Exception as ex:
            message = ex
        return render(request, 'admin/addproduct.html',
                      {'categories': categories, 'brands': brands, 'message': message})
    return redirect(login)


def getsubcategories(request, master):
    subcategories = Subcategory.objects.filter(master=master)
    json = serializers.serialize('json', subcategories)
    return JsonResponse(json, safe=False)


def details(request):
    try:
        pid = str(request.GET.get('pid')).strip()
        product = Product.objects.get(id=pid)
        message = None
        class_ = None
        if request.method == 'POST':
            flag = False
            pid = str(request.POST.get('id')).strip()
            if 'cart' in request.session:
                cart = list(request.session['cart'])
                if not any(d['id'] == pid for d in cart):
                    flag = True
            else:
                flag = True
                cart = []
            if flag:
                name = str(request.POST.get('name')).strip()
                description = str(request.POST.get('description')).strip()
                qty = int(request.POST.get('qty'))  
                price = float(request.POST.get('price'))
                total = qty * price
    
                cart.append(
                    {'id': pid, 'name': name, 'description': description, 'price': price, 'qty': qty, 'total': total})
                request.session['cart'] = cart
                request.session['cart_count'] = len(cart)
                request.session['cart_total'] = sum(d['total'] for d in cart)
                class_ = 'success'
                message = 'Item added to bag successfully'
            else:
                class_ = 'danger'
                message = 'Item already exists in bag'
        return render(request, 'app/details.html', {'product': product, 'message': message, 'class': class_})
    except Exception as ex:
        return render(request, 'app/details.html', {'message': ex, 'class': 'danger'})


def view_cart(request):
    try:
        cart = []
        if request.method == 'POST':
            pid = str(request.POST.get('id')).strip()
            cart = list(request.session['cart'])
            for i in range(len(cart)):
                if cart[i]['id'] == pid:
                    del cart[i]
                    break
            request.session['cart'] = cart
            request.session['cart_count'] = len(cart)
            request.session['cart_total'] = sum(d['total'] for d in cart)
        if 'cart' in request.session:
            cart = list(request.session['cart'])
        return render(request, 'app/viewcart.html', {'cart': cart})
    except Exception as ex:
        return render(request, 'app/viewcart.html', {'message': ex})


def update_cart_qty(request):
    if request.method == 'POST':
        qty = int(request.POST.get('qty'))
        if qty > 0:
            pid = str(request.POST.get('pid')).strip()
            cart = list(request.session['cart'])
            for i in range(len(cart)):
                if cart[i]['id'] == pid:
                    cart[i]['qty'] = qty
                    cart[i]['total'] = qty * float(cart[i]['price'])
                    break
            request.session['cart'] = cart
            request.session['cart_total'] = sum(d['total'] for d in cart)
            return HttpResponse('Cart Updated')
        return HttpResponse('Failed to Update Cart')
    HttpResponseNotAllowed(['POST'])


def registration(request):
    if request.method == 'POST':
        try:
            user = User()
            user.id = datetime.now().strftime('%d%m%y%I%M%S')
            user.name = request.POST.get('name')
            user.email = request.POST.get('email')
            user.mobile = request.POST.get('mobile')
            user.address = request.POST.get('address')
            user.password = str(request.POST.get('password')).strip()
            user.save(force_insert=True)
            class_ = 'success'
            message = 'User registration done successfully'
        except Exception as ex:
            class_ = 'danger'
            message = ex
        return render(request, 'app/registration.html', {'message': message, 'class': class_})
    else:
        return render(request, 'app/registration.html')

def unavailable_product(request):
    pid = str(request.GET.get('pid')).strip()
    product = Product.objects.get(id=pid)
    message = None
    class_ = None
    if product.productCount <= 0:
        class_ = 'danger'
        message = 'Product Unavailable'

def product_details(request):
    if 'ulogin' in request.session and request.session['ulogin']:
        try:
            uid = request.session['id']
            pid = str(request.GET.get('pid')).strip()
            product = Product.objects.get(id=pid)
            message = None
            class_ = None
        
            if request.method == 'POST':


                if product.productCount <= 0:
                    class_ = 'danger'
                    message = 'Product Unavailable'
                else:
                    pid = str(request.POST.get('id')).strip()
                    name = str(request.POST.get('name')).strip()
                    description = str(request.POST.get('description')).strip()
                    qty = int(request.POST.get('qty'))
                    price = float(request.POST.get('price'))
                    total = qty * price
                    cart = Cart()
                    cart.uid = uid
                    cart.pid = pid
                    cart.name = name
                    cart.description = description
                    cart.price = price
                    cart.qty = qty
                    cart.total = total
                    cart.save(force_insert=True)


                    load_cart(request, uid)
                    class_ = 'success'
                    message = 'Item added to bag successfully'
                    decrease_product_quantity(request)

        
        

        except IntegrityError:
            class_ = 'danger'
            message = 'Item already exists in bag'
        except Exception as ex:
            class_ = 'danger'
        
            message = ex
        return render(request, 'user/details.html', {'product': product, 'message': message, 'class': class_})
    else:
        return redirect(login)


def view_user_cart(request):
    if 'ulogin' in request.session and request.session['ulogin']:
        try:
            pid = str(request.POST.get('pid')).strip()
            uid = request.session['id']

            if request.method == 'POST':
                cart = Cart.objects.get(uid=uid, pid=pid)

                conn = sqlite3.connect('dbEcomm.sqlite3')
                cursor = conn.cursor()

                product = Product.objects.get(id=pid)
                name=cart.name
                updated_quantity = product.productCount + cart.qty
                
                cursor.execute("UPDATE tblProduct SET productCount=? where name=?", (updated_quantity,name))
                conn.commit()
                # making changes here
                
                # till here
                cart.delete()
            load_cart(request, uid)
            cart = Cart.objects.filter(uid=uid)
            return render(request, 'user/viewcart.html', {'cart': cart})
        except Exception as ex:
            return render(request, 'user/viewcart.html', {'message': ex})
    else:
        return redirect(login)


def home(request):
    if 'ulogin' in request.session and request.session['ulogin']:
        try:
            products = Product.objects.all().order_by('?')[:4]
            return render(request, 'user/index.html', {'products': products})
        except Exception as ex:
            return render(request, 'user/index.html', {'message': ex})
    else:
        return redirect(login)


def save_cart(cart_, uid):
    for product in cart_:
        try:
            cart = Cart()
            cart.uid = uid
            cart.pid = product['id']
            cart.name = product['name']
            cart.description = product['description']
            cart.price = product['price']
            cart.qty = product['qty']
            cart.total = product['total']
            cart.save(force_insert=True)
        except IntegrityError:
            cart = Cart.objects.get(uid=uid, pid=product['id'])
            qty = product['qty']
            price = product['price']
            cart.name = product['name']
            cart.description = product['description']
            cart.price = price
            cart.qty = qty
            cart.total = qty * price
            cart.save(force_update=True)


def load_cart(request, uid):
    cart = list(Cart.objects.filter(uid=uid).values())
    request.session['cart_count'] = len(cart)
    request.session['cart_total'] = sum(d['total'] for d in cart)


def logout(request):
    sessions = list(request.session.keys())
    for session in sessions:
        del request.session[session]
        request.session.modified = True
    return redirect(login)


def update_user_cart_qty(request):
    if request.method == 'POST':
        qty = int(request.POST.get('qty'))
        if qty > 0:
            uid = request.session['id']
            pid = str(request.POST.get('pid')).strip()
            cart = Cart.objects.get(uid=uid, pid=pid)
            price = cart.price
            cart.qty = qty
            cart.total = qty * price
            cart.save(force_update=True)
            load_cart(request, uid)
            return HttpResponse('Cart Updated')
        return HttpResponse('Failed to Update Cart')
    HttpResponseNotAllowed(['POST'])


def loadcategories(request):
    try:
        categories = list(Category.objects.all().values())
        response = JsonResponse(categories, safe=False)
    except Exception as ex:
        print(ex)
        response = HttpResponseServerError(ex)
    return response


def loadbrands(request):
    try:
        brands = list(Brand.objects.all().values())
        response = JsonResponse(brands, safe=False)
    except Exception as ex:
        print(ex)
        response = HttpResponseServerError(ex)
    return response


def productscat(request):
    try:
        message = None
        class_ = None
        min = 0
        max = 0
        min_ = 0
        max_ = 0
        dmin = 0
        dmax = 0
        dmin_ = 0
        dmax_ = 0
        category = str(request.GET.get('category')).strip()
        subcategories = Subcategory.objects.filter(master=category)
        sub = str(request.GET.get('sub')).strip()
        if category != 'None':
            product = Product.objects.filter(master=category)
            min = list(product.aggregate(Min('price')).values())[0]
            max = list(product.aggregate(Max('price')).values())[0]
            min_ = min
            max_ = max
            dmin = list(product.aggregate(Min('discount')).values())[0]
            dmax = list(product.aggregate(Max('discount')).values())[0]
            dmin_ = dmin
            dmax_ = dmax
            if sub != 'None':
                product = Product.objects.filter(master=category, sub=sub)
                min = list(product.aggregate(Min('price')).values())[0]
                max = list(product.aggregate(Max('price')).values())[0]
                min_ = min
                max_ = max
                dmin = list(product.aggregate(Min('discount')).values())[0]
                dmax = list(product.aggregate(Max('discount')).values())[0]
                dmin_ = dmin
                dmax_ = dmax
        if str(request.GET.get('min')).strip() != 'None' and str(request.GET.get('max')).strip() != 'None':
            min_ = int(request.GET.get('min'))
            max_ = int(request.GET.get('max'))
            if category != 'None':
                product = Product.objects.filter(master=category, price__gte=min_, price__lte=max_)
                if sub != 'None':
                    product = Product.objects.filter(master=category, sub=sub, price__gte=min_, price__lte=max_)
        if str(request.GET.get('dmin')).strip() != 'None' and str(request.GET.get('dmax')).strip() != 'None':
            dmin_ = int(request.GET.get('dmin'))
            dmax_ = int(request.GET.get('dmax'))
            if category != 'None':
                product = Product.objects.filter(master=category, discount__gte=dmin_, discount__lte=dmax_)
                if sub != 'None':
                    product = Product.objects.filter(master=category, sub=sub, discount__gte=dmin_, discount__lte=dmax_)
        return render(request, 'app/productscat.html',
                      {'category': category, 'subcategories': subcategories, 'sub': sub, 'products': product,
                       'min': min, 'max': max, 'min_': min_,
                       'max_': max_,
                       'dmin': dmin, 'dmax': dmax, 'dmin_': dmin_,
                       'dmax_': dmax_, 'message': message,
                       'class': class_})
    except Exception as ex:
        return render(request, 'app/productscat.html', {'message': ex, 'class': 'danger'})


def productsbrand(request):
    try:
        message = None
        class_ = None
        min = 0
        max = 0
        min_ = 0
        max_ = 0
        dmin = 0
        dmax = 0
        dmin_ = 0
        dmax_ = 0
        brand = str(request.GET.get('brand')).strip()
        category = str(request.GET.get('category')).strip()
        categories = dict()
        for cat in set(Product.objects.filter(brand=brand).values_list('master', flat=True)):
            categories.update(
                {cat: Subcategory.objects.filter(master=cat).values_list('name', flat=True)})
        sub = str(request.GET.get('sub')).strip()
        if brand != 'None':
            product = Product.objects.filter(brand=brand)
            min = list(product.aggregate(Min('price')).values())[0]
            max = list(product.aggregate(Max('price')).values())[0]
            min_ = min
            max_ = max
            dmin = list(product.aggregate(Min('discount')).values())[0]
            dmax = list(product.aggregate(Max('discount')).values())[0]
            dmin_ = dmin
            dmax_ = dmax
            if category != 'None':
                product = Product.objects.filter(brand=brand, master=category)
                min = list(product.aggregate(Min('price')).values())[0]
                max = list(product.aggregate(Max('price')).values())[0]
                min_ = min
                max_ = max
                dmin = list(product.aggregate(Min('discount')).values())[0]
                dmax = list(product.aggregate(Max('discount')).values())[0]
                dmin_ = dmin
                dmax_ = dmax
                if sub != 'None':
                    product = Product.objects.filter(brand=brand, master=category, sub=sub)
                    min = list(product.aggregate(Min('price')).values())[0]
                    max = list(product.aggregate(Max('price')).values())[0]
                    min_ = min
                    max_ = max
                    dmin = list(product.aggregate(Min('discount')).values())[0]
                    dmax = list(product.aggregate(Max('discount')).values())[0]
                    dmin_ = dmin
                    dmax_ = dmax
        if str(request.GET.get('min')).strip() != 'None' and str(request.GET.get('max')).strip() != 'None':
            min_ = int(request.GET.get('min'))
            max_ = int(request.GET.get('max'))
            if brand != 'None':
                product = Product.objects.filter(brand=brand, price__gte=min_, price__lte=max_)
                if category != 'None':
                    product = Product.objects.filter(brand=brand, master=category, price__gte=min_, price__lte=max_)
                    if sub != 'None':
                        product = Product.objects.filter(brand=brand, master=category, sub=sub, price__gte=min_,
                                                         price__lte=max_)
        if str(request.GET.get('dmin')).strip() != 'None' and str(request.GET.get('dmax')).strip() != 'None':
            dmin_ = int(request.GET.get('dmin'))
            dmax_ = int(request.GET.get('dmax'))
            if brand != 'None':
                product = Product.objects.filter(brand=brand, discount__gte=dmin_, discount__lte=dmax_)
                if category != 'None':
                    product = Product.objects.filter(brand=brand, master=category, discount__gte=dmin_,
                                                     discount__lte=dmax_)
                    if sub != 'None':
                        product = Product.objects.filter(brand=brand, master=category, sub=sub, discount__gte=dmin_,
                                                         discount__lte=dmax_)
        return render(request, 'app/productsbrand.html',
                      {'brand': brand, 'category': category, 'categories': categories,
                       'sub': sub, 'products': product,
                       'min': min, 'max': max, 'min_': min_,
                       'max_': max_,
                       'dmin': dmin, 'dmax': dmax, 'dmin_': dmin_,
                       'dmax_': dmax_, 'message': message,
                       'class': class_})
    except Exception as ex:
        return render(request, 'app/productsbrand.html', {'message': ex, 'class': 'danger'})


def userproductscat(request):
    try:
        message = None
        class_ = None
        min = 0
        max = 0
        min_ = 0
        max_ = 0
        dmin = 0
        dmax = 0
        dmin_ = 0
        dmax_ = 0
        category = str(request.GET.get('category')).strip()
        subcategories = Subcategory.objects.filter(master=category)
        sub = str(request.GET.get('sub')).strip()
        if category != 'None':
            product = Product.objects.filter(master=category)
            min = list(product.aggregate(Min('price')).values())[0]
            max = list(product.aggregate(Max('price')).values())[0]
            min_ = min
            max_ = max
            dmin = list(product.aggregate(Min('discount')).values())[0]
            dmax = list(product.aggregate(Max('discount')).values())[0]
            dmin_ = dmin
            dmax_ = dmax
            if sub != 'None':
                product = Product.objects.filter(master=category, sub=sub)
                min = list(product.aggregate(Min('price')).values())[0]
                max = list(product.aggregate(Max('price')).values())[0]
                min_ = min
                max_ = max
                dmin = list(product.aggregate(Min('discount')).values())[0]
                dmax = list(product.aggregate(Max('discount')).values())[0]
                dmin_ = dmin
                dmax_ = dmax
        if str(request.GET.get('min')).strip() != 'None' and str(request.GET.get('max')).strip() != 'None':
            min_ = int(request.GET.get('min'))
            max_ = int(request.GET.get('max'))
            if category != 'None':
                product = Product.objects.filter(master=category, price__gte=min_, price__lte=max_)
                if sub != 'None':
                    product = Product.objects.filter(master=category, sub=sub, price__gte=min_, price__lte=max_)
        if str(request.GET.get('dmin')).strip() != 'None' and str(request.GET.get('dmax')).strip() != 'None':
            dmin_ = int(request.GET.get('dmin'))
            dmax_ = int(request.GET.get('dmax'))
            if category != 'None':
                product = Product.objects.filter(master=category, discount__gte=dmin_, discount__lte=dmax_)
                if sub != 'None':
                    product = Product.objects.filter(master=category, sub=sub, discount__gte=dmin_, discount__lte=dmax_)
        return render(request, 'user/productscat.html',
                      {'category': category, 'subcategories': subcategories, 'sub': sub, 'products': product,
                       'min': min, 'max': max, 'min_': min_,
                       'max_': max_,
                       'dmin': dmin, 'dmax': dmax, 'dmin_': dmin_,
                       'dmax_': dmax_, 'message': message,
                       'class': class_})
    except Exception as ex:
        return render(request, 'user/productscat.html', {'message': ex, 'class': 'danger'})


def userproductsbrand(request):
    try:
        message = None
        class_ = None
        min = 0
        max = 0
        min_ = 0
        max_ = 0
        dmin = 0
        dmax = 0
        dmin_ = 0
        dmax_ = 0
        brand = str(request.GET.get('brand')).strip()
        category = str(request.GET.get('category')).strip()
        categories = dict()
        for cat in set(Product.objects.filter(brand=brand).values_list('master', flat=True)):
            categories.update(
                {cat: Subcategory.objects.filter(master=cat).values_list('name', flat=True)})
        sub = str(request.GET.get('sub')).strip()
        if brand != 'None':
            product = Product.objects.filter(brand=brand)
            min = list(product.aggregate(Min('price')).values())[0]
            max = list(product.aggregate(Max('price')).values())[0]
            min_ = min
            max_ = max
            dmin = list(product.aggregate(Min('discount')).values())[0]
            dmax = list(product.aggregate(Max('discount')).values())[0]
            dmin_ = dmin
            dmax_ = dmax
            if category != 'None':
                product = Product.objects.filter(brand=brand, master=category)
                min = list(product.aggregate(Min('price')).values())[0]
                max = list(product.aggregate(Max('price')).values())[0]
                min_ = min
                max_ = max
                dmin = list(product.aggregate(Min('discount')).values())[0]
                dmax = list(product.aggregate(Max('discount')).values())[0]
                dmin_ = dmin
                dmax_ = dmax
                if sub != 'None':
                    product = Product.objects.filter(brand=brand, master=category, sub=sub)
                    min = list(product.aggregate(Min('price')).values())[0]
                    max = list(product.aggregate(Max('price')).values())[0]
                    min_ = min
                    max_ = max
                    dmin = list(product.aggregate(Min('discount')).values())[0]
                    dmax = list(product.aggregate(Max('discount')).values())[0]
                    dmin_ = dmin
                    dmax_ = dmax
        if str(request.GET.get('min')).strip() != 'None' and str(request.GET.get('max')).strip() != 'None':
            min_ = int(request.GET.get('min'))
            max_ = int(request.GET.get('max'))
            if brand != 'None':
                product = Product.objects.filter(brand=brand, price__gte=min_, price__lte=max_)
                if category != 'None':
                    product = Product.objects.filter(brand=brand, master=category, price__gte=min_, price__lte=max_)
                    if sub != 'None':
                        product = Product.objects.filter(brand=brand, master=category, sub=sub, price__gte=min_,
                                                         price__lte=max_)
        if str(request.GET.get('dmin')).strip() != 'None' and str(request.GET.get('dmax')).strip() != 'None':
            dmin_ = int(request.GET.get('dmin'))
            dmax_ = int(request.GET.get('dmax'))
            if brand != 'None':
                product = Product.objects.filter(brand=brand, discount__gte=dmin_, discount__lte=dmax_)
                if category != 'None':
                    product = Product.objects.filter(brand=brand, master=category, discount__gte=dmin_,
                                                     discount__lte=dmax_)
                    if sub != 'None':
                        product = Product.objects.filter(brand=brand, master=category, sub=sub, discount__gte=dmin_,
                                                         discount__lte=dmax_)
        return render(request, 'user/productsbrand.html',
                      {'brand': brand, 'category': category, 'categories': categories,
                       'sub': sub, 'products': product,
                       'min': min, 'max': max, 'min_': min_,
                       'max_': max_,
                       'dmin': dmin, 'dmax': dmax, 'dmin_': dmin_,
                       'dmax_': dmax_, 'message': message,
                       'class': class_})
    except Exception as ex:
        return render(request, 'user/productsbrand.html', {'message': ex, 'class': 'danger'})


def placeorder(request):
    if 'ulogin' in request.session and request.session['ulogin']:
        user = None
        class_ = 'success'
        try:
            message = ''
            uid = request.session['id']
            user = User.objects.get(id=uid)
            if request.method == 'POST':
                if request.session['cart_count'] > 0:
                    orderid = datetime.now().strftime('%d%m%y%I%M%S')
                    order = Order()
                    order.id = orderid
                    order.uid = uid
                    order.date = datetime.now().strftime('%d/%m/%y')
                    order.ordertotal = request.session['cart_total']
                    order.bname = request.POST.get('bname')
                    order.baddress = request.POST.get('baddress')
                    order.bcontact = request.POST.get('bcontact')
                    order.save(force_insert=True)
                    for cart in Cart.objects.filter(uid=uid):
                        orderdetails = OrderDetails()
                        orderdetails.orderid = orderid
                        orderdetails.pid = cart.pid
                        orderdetails.name = cart.name
                        orderdetails.description = cart.description
                        orderdetails.price = cart.price
                        orderdetails.qty = cart.qty
                        orderdetails.total = cart.total
                        orderdetails.status = 'Pending'
                        orderdetails.save(force_insert=True)
                        Cart.objects.get(uid=uid, pid=cart.pid).delete()


                    load_cart(request, uid)
                    

                    
                    
                    message = 'Order has been placed successfully'
                else:
                    raise Exception('Empty Cart')
        except Exception as ex:
            class_ = 'danger'
            message = ex
        return render(request, 'user/placeorder.html', {'class': class_, 'message': message, 'user': user})
    else:
        return redirect(login)


def orderhistory(request):
    if 'ulogin' in request.session and request.session['ulogin']:
        orders = None
        message = ''
        try:
            if request.method == "POST":
                orderid = request.POST.get('orderid')
                pid = request.POST.get('pid')
                orderdetails = OrderDetails.objects.get(orderid=orderid, pid=pid)
                orderdetails.status = 'Cancelled'
                orderdetails.save(force_update=True)
            uid = request.session['id']
            orders = pd.DataFrame(list(Order.objects.filter(uid=uid).values()))
            if len(orders) > 0:
                orderdetails = pd.DataFrame(list(OrderDetails.objects.all().values()))
                orderdetails.rename({'orderid': 'id'}, axis=1, inplace=True)
                orders = orders.merge(orderdetails, on=['id'])
                orders = orders.to_dict('records')
            else:
                raise Exception('Empty Shopping List')
        except Exception as ex:
            message = ex
        return render(request, 'user/orderhistory.html', {'message': message, 'orders': orders})
    else:
        return redirect(login)


def customerorders(request):
    if 'alogin' in request.session and request.session['alogin']:
        orders = None
        message = ''
        try:
            if request.method == "POST":
                orderid = request.POST.get('orderid')
                pid = request.POST.get('pid')
                orderdetails = OrderDetails.objects.get(orderid=orderid, pid=pid)
                orderdetails.status = 'Delivered'
                orderdetails.save(force_update=True)
            orders = pd.DataFrame(list(Order.objects.all().values()))
            orderdetails = pd.DataFrame(list(OrderDetails.objects.all().values()))
            orderdetails.rename({'orderid': 'id'}, axis=1, inplace=True)
            orders = orders.merge(orderdetails, on=['id'])
            orders = orders.to_dict('records')
        except Exception as ex:
            message = ex
        return render(request, 'admin/customerorders.html', {'message': message, 'orders': orders})
    else:
        return redirect(login)


def sendfeedback(request):
    if 'ulogin' in request.session and request.session['ulogin']:
        class_ = 'success'
        try:
            message = ''
            uid = request.session['id']
            pnames = None
            if request.method == 'POST':
                feedback = Feedback()
                feedback.id = datetime.now().strftime('%d%m%y%I%M%S')
                feedback.date = datetime.now().strftime('%d/%m/%y')
                feedback.uid = uid
                feedback.pname = request.POST.get('pname')
                feedback.message = request.POST.get('message')
                feedback.rating = request.POST.get('rating')
                feedback.save(force_insert=True)
                message = 'Feedback sent'
            orders = pd.DataFrame(list(Order.objects.filter(uid=uid).values()))
            if len(orders) > 0:
                orderdetails = pd.DataFrame(list(OrderDetails.objects.all().values()))
                orderdetails.rename({'orderid': 'id'}, axis=1, inplace=True)
                orders = orders.merge(orderdetails, on=['id'])
                orders = orders.to_dict('records')
                pnames = set([order['name'] for order in orders])
            else:
                raise Exception('Empty Shopping List')
        except Exception as ex:
            class_ = 'danger'
            message = ex
        return render(request, 'user/sendfeedback.html', {'class': class_, 'message': message, 'pnames': pnames})
    else:
        return redirect(login)


def customerfeedbacks(request):
    if 'alogin' in request.session and request.session['alogin']:
        orders = None
        message = ''
        try:
            users = pd.DataFrame(list(User.objects.all().values()))
            users.rename({'id': 'uid'}, axis=1, inplace=True)
            feedbacks = pd.DataFrame(list(Feedback.objects.all().values()))
            feedbacks = feedbacks.merge(users, on=['uid'])
            feedbacks = feedbacks.to_dict('records')
        except Exception as ex:
            message = ex
        return render(request, 'admin/customerfeedbacks.html', {'message': message, 'feedbacks': feedbacks})
    else:
        return redirect(login)


def updateproduct(request):
    if 'alogin' in request.session and request.session['alogin']:
        class_ = 'success'
        products = None
        try:
            message = ''
            if request.method == 'POST':
                pid = str(request.POST.get('pid')).strip()
                product = Product.objects.get(id=pid)
                mrp = float(request.POST.get('mrp'))
                discount = int(request.POST.get('discount'))
                product.mrp = mrp
                product.discount = discount
                product.price = mrp - (mrp * discount) / 100
                product.save(force_update=True)
                message = 'Product updated successfully'
            products = Product.objects.all()
        except Exception as ex:
            class_ = 'danger'
            message = ex
        return render(request, 'admin/updateproduct.html', {'class': class_, 'message': message, 'products': products})
    else:
        return redirect(login)


def categorymaster(request):
    if 'alogin' in request.session and request.session['alogin']:
        categories = None
        message = ''
        try:
            if request.method == "POST":
                catid = str(request.POST.get('catid')).strip()
                category = Category.objects.get(id=catid)
                category.delete()
                message = 'Category deleted successfully'
            categories = Category.objects.all()
        except DatabaseError as ex:
            if 'FOREIGN KEY constraint' in str(ex):
                categories = Category.objects.all()
                message = 'Do not delete category, It is in use'
            else:
                message = ex
        except Exception as ex:
            message = ex
        return render(request, 'admin/categorymaster.html', {'message': message, 'categories': categories})
    else:
        return redirect(login)


def subcategorymaster(request):
    if 'alogin' in request.session and request.session['alogin']:
        categories = None
        message = ''
        try:
            if request.method == "POST":
                catid = str(request.POST.get('catid')).strip()
                category = Subcategory.objects.get(id=catid)
                category.delete()
                message = 'Category deleted successfully'
            categories = Subcategory.objects.all()
        except DatabaseError as ex:
            if 'FOREIGN KEY constraint' in str(ex):
                categories = Subcategory.objects.all()
                message = 'Do not delete category, It is in use'
            else:
                message = ex
        except Exception as ex:
            message = ex
        return render(request, 'admin/subcategorymaster.html', {'message': message, 'categories': categories})
    else:
        return redirect(login)


def brandmaster(request):
    if 'alogin' in request.session and request.session['alogin']:
        brands = None
        message = ''
        try:
            if request.method == "POST":
                brandid = str(request.POST.get('brandid')).strip()
                brand = Brand.objects.get(id=brandid)
                brand.delete()
                message = 'Brand deleted successfully'
            brands = Brand.objects.all()
        except DatabaseError as ex:
            if 'FOREIGN KEY constraint' in str(ex):
                brands = Brand.objects.all()
                message = 'Do not delete brand, It is in use'
            else:
                message = ex
        except Exception as ex:
            message = ex
        return render(request, 'admin/brandmaster.html', {'message': message, 'brands': brands})
    else:
        return redirect(login)


def productmaster(request):
    if 'alogin' in request.session and request.session['alogin']:
        products = None
        message = ''
        try:
            if request.method == "POST":
                pid = str(request.POST.get('pid')).strip()
                product = Product.objects.get(id=pid)
                product.delete()
                message = 'Product deleted successfully'
            products = Product.objects.all()
        except DatabaseError as ex:
            if 'FOREIGN KEY constraint' in str(ex):
                products = Product.objects.all()
                message = 'Do not delete product, It is in use'
            else:
                message = ex
        except Exception as ex:
            message = ex
        return render(request, 'admin/productmaster.html', {'message': message, 'products': products})
    else:
        return redirect(login)


def changepassword(request):
    if 'ulogin' in request.session and request.session['ulogin']:
        try:
            class_ = 'success'
            message = ''
            if request.method == 'POST':
                uid = request.session['id']
                user = User.objects.get(id=uid)
                oldpassword = str(request.POST.get('oldpassword')).strip()
                newpassword = str(request.POST.get('newpassword')).strip()
                if user.password == oldpassword:
                    user.password = newpassword
                    user.save(force_update=True)
                    message = 'Password changed successfully'
                else:
                    raise Exception('Password not match')
        except Exception as ex:
            class_ = 'danger'
            message = ex
        return render(request, 'user/changepassword.html', {'class': class_, 'message': message})
    else:
        return redirect(login)
