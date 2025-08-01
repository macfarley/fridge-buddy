# Fridge Buddy 🥗

A Django web application for managing food inventory across multiple containers (fridge, freezer, pantry, shopping lists). Track expiration dates, organize by categories, and reduce food waste with smart organization.

## Current Features

### 🏠 Core Functionality
- **Container Management**: Create and organize multiple containers (Fridge, Freezer, Pantry, Shopping List)
- **Food Catalog**: Global database of food items with categories, descriptions, and images
- **User-Friendly URLs**: Semantic routing with `/my-lists/` for personal containers and `/food-catalog/` for browsing

### 📋 Current Models
- **CatalogFood**: Global food catalog with categories (dairy, meat, seafood, vegetables, fruits, grains, condiments, beverages, leftovers, other)
- **Container**: User-owned containers with types (Fridge, Freezer, Pantry, Shopping)
- **ContainerFood**: Food items within specific containers with quantity and expiration tracking

### 🎨 Templates & Views
- **Class-based views** for consistent CRUD operations
- **Responsive templates** with semantic HTML structure
- **Dynamic form handling** with Django forms
- **Conditional delete confirmations** for different object types

### 🛣️ URL Structure
```
/                           # Home page
/about/                     # About page
/my-lists/                  # User's containers index
/my-lists/<id>/             # Food items in specific container
/my-lists/create/           # Create new container
/my-lists/<id>/update/      # Edit container
/my-lists/<id>/delete/      # Delete container
/food-catalog/              # Browse all food items
/food-catalog/<id>/         # Food item details
/food-catalog/create/       # Add new food to catalog
/food-catalog/<id>/update/  # Edit food item
/food-catalog/<id>/delete/  # Delete food item
```

## Technology Stack
- **Backend**: Django 5.2.4
- **Database**: SQLite (development)
- **Frontend**: HTML5, CSS3, Django Templates
- **Dependency Management**: Pipenv
- **Version Control**: Git

## Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/macfarley/fridge-buddy.git
   cd fridge-buddy
   ```

2. **Install dependencies**
   ```bash
   pipenv install
   pipenv shell
   ```

3. **Navigate to Django project**
   ```bash
   cd fridgebuddy
   ```

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Start development server**
   ```bash
   python manage.py runserver
   ```

6. **Visit** `http://127.0.0.1:8000/`

## Project Structure
```
fridge-buddy/
├── Pipfile                 # Python dependencies
├── fridgebuddy/           # Django project directory
│   ├── manage.py          # Django management script
│   ├── fridgebuddy/       # Project settings
│   └── main_app/          # Main application
│       ├── models.py      # Database models
│       ├── views.py       # Class-based views
│       ├── urls.py        # URL routing
│       ├── static/        # CSS, images, JavaScript
│       └── templates/     # HTML templates
│           ├── base.html
│           ├── home.html
│           ├── about.html
│           ├── catalog_food/
│           ├── containers/
│           └── main_app/
```

## Next Steps & Planned Features

### 🎯 Immediate Priorities
1. **Complete Template Implementation**
   - Fill in `container_form.html` for embedded form functionality
   - Create missing detail templates
   - Add proper error handling and validation messages

2. **User Authentication**
   - Implement Django auth system
   - Add user registration/login
   - Filter containers by logged-in user

### 🚀 Enhanced User Experience
3. **Action Buttons & Quick Actions**
   - Add "Add to List" buttons in food catalog
   - Implement "Move between lists" functionality
   - Quick remove/delete actions for container items
   - AJAX-powered interactions for seamless UX

4. **Smart Expiration Management**
   - Automatic expiration date calculation based on food category
   - Visual indicators for expiring items (color coding)
   - Notifications for items nearing expiration
   - Smart suggestions for food usage

### 📊 Advanced Features
5. **Analytics & Insights**
   - Food waste tracking
   - Usage patterns and statistics
   - Shopping suggestions based on consumption
   - Meal planning integration

6. **Enhanced Food Management**
   - Barcode scanning for easy item addition
   - Nutritional information integration
   - Recipe suggestions based on available ingredients
   - Grocery list optimization

### 🔧 Technical Improvements
7. **Performance & Scalability**
   - Database optimization and indexing
   - Caching for frequently accessed data
   - API endpoints for mobile app development
   - Image upload and storage for custom food items

8. **Quality of Life**
   - Dark mode theme
   - Mobile-responsive design improvements
   - Keyboard shortcuts for power users
   - Export/import functionality for data backup

## Contributing
This is a learning project, but suggestions and improvements are welcome! Please feel free to:
- Report bugs or issues
- Suggest new features
- Submit pull requests
- Share feedback on user experience

## License
MIT License - feel free to use this project for learning or personal use.

---
*Built with ❤️ using Django*
