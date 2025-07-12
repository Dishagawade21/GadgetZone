"""VR URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.urls import path
import app.views
from VR import settings

urlpatterns = [
                  path('', app.views.index),
                  path('login', app.views.login),
                  path('addcategory', app.views.add_category),
                  path('categorymaster', app.views.categorymaster),
                  path('addsubcategory', app.views.add_subcategory),
                  path('subcategorymaster', app.views.subcategorymaster),
                  path('addbrand', app.views.add_brand),
                  path('brandmaster', app.views.brandmaster),
                  path('addproduct', app.views.add_product),
                  path('productmaster', app.views.productmaster),
                  path('getsubcategories/<master>', app.views.getsubcategories),
                  path('details', app.views.details),
                  path('viewcart', app.views.view_cart),
                  path('updatecartqty', app.views.update_cart_qty),
                  path('registration', app.views.registration),
                  path('productdetails', app.views.product_details),
                  path('viewusercart', app.views.view_user_cart),
                  path('home', app.views.home),
                  path('logout', app.views.logout),
                  path('updateusercartqty', app.views.update_user_cart_qty),
                  path('loadcategories', app.views.loadcategories),
                  path('loadbrands', app.views.loadbrands),
                  path('productscat', app.views.productscat),
                  path('productsbrand', app.views.productsbrand),
                  path('userproductscat', app.views.userproductscat),
                  path('userproductsbrand', app.views.userproductsbrand),
                  path('placeorder', app.views.placeorder),
                  path('orderhistory', app.views.orderhistory),
                  path('customerorders', app.views.customerorders),
                  path('sendfeedback', app.views.sendfeedback),
                  path('customerfeedbacks', app.views.customerfeedbacks),
                  path('updateproduct', app.views.updateproduct),
                  path('changepassword', app.views.changepassword),

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
