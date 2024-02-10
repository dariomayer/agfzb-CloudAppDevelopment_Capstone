from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden, HttpResponseServerError
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
# from .restapis import related methods
from .models import CarDealer, CarModel
from .restapis import get_dealers_from_cf, get_dealer_by_id_from_cf, post_request
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
# def about(request):
# ...
def get_about(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/about.html', context)

# Create a `contact` view to return a static contact page
#def contact(request):
def get_contact(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/contact.html', context)

# Create a `login_request` view to handle sign in request
# def login_request(request):
def login_request(request):
    context = {}
    # Handles POST request
    if request.method == "POST":
        # Get username and password from request.POST dictionary
        username = request.POST['username']
        password = request.POST['psw']
        # Try to check if provide credential can be authenticated
        user = authenticate(username=username, password=password)
        if user is not None:
            # If user is valid, call login method to login current user
            login(request, user)
            return redirect('djangoapp:index')
        else:
            # If not, return to login page again
            context['message'] = 'Your username or password is incorrect.'
            return render(request, 'djangoapp/login.html', context)
    else:
        return render(request, 'djangoapp/login.html', context)

# Create a `logout_request` view to handle sign out request
# def logout_request(request):
def logout_request(request):
    # Get the user object based on session id in request
    print("Log out the user `{}`".format(request.user.username))
    # Logout user in the request
    logout(request)
    # Redirect user back to course list view
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
# def registration_request(request):
def registration_request(request):
    context = {}
    # If it is a GET request, just render the registration page
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    # If it is a POST request
    elif request.method == 'POST':
        # Get user information from request.POST
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            # Check if user already exists
            User.objects.get(username=username)
            user_exist = True
            context['message'] = 'A user with that username already exists.'
        except:
            # If not, simply log this is a new user
            logger.debug("{} is new user".format(username))
        # If it is a new user
        if not user_exist:
            # Create user in auth_user table
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            # Login the user and redirect to course list page
            login(request, user)
            return redirect("djangoapp:index")
        else:
            context['message'] = 'Registration failed due to an unexpected error.'
            return render(request, 'djangoapp/registration.html', context)

#----------------------------------------------------------------------------------------------------------------------
# Update the `get_dealerships` view to render the index page with a list of dealerships
    # NOTE: ricorda di avviare la funzione functions/get-dealership.js con comando node get-dealership.js
def get_dealerships(request):
    # Create an empty context dictionary
    context ={}
    if request.method == "GET":
        url = "http://127.0.0.1:3000/dealerships/get"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        # Concat all dealer's short name
        #dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        # Return a list of dealer short name
        #return HttpResponse(dealer_names, context)
        context['dealerships'] = dealerships
        # Verifica se sei sulla pagina "dealer_details"
        # Altrimenti, esegui il rendering della prima pagina
        return render(request, 'djangoapp/index.html', context)



#----------------------------------------------------------------------------------------------------------------------
# Create a `get_dealer_details` view to render the reviews of a dealer
# def get_dealer_details(request, dealer_id):
    # NOTE: ricorda di avviare la funzione functions/reviews.py con comando python3.9 reviews.py
def get_dealer_details(request, dealer_id):
    context = {}
    if request.method == "GET":
        # Get reviews by dealer id
        reviews_url = "http://127.0.0.1:5000/api/get_reviews"
        reviews = get_dealer_by_id_from_cf(reviews_url, dealer_id)

        # Get dealerships
        dealerships_url = "http://127.0.0.1:3000/dealerships/get"
        dealerships = get_dealers_from_cf(dealerships_url)

        # Find the specific dealer from the dealerships
        dealer = next((dealer for dealer in dealerships if dealer.id == dealer_id), None)
        
        # Add reviews and dealer to the context
        context['reviews'] = reviews
        context['dealer'] = dealer  # Assuming 'dealer' is the context variable needed for the dealer information

        return render(request, 'djangoapp/dealer_details.html', context)
        
#----------------------------------------------------------------------------------------------------------------------
# Create a `add_review` view to submit a review
# def add_review(request, dealer_id):
# in the add_review view method:
# First check if user is authenticated because only authenticated users can post reviews for a dealer.
# Create a dictionary object called review to append keys like
# (time, name, dealership, review, purchase) and any attributes you defined in your review-post cloud function.
def add_review(request, dealer_id):
        # Check if user is authenticated
        if not request.user.is_authenticated:
            return HttpResponseForbidden("You must be authenticated to add a review")
        elif request.user.is_authenticated:
            context = {}
            if request.method == 'GET':
                # Get dealerships
                dealerships_url = "http://127.0.0.1:3000/dealerships/get"
                dealerships = get_dealers_from_cf(dealerships_url)

                # Find the specific dealer from the dealerships
                dealer = next((dealer for dealer in dealerships if dealer.id == dealer_id), None)
                
                # Query per ottenere il modello dell'auto associato al dealer
                cars = CarModel.objects.all()
                context['dealer'] = dealer
                context['cars'] = cars
                return render(request, 'djangoapp/add_review.html', context)
            elif request.method == "POST":
                url = "http://127.0.0.1:5000/api/post_review"
                # Create a dictionary object called review to append keys like
                # (time, name, dealership, review, purchase) and any attributes you defined in your review-post cloud function.
                # required_fields = ['id', 'name', 'dealership', 'review', 'purchase', 'purchase_date', 'car_make', 'car_model', 'car_year']
                review = {}
                review["id"] = request.POST['id']
                review["name"] = request.POST['name']
                review["dealership"] = dealer_id
                review["review"] = request.POST['content']
                review["purchase"] = request.POST.get('purchasecheck')== 'on'
                review["purchase_date"] = request.POST['purchasedate']
                review["car_make"] = request.POST['car_make']
                review["car_model"] = request.POST['car_model']
                review["car_year"] = request.POST['car_year']
                result = post_request(url, json_payload=review, dealerId=dealer_id)

                if result is not None:
                    if 'message' in result:
                        success_message = result['message']
                        return HttpResponse(success_message)
                    else:
                        return HttpResponseServerError("Invalid 'message' field in server response.")
                else:
                        return HttpResponseServerError("Server response is not valid JSON.")

            
