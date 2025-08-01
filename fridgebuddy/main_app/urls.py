from django.urls import path
# Import views to connect routes to view functions
from . import views 

urlpatterns = [
    # Define the home route
    path('', views.home, name='home'),
    # Define the about route
    path('about/', views.about, name='about'),
    # Index of food in fridge
    path('food/', views.food_index, name='food-index'),
    # Detail view for a specific food item
    path('food/<int:food_id>/', views.food_detail, name='food-detail'),
    # TODO: Add class-based views for CRUD operations after model migration
    # path('food/create/', views.FoodCreate.as_view(), name='food-create'),
    # path('food/<int:pk>/update/', views.FoodUpdate.as_view(), name='food-update'),
    # path('food/<int:pk>/delete/', views.FoodDelete.as_view(), name='food-delete'),
   
]