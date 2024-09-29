from django.urls import path

from . import views

app_name = "auctions"

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path('addListing', views.add_listing, name="newListing"),
    path('listing/<int:listing_id>', views.entry_bid, name="entryBid"),
    path('listing/<int:listing_id>/place_bid/', views.place_bid, name="placeBid"),
    path('listing/<int:listing_id>/end_bid/',views.end_bid, name="endBid"),
    path('watchList', views.watch_list, name='watchList'),
    path('listing/<int:listing_id>/toggleWatch',views.toggle_watch_list, name='toggleWatch'),
    path('listing/<int:listing_id>/comment',views.add_comment, name='comment'),
    path('listing/<int:listing_id>/<int:comment_id>/editComment', views.edit_comment, name="editComment"),
    path('category', views.category_view, name="categoryView"),
    path('category/<str:category_name>', views.category_filter, name="categoryFilter")
]

