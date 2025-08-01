# main_app/views.py

from django.shortcuts import render

# Import HttpResponse to send text-based responses
from django.http import HttpResponse

# Define the home view function
def home(request):
    # Render the home template
    return render(request, 'home.html')
# Define the about page
def about(request):
    return render(request, 'about.html')
# Define the food index view function
def food_index(request):
    # Render the food index template
    return render(request, 'food/index.html')
# Define the food detail view function
def food_detail(request, food_id):
    # Render the food detail template
    return render(request, 'food/detail.html', {'food_id': food_id})
