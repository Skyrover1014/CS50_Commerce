from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Listing, Bid
from decimal import Decimal



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
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


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
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")




def new_listing(request):
    if request.method == "POST":
        user=request.user
        title=request.POST["title"]
        description=request.POST["description"]
        starting_price=request.POST["starting_price"]
        url=request.POST["image_url"]
        status="active"


        starting_price = Decimal(starting_price)

        if starting_price <= 0:
            return render(request,"auctions/newListing.html",{
                "message": "the starting_price must be greater than 0 dollars! "
            })
        else:
            listing = Listing.objects.create(
                user=user,
                title=title,
                description=description,
                starting_price=starting_price,
                current_price=starting_price,
                url=url,
                status=status)
            listing.save()
            return HttpResponseRedirect(reverse("index"))

    return render(request, "auctions/newListing.html")