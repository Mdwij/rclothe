from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="ShopHome"),
    path("signup/", views.signup_user, name="Signup"),
    path("login/", views.login_user, name="Login"),
    path("logout/", views.logout_user, name="Logout"),
    path("product/<str:mycategory>/", views.category_view, name="Category_view"),
    path("product/<str:mycategory>/<int:myid>/", views.productview, name="Productview"),
    path("update_cart/", views.updateCart, name="UpdateCart"),
    path("update_wishlist/", views.updateWishlist, name="UpdateWishlist"),
    path("cart/", views.Cart, name="Cart"),
    path("wishlist/", views.Wishlist, name="Wishlist"),
    path("checkout/", views.Checkout, name="Checkout"),
    path("search/", views.search, name="Search"),
    path("about/", views.about, name="About"),
    path("handlerequest/", views.handlerequest, name="Handlerequest"),
]
