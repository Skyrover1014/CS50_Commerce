from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponseNotAllowed
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils import timezone

from .models import User, Listing, Bid, Comment, Watchlist, Category
from .forms import ListingForm, BidForm, CommentForm


def index(request):
    return render(request, "auctions/index.html",{
        "Listings":Listing.objects.all()
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("auctions:index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("auctions:index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("auctions:index"))
    else:
        return render(request, "auctions/register.html")




def add_listing(request):
    if request.method == "POST":
        form = ListingForm(request.POST)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.owner=request.user
            listing.status="active"
            starting_price = int(form.cleaned_data['starting_price'])
            if starting_price <= 0:
                return render(request,"auctions/addListing.html",{
                    "form": form,
                    "message": "the starting price must be greater than 10 dollars! "
                })
            else:
                listing.current_price = starting_price
                listing.save()
                return HttpResponseRedirect(reverse("auctions:index"))
        else:
            return render(request, "auctions/addListing.html",{
                'form': form,
                'message':"Form validation failed. Please check your submit!"
            })
    else:
        form = ListingForm()
        categories = Category.objects.all()
        return render(request, "auctions/addListing.html",{
            'form':form,
            'categories': categories
        })


def get_listing_context(listing_id):
    listing = get_object_or_404(Listing.objects.select_related('category','owner'),id=listing_id)
    context = {
        'listing':listing,
        'bid_times':listing.get_bid_count()
    }
    return listing, context


    
def watch_list(request):
    
        tracked_items = Watchlist.objects.filter(is_tracked=True, user=request.user)

        if tracked_items.exists():
            listings = [ tracked_item.item for tracked_item in tracked_items]
            for listing in listings:
                listing.status = listing.status.upper()
            return render(request, "auctions/watchlist.html",{
                "Listings":listings
            })
        else:
            active_listings = Listing.objects.filter(status='active')
            return render(request, "auctions/watchlist.html",{
                "active_Listings":active_listings
            })

def toggle_watch_list(request, listing_id):
    listing, context = get_listing_context(listing_id)
    if request.method == "POST":
        if Watchlist.objects.filter(item=listing,user=request.user).exists():
            track_item = Watchlist.objects.get(item=listing, user=request.user )
            track_item.is_tracked = not track_item.is_tracked 
            track_item.save()
            print(f"Updated:{track_item}") 
        else: 
            track_item = Watchlist.objects.create(
                item=listing,
                user=request.user,
                is_tracked=True
            )
            print(f"Success: {track_item}")
        return HttpResponseRedirect(reverse("auctions:entryBid", args=(listing_id,)))
    return HttpResponseNotAllowed(['POST'])


def track_status_button(listing, user):
    track_item = Watchlist.objects.filter(item=listing, user=user).first()
    return {
        'track_status': track_item.is_tracked if track_item else False
    }




def add_comment(request, listing_id):
    listing, context = get_listing_context(listing_id)
    if request.method == "POST":
        commentForm = CommentForm(request.POST)
        if commentForm.is_valid():
            comment = commentForm.save(commit=False)
            comment.item = listing
            comment.user = request.user
            comment.save()   
            print(f"Success:{comment}")
            return HttpResponseRedirect(f'{reverse("auctions:entryBid", args=(listing_id,))}?show_comments=all')
    return HttpResponseNotAllowed(['POST'])
 
        
def edit_comment(request, listing_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id) 
    if request.method == "POST":
        commentForm = CommentForm(request.POST, instance=comment)
        if commentForm.is_valid():
            comment.save()
            return HttpResponseRedirect(f'{reverse("auctions:entryBid", args=(listing_id,))}?show_comments=all')
    else:
        commentForm = commentForm(instance=comment)
        return render(request, "auctions/bidPage.html",{
            'commentForm': commentForm,
            'listing_id': listing_id,
            'comment_id':comment_id
        })
    return HttpResponseNotAllowed(['POST'])


def comment_list(listing):
    comments = Comment.objects.select_related('user').filter(item=listing).order_by('-comment_time')
    comments.count
    return {'Comments':comments}


def edit_comment_view (request):
    edit_comment_id = request.GET.get('edit',None)
    if edit_comment_id:
        return{
            'edit_comment_id':int(edit_comment_id),
            'commentForm': CommentForm(instance=Comment.objects.get(id=int(edit_comment_id)))
        }
    return{
        'edit_comment_id': None,
        'commentForm': CommentForm()
    }


def show_all_comments_view(request):
    return { 'show_all_comments' : request.GET.get('show_comments', None) == 'all'}


def entry_bid(request, listing_id):   
    listing, context = get_listing_context(listing_id)

    if request.user.is_authenticated:
        context.update({
            **edit_comment_view(request),
            **show_all_comments_view(request),
            **track_status_button(listing, request.user),
            **comment_list(listing),
            'now':timezone.now(),
            'message':request.GET.get('message',None),
            'is_owner':request.user == listing.owner,
            'is_winner':request.user == listing.winner,
            'bidForm':BidForm(),
        })
    else: 
        context.update({
            **show_all_comments_view(request),
            **comment_list(listing),
            'commentForm':None,
            'bidForm':None,
            'is_owner': False,
            'is_winner':False,
            'message':request.GET.get('message',None),
        })
    print(context)
    return render(request, "auctions/bidPage.html",context)


def place_bid(request, listing_id):
    listing, context = get_listing_context(listing_id)
    if request.method =="POST":
        bidForm = BidForm(request.POST)
        if bidForm.is_valid():
            bid = bidForm.save(commit=False)
            bid.object = listing
            bid.user = request.user
            amount = int(bidForm.cleaned_data['amount'])
            if amount > listing.current_price + 9:
                bid.save()
                print(f"Bid:{bid}")
                return HttpResponseRedirect(reverse("auctions:entryBid", args=(listing_id,)))
            else:
                context.update({
                  'message': "Your bid must be at least $10 higher than the current price.",
                  'bidForm':bidForm,
                  'now':timezone.now(),
                  **comment_list(listing),
                  **track_status_button(listing, request.user)
                })
                print(context)
                return render(request, "auctions/bidPage.html",context)
        else:
            context.update({
                'message':"Your bid must enter number not words.",
                'bidForm':bidForm,
                'now':timezone.now(),
                **comment_list(listing),
                **track_status_button(listing, request.user)                
            })
            return render(request, "auctions/bidPage.html",context)
    return HttpResponseNotAllowed(['POST'])

            
def end_bid(request, listing_id):
    listing, context = get_listing_context(listing_id)
    if request.method == "POST":  
         try:
            latest_bid=Bid.objects.filter(object=listing).latest('bid_time')
            listing.winner = latest_bid.user
            status="ended"
            listing.status = status
            listing.save()
            print(f"Listing:{listing}")
            return HttpResponseRedirect(reverse("auctions:entryBid", args=(listing_id,)))
         except Bid.DoesNotExist:
            listing.status = "active"
            listing.save()
            context.update({
                'message':"Not bids yet. Can't close.",
                'bidForm':BidForm(),
                'is_owner':request.user == listing.owner,
                'is_winner': request.user == listing.winner,
                **track_status_button(listing, request.user),
                **comment_list(listing),
                'now':timezone.now(),
            })
            return render(request, "auctions/bidPage.html", context )
    return HttpResponseNotAllowed(['POST'])
         

def category_view(request):
    Categories = Category.objects.all()
    return render(request, "auctions/category.html",{
        'Categories':Categories,
    })


def category_filter(request, category_name):
    category = get_object_or_404(Category, name=category_name)
    Listings = Listing.objects.filter(category=category, status='active').select_related('category','owner')
    print(f"Filter_filed: {Listings}")

    return render(request, "auctions/categoryFilter.html",{
        'Category': category,
        'Listings':Listings
    })