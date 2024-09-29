
from django import forms
from .models import Listing, Comment, Bid 

class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['item','category','description','starting_price','url']
        widgets = {
            'item': forms.TextInput(attrs={'placeholder':'Enter title'}),
            'description': forms.Textarea(attrs={'placeholder':'Enter description'}),
            'starting_price':forms.NumberInput(attrs={'min': 0 }),
            'url':forms.URLInput(attrs={'placeholder':'Enter image URL or Not'}),
        }

class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['amount']
        widgets = {
            'amount':forms.TextInput(attrs={'placeholder':'Bid'}),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.TextInput(attrs={'placeholder':'Leave your comment'}),
        }

