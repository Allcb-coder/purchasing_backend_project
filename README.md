# Purchasing Backend

A Django REST Framework backend for an automated purchasing system.

## Features

- **User Management**: Registration, authentication, profile management
- **Product Catalog**: Categories, products with filtering and search
- **Supplier Management**: Multiple suppliers with product listings
- **Shopping Cart**: Add, update, remove items
- **Order Processing**: Complete order flow with multiple items
- **YAML Import**: Import products from YAML files
- **API Documentation**: Swagger/ReDoc auto-generated docs

## Tech Stack

- **Backend**: Django 4.2.7 + Django REST Framework
- **Database**: SQLite (development), PostgreSQL ready
- **Authentication**: Token-based authentication
- **API Docs**: drf-yasg for Swagger/ReDoc

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Allcb-coder/purchasing_backend_project.git
   cd purchasing_backend
2. **Create and activate virtual environment**

       python -m venv .venv
       source .venv/bin/activate  # On Windows: .venv\Scripts\activate
3. **Install dependencies**

     pip install -r requirements.txt