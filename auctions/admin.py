from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

# Register your models here.

from .models import User, Listing, Bid, Comment

class ListingAdmin(SimpleHistoryAdmin):
    list_display = ('title', 'description', 'starting_price', 'current_price', 'status', 'created_time', 'updated_time', 'get_bid_count')

class BidAdmin(SimpleHistoryAdmin):
    list_display = ('object', 'user', 'amount', 'bid_time')

admin.site.register(User)
admin.site.register(Listing, ListingAdmin)
admin.site.register(Bid, BidAdmin)
admin.site.register(Comment)