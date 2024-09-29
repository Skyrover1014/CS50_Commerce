from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

# Register your models here.

from .models import User, Listing, Bid, Comment, Category, Watchlist

class ListingAdmin(SimpleHistoryAdmin):
    list_display = ('owner','winner','item','category','description', 'starting_price', 'current_price', 'status', 'created_time', 'updated_time', 'get_bid_count')

class BidAdmin(SimpleHistoryAdmin):
    list_display = ('object', 'user', 'amount', 'bid_time')

class CommentAdmin(SimpleHistoryAdmin):
    list_display = ('item','user','content','comment_time')

class CategoryAdmin(SimpleHistoryAdmin):
    list_display = ('name','description','imageCategory')

class WatchlistAdmin(SimpleHistoryAdmin):
    list_display = ('user','item','is_tracked')

admin.site.register(User)
admin.site.register(Listing, ListingAdmin)
admin.site.register(Bid, BidAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Category,CategoryAdmin)
admin.site.register(Watchlist, WatchlistAdmin)