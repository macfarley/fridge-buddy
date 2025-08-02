from django.core.management.base import BaseCommand
from main_app.models import CatalogFood
import requests
import json

class Command(BaseCommand):
    help = 'Populate food catalog from external API'

    def add_arguments(self, parser):
        parser.add_argument(
            '--source',
            type=str,
            choices=['usda', 'spoonacular', 'json'],
            default='json',
            help='Data source to use for populating catalog'
        )
        parser.add_argument(
            '--file',
            type=str,
            help='Path to JSON file (when using json source)'
        )

    def handle(self, *args, **options):
        source = options['source']
        
        if source == 'json':
            self.populate_from_json(options.get('file'))
        elif source == 'usda':
            self.populate_from_usda()
        elif source == 'spoonacular':
            self.populate_from_spoonacular()

    def populate_from_json(self, file_path=None):
        """Populate from a local JSON file"""
        if not file_path:
            # Default sample data
            sample_foods = [
                {
                    "name": "Chicken Breast",
                    "category": "MEAT",
                    "description": "Boneless, skinless chicken breast"
                },
                {
                    "name": "Whole Milk",
                    "category": "DAIRY",
                    "description": "Fresh whole milk, 3.25% fat"
                },
                {
                    "name": "Bananas",
                    "category": "FRUIT",
                    "description": "Fresh yellow bananas"
                },
                {
                    "name": "Spinach",
                    "category": "VEGETABLE",
                    "description": "Fresh baby spinach leaves"
                },
                {
                    "name": "White Bread",
                    "category": "GRAIN",
                    "description": "Sliced white bread loaf"
                },
                {
                    "name": "Cheddar Cheese",
                    "category": "DAIRY",
                    "description": "Sharp cheddar cheese block"
                },
                {
                    "name": "Ground Beef",
                    "category": "MEAT",
                    "description": "80/20 ground beef"
                },
                {
                    "name": "Apples",
                    "category": "FRUIT",
                    "description": "Fresh red apples"
                },
                {
                    "name": "Carrots",
                    "category": "VEGETABLE", 
                    "description": "Fresh baby carrots"
                },
                {
                    "name": "Brown Rice",
                    "category": "GRAIN",
                    "description": "Long grain brown rice"
                }
            ]
            foods_data = sample_foods
        else:
            with open(file_path, 'r') as f:
                foods_data = json.load(f)

        created_count = 0
        for food_data in foods_data:
            food, created = CatalogFood.objects.get_or_create(
                name=food_data['name'],
                defaults={
                    'category': food_data['category'],
                    'description': food_data.get('description', ''),
                    'image_url': food_data.get('image_url', '')
                }
            )
            if created:
                created_count += 1
                self.stdout.write(f"Created: {food.name}")
            else:
                self.stdout.write(f"Already exists: {food.name}")

        self.stdout.write(
            self.style.SUCCESS(f"Successfully created {created_count} new food items")
        )

    def populate_from_usda(self):
        """Populate from USDA FoodData Central API (Free)"""
        # You'll need to get a free API key from: https://fdc.nal.usda.gov/api-guide.html
        api_key = "YOUR_USDA_API_KEY"  # Replace with actual key
        
        # Example search for common foods
        common_searches = [
            "chicken breast", "milk", "banana", "spinach", "bread",
            "cheese", "ground beef", "apple", "carrot", "rice"
        ]
        
        for search_term in common_searches:
            url = f"https://api.nal.usda.gov/fdc/v1/foods/search"
            params = {
                'query': search_term,
                'api_key': api_key,
                'pageSize': 5,
                'dataType': ['Foundation', 'SR Legacy']
            }
            
            try:
                response = requests.get(url, params=params)
                data = response.json()
                
                for food_item in data.get('foods', []):
                    # Map USDA categories to your categories
                    category_mapping = {
                        'Dairy and Egg Products': 'DAIRY',
                        'Spices and Herbs': 'SPICE',
                        'Baby Foods': 'OTHER',
                        'Fats and Oils': 'OTHER',
                        'Poultry Products': 'MEAT',
                        'Soups, Sauces, and Gravies': 'OTHER',
                        'Sausages and Luncheon Meats': 'MEAT',
                        'Breakfast Cereals': 'GRAIN',
                        'Fruits and Fruit Juices': 'FRUIT',
                        'Pork Products': 'MEAT',
                        'Vegetables and Vegetable Products': 'VEGETABLE',
                        'Nut and Seed Products': 'OTHER',
                        'Beef Products': 'MEAT',
                        'Beverages': 'BEVERAGE',
                        'Finfish and Shellfish Products': 'SEAFOOD',
                        'Legumes and Legume Products': 'VEGETABLE',
                        'Lamb, Veal, and Game Products': 'MEAT',
                        'Baked Products': 'GRAIN',
                        'Sweets': 'OTHER',
                        'Cereal Grains and Pasta': 'GRAIN',
                        'Fast Foods': 'OTHER',
                        'Meals, Entrees, and Side Dishes': 'OTHER',
                        'Snacks': 'OTHER'
                    }
                    
                    usda_category = food_item.get('foodCategory', '')
                    our_category = category_mapping.get(usda_category, 'OTHER')
                    
                    food, created = CatalogFood.objects.get_or_create(
                        name=food_item['description'][:100],  # Truncate if too long
                        defaults={
                            'category': our_category,
                            'description': food_item.get('additionalDescriptions', '')
                        }
                    )
                    
                    if created:
                        self.stdout.write(f"Created: {food.name}")
                        
            except Exception as e:
                self.stdout.write(f"Error fetching {search_term}: {str(e)}")

    def populate_from_spoonacular(self):
        """Populate from Spoonacular API (Paid, but has free tier)"""
        api_key = "YOUR_SPOONACULAR_API_KEY"  # Replace with actual key
        
        url = "https://api.spoonacular.com/food/ingredients/search"
        
        # Common ingredient searches
        searches = [
            "chicken", "milk", "banana", "spinach", "bread",
            "cheese", "beef", "apple", "carrot", "rice"
        ]
        
        for search_term in searches:
            params = {
                'query': search_term,
                'apiKey': api_key,
                'number': 10
            }
            
            try:
                response = requests.get(url, params=params)
                data = response.json()
                
                for ingredient in data.get('results', []):
                    # You'd need to map Spoonacular categories to yours
                    food, created = CatalogFood.objects.get_or_create(
                        name=ingredient['name'],
                        defaults={
                            'category': 'OTHER',  # You'd implement category mapping
                            'description': f"Ingredient: {ingredient['name']}",
                            'image_url': f"https://spoonacular.com/cdn/ingredients_100x100/{ingredient['image']}"
                        }
                    )
                    
                    if created:
                        self.stdout.write(f"Created: {food.name}")
                        
            except Exception as e:
                self.stdout.write(f"Error fetching {search_term}: {str(e)}")
