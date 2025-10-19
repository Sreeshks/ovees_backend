"""
Sample data script to populate the database with initial categories and products.
Run this after starting the application for the first time.
"""
import requests
import json

BASE_URL = "http://localhost:8000"

# Step 1: Register Admin
def register_admin():
    print("📝 Registering admin...")
    response = requests.post(
        f"{BASE_URL}/admin/register",
        json={"username": "admin", "password": "admin123"}
    )
    print(f"Admin registration: {response.json()}")
    return response.json()

# Step 2: Login and get token
def login_admin():
    print("\n🔐 Logging in...")
    response = requests.post(
        f"{BASE_URL}/admin/login",
        json={"username": "admin", "password": "admin123"}
    )
    data = response.json()
    print(f"Login successful! Token: {data['access_token'][:50]}...")
    return data["access_token"]

# Step 3: Create Categories
def create_categories(token):
    print("\n📁 Creating categories...")
    headers = {"Authorization": f"Bearer {token}"}
    
    categories = [
        {"name": "Necklace", "description": "Beautiful necklaces for all occasions"},
        {"name": "Haarams", "description": "Traditional South Indian temple jewelry"},
        {"name": "Earrings", "description": "Elegant earrings collection"},
        {"name": "Maangtikkas", "description": "Traditional forehead jewelry"},
        {"name": "Bangles & Bracelets", "description": "Stylish bangles and bracelets"},
        {"name": "Hipchains", "description": "Traditional waist chains"},
        {"name": "Hair Accessories", "description": "Decorative hair accessories"},
        {"name": "Anklets", "description": "Beautiful anklets"},
        {"name": "Matti", "description": "Traditional Matti jewelry"},
        {"name": "Nose Pin", "description": "Elegant nose pins"},
        {"name": "Rings", "description": "Stunning finger rings"}
    ]
    
    category_ids = {}
    for category in categories:
        response = requests.post(
            f"{BASE_URL}/admin/categories",
            headers=headers,
            json=category
        )
        if response.status_code == 201:
            cat_data = response.json()
            category_ids[category["name"]] = cat_data["id"]
            print(f"✅ Created: {category['name']} (ID: {cat_data['id']})")
        else:
            print(f"❌ Failed: {category['name']} - {response.text}")
    
    return category_ids

# Step 4: Create Sample Products
def create_products(token, category_ids):
    print("\n🛍️ Creating sample products...")
    headers = {"Authorization": f"Bearer {token}"}
    
    products = [
        # 99 Store Products
        {
            "product_code": "NK99001",
            "name": "Simple Gold Chain",
            "details": "Delicate gold-plated chain, perfect for daily wear",
            "price": 99,
            "category_id": category_ids["Necklace"],
            "images": ["chain1.jpg"],
            "stock_quantity": 100
        },
        {
            "product_code": "ER99001",
            "name": "Pearl Studs",
            "details": "Classic pearl stud earrings",
            "price": 99,
            "category_id": category_ids["Earrings"],
            "images": ["pearl_studs.jpg"],
            "stock_quantity": 150
        },
        {
            "product_code": "RG99001",
            "name": "Simple Ring",
            "details": "Elegant simple design ring",
            "price": 99,
            "category_id": category_ids["Rings"],
            "images": ["ring1.jpg"],
            "stock_quantity": 200
        },
        
        # 199 Store Products
        {
            "product_code": "NK199001",
            "name": "Designer Necklace",
            "details": "Beautiful designer necklace with intricate patterns",
            "price": 199,
            "category_id": category_ids["Necklace"],
            "images": ["designer_necklace.jpg"],
            "stock_quantity": 75
        },
        {
            "product_code": "ER199001",
            "name": "Jhumka Earrings",
            "details": "Traditional jhumka earrings with stone work",
            "price": 199,
            "category_id": category_ids["Earrings"],
            "images": ["jhumka.jpg"],
            "stock_quantity": 80
        },
        {
            "product_code": "BG199001",
            "name": "Designer Bangles Set",
            "details": "Set of 4 designer bangles",
            "price": 199,
            "category_id": category_ids["Bangles & Bracelets"],
            "images": ["bangles.jpg"],
            "stock_quantity": 60
        },
        
        # Premium Products
        {
            "product_code": "HR001",
            "name": "Temple Haaram",
            "details": "Exquisite temple jewelry haaram with Lakshmi pendant",
            "price": 599,
            "category_id": category_ids["Haarams"],
            "images": ["haaram1.jpg", "haaram2.jpg"],
            "stock_quantity": 30
        },
        {
            "product_code": "MT001",
            "name": "Bridal Maangtikka",
            "details": "Stunning bridal maangtikka with kundan work",
            "price": 399,
            "category_id": category_ids["Maangtikkas"],
            "images": ["maangtikka.jpg"],
            "stock_quantity": 40
        },
        {
            "product_code": "HP001",
            "name": "Traditional Hipchain",
            "details": "Gold-plated traditional hipchain with intricate design",
            "price": 499,
            "category_id": category_ids["Hipchains"],
            "images": ["hipchain.jpg"],
            "stock_quantity": 25
        },
        {
            "product_code": "NP001",
            "name": "Diamond Look Nose Pin",
            "details": "Sparkling diamond-look nose pin",
            "price": 149,
            "category_id": category_ids["Nose Pin"],
            "images": ["nosepin.jpg"],
            "stock_quantity": 120
        }
    ]
    
    product_ids = []
    for product in products:
        response = requests.post(
            f"{BASE_URL}/admin/products",
            headers=headers,
            json=product
        )
        if response.status_code == 201:
            prod_data = response.json()
            product_ids.append(prod_data["id"])
            print(f"✅ Created: {product['name']} (₹{product['price']})")
        else:
            print(f"❌ Failed: {product['name']} - {response.text}")
    
    return product_ids

# Step 5: Create Sample Combo
def create_combo(token, product_ids):
    print("\n🎁 Creating sample combo...")
    headers = {"Authorization": f"Bearer {token}"}
    
    combo = {
        "combo_code": "BRIDAL001",
        "name": "Bridal Jewelry Set",
        "description": "Complete bridal jewelry set with necklace, earrings, and maangtikka",
        "combo_price": 999,
        "is_active": True,
        "products": [
            {"product_id": product_ids[3], "quantity": 1},  # Designer Necklace
            {"product_id": product_ids[4], "quantity": 1},  # Jhumka Earrings
            {"product_id": product_ids[7], "quantity": 1}   # Bridal Maangtikka
        ]
    }
    
    response = requests.post(
        f"{BASE_URL}/admin/combos",
        headers=headers,
        json=combo
    )
    
    if response.status_code == 201:
        print(f"✅ Created combo: {combo['name']}")
    else:
        print(f"❌ Failed to create combo: {response.text}")

# Step 6: Add New Arrivals
def add_new_arrivals(token, product_ids):
    print("\n🆕 Adding new arrivals...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Add first 3 products as new arrivals
    for product_id in product_ids[:3]:
        response = requests.post(
            f"{BASE_URL}/admin/new-arrivals",
            headers=headers,
            json={"product_id": product_id}
        )
        if response.status_code == 201:
            print(f"✅ Added product {product_id} to new arrivals")

# Main execution
def main():
    print("🎀 Ovees Jewelry Store - Sample Data Setup\n")
    print("=" * 60)
    
    try:
        # Register admin
        register_admin()
        
        # Login
        token = login_admin()
        
        # Create categories
        category_ids = create_categories(token)
        
        # Create products
        product_ids = create_products(token, category_ids)
        
        # Create combo
        if len(product_ids) >= 3:
            create_combo(token, product_ids)
        
        # Add new arrivals
        if len(product_ids) >= 3:
            add_new_arrivals(token, product_ids)
        
        print("\n" + "=" * 60)
        print("✅ Sample data setup completed successfully!")
        print("\n📊 Summary:")
        print(f"   - Categories: {len(category_ids)}")
        print(f"   - Products: {len(product_ids)}")
        print(f"   - Combos: 1")
        print(f"   - New Arrivals: {min(3, len(product_ids))}")
        print("\n🔗 Access the API:")
        print(f"   - Documentation: {BASE_URL}/docs")
        print(f"   - Admin Token: Use the token from login response")
        print("\n🔐 Admin Credentials:")
        print("   - Username: admin")
        print("   - Password: admin123")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("Make sure the API server is running at http://localhost:8000")

if __name__ == "__main__":
    main()
