# 🎀 Ovees Jewelry Store - Backend API

A comprehensive FastAPI backend for Ovees Jewelry E-commerce Platform with admin management and public product browsing.

## ✨ Features

### 🔐 Admin Features
- Secure JWT-based authentication
- Product management (CRUD operations)
- Category management
- Combo/Bundle creation
- New arrivals management

### 🛍️ Public Features
- Browse all products with pagination
- Filter by categories
- Search products by name/details
- Sort by price (high/low) or date (newest/oldest)
- Special collections:
  - **99 Store** - All products priced at ₹99
  - **199 Store** - All products priced at ₹199
  - **Combos** - Product bundles at special prices
  - **New Arrivals** - Latest products

## 📋 Database Schema

### Categories
- Necklace
- Haarams
- Earrings
- Maangtikkas
- Bangles & Bracelets
- Hipchains
- Hair Accessories
- Anklets
- Matti
- Nose Pin
- Rings

### Tables
1. **Products** - Main product catalog
2. **Categories** - Product categories
3. **Combos** - Product bundles
4. **ComboProducts** - Junction table for combo products
5. **NewArrivals** - Featured new products
6. **Admins** - Admin users

## 🚀 Quick Start

### 1. Clone & Setup
```bash
cd Ovees_backend
source ovees_venv/bin/activate  # On Windows: ovees_venv\Scripts\activate
```

### 2. Environment Variables
Create a `.env` file:
```bash
cp .env.example .env
```

Edit `.env` and update:
```
SECRET_KEY=your-secure-secret-key-here
CORS_ORIGINS=http://localhost:3000
```

### 3. Run the Application
```bash
python main.py
```

Or with uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

### 4. Access Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔑 Admin Setup

### Register First Admin
```bash
POST /admin/register
{
  "username": "admin",
  "password": "your_secure_password"
}
```

### Login
```bash
POST /admin/login
{
  "username": "admin",
  "password": "your_secure_password"
}
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

Use the access token in subsequent requests:
```
Authorization: Bearer <access_token>
```

## 📚 API Endpoints

### Public Endpoints (No Auth Required)

#### Products
```
GET  /products                          # Get all products
GET  /products/{product_code}           # Get single product
GET  /products/category/{category_name} # Filter by category
GET  /products/collection/99-store      # 99 store products
GET  /products/collection/199-store     # 199 store products
```

#### Categories
```
GET  /categories                        # Get all categories
GET  /categories/{category_id}          # Get single category
```

#### Combos
```
GET  /combos                            # Get all combos
GET  /combos/{combo_code}               # Get single combo
```

#### New Arrivals
```
GET  /new-arrivals                      # Get new arrivals
```

#### Stats
```
GET  /stats/products-count              # Get product statistics
```

### Admin Endpoints (Auth Required)

#### Categories
```
POST   /admin/categories                # Create category
PUT    /admin/categories/{id}           # Update category
DELETE /admin/categories/{id}           # Delete category
```

#### Products
```
POST   /admin/products                  # Create product
PUT    /admin/products/{product_code}   # Update product
DELETE /admin/products/{product_code}   # Delete product
```

#### Combos
```
POST   /admin/combos                    # Create combo
PUT    /admin/combos/{combo_code}       # Update combo
DELETE /admin/combos/{combo_code}       # Delete combo
```

#### New Arrivals
```
POST   /admin/new-arrivals              # Add to new arrivals
DELETE /admin/new-arrivals/{product_id} # Remove from new arrivals
PATCH  /admin/new-arrivals/{product_id}/toggle  # Toggle active status
```

## 📝 Example Requests

### Create a Product
```bash
POST /admin/products
Authorization: Bearer <token>

{
  "product_code": "NK001",
  "name": "Gold Plated Necklace",
  "details": "Beautiful gold plated necklace with intricate design",
  "price": 199,
  "category_id": 1,
  "images": ["image1.jpg", "image2.jpg"],
  "stock_quantity": 50,
  "is_active": true
}
```

### Create a Combo
```bash
POST /admin/combos
Authorization: Bearer <token>

{
  "combo_code": "COMBO001",
  "name": "Bridal Set",
  "description": "Complete bridal jewelry set",
  "combo_price": 999,
  "is_active": true,
  "products": [
    {"product_id": 1, "quantity": 1},
    {"product_id": 2, "quantity": 1},
    {"product_id": 3, "quantity": 2}
  ]
}
```

### Filter & Sort Products
```bash
GET /products?category_id=1&sort_by=price_low&min_price=50&max_price=200&skip=0&limit=20
```

## 🛠️ Technology Stack

- **FastAPI** - Modern web framework
- **SQLAlchemy** - ORM
- **SQLite** - Database
- **Pydantic** - Data validation
- **JWT** - Authentication
- **Uvicorn** - ASGI server

## 📦 Project Structure

```
Ovees_backend/
├── main.py                 # Application entry point
├── requirements.txt        # Dependencies
├── .env                    # Environment variables
├── ovees.db               # SQLite database (auto-generated)
├── models/                # Database models
│   ├── product.py
│   ├── category.py
│   ├── combo.py
│   ├── new_arrival.py
│   └── admin.py
├── schemas/               # Pydantic schemas
│   ├── product.py
│   ├── category.py
│   ├── combo.py
│   ├── new_arrival.py
│   └── admin.py
├── routers/               # API routes
│   ├── admin.py
│   └── public.py
├── database/              # Database configuration
│   └── connection.py
└── utils/                 # Utilities
    └── auth.py
```

## 🔒 Security

- Passwords are hashed using bcrypt
- JWT tokens for authentication
- Admin-only routes protected
- CORS configuration for frontend
- Environment variables for secrets

## 📊 Query Parameters

### Products Endpoint
- `skip`: Pagination offset (default: 0)
- `limit`: Items per page (default: 100, max: 100)
- `sort_by`: price_low | price_high | newest | oldest
- `min_price`: Minimum price filter
- `max_price`: Maximum price filter
- `category_id`: Filter by category ID
- `search`: Search in name and details
- `is_active`: Show active/inactive products

## 🎯 Future Enhancements

- [ ] Image upload functionality
- [ ] Order management
- [ ] Customer management
- [ ] Payment gateway integration
- [ ] Inventory tracking
- [ ] Sales analytics
- [ ] Email notifications
- [ ] PostgreSQL migration for production

## 👨‍💻 Development

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run in Development
```bash
uvicorn main:app --reload
```

### Database Migrations
The database is automatically initialized on first run.

## 📄 License

Private - Ovees Jewelry Store

## 🤝 Support

For support, contact: support@ovees.com

---

**Built with ❤️ for Ovees Jewelry**
