from simple_history.models import HistoricalRecords
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Listing(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=64)
    description = models.TextField(max_length=2048)
    starting_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    current_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    url = models.URLField(blank=True, null=True, max_length=500)
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('ended','Ended')
        ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    history = HistoricalRecords()

    def __str__(self):
        return self.title
    def get_bid_count(self):
        return self.bids.count()
    def get_latest_bid(self):
        return self.bids.latest('bid_time')
    

class Bid(models.Model): #Record every bid and take them as one independent data
    object = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='bids')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2,help_text='Enter the what the starting bid should be')
    bid_time = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.user.username} bid {self.amount} on {self.object.title} at {self.bid_time}"
    class Meta:
        ordering = ['-bid_time']
    def save(self, *args, **kwargs):
        self.object.current_price = self.amount
        self.object.save()
        super().save(*args, **kwargs)

class Comment(models.Model):
    title = models.ForeignKey(Listing, related_name='comments',  on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(max_length=2048)
    comment_time = models.TimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Comment: {self.content} by {self.user.username} on {self.title.objects} at {self.comment_time}"
    

