"""
Sample data script to populate the database with 100+ products, banners, and comprehensive data.
Run this after starting the application for the first time.
"""
import requests
import json
import time
from io import BytesIO

BASE_URL = "http://localhost:8000"

# Real jewelry image URLs from public sources
JEWELRY_IMAGES = {
    "necklace": [
        "https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f",
        "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338",
        "https://images.unsplash.com/photo-1506630448388-4e683c67ddb0",
        "https://images.unsplash.com/photo-1611591437281-460bfbe1220a",
        "https://images.unsplash.com/photo-1535632066927-ab7c9ab60908",
    ],
    "earrings": [
        "https://images.unsplash.com/photo-1535556116002-6281ff3e9f43",
        "https://images.unsplash.com/photo-1595327743691-3b5e4e88f7b5",
        "https://images.unsplash.com/photo-1617038260897-41a1f14a8ca0",
        "https://images.unsplash.com/photo-1588444650973-294eb2c7e6cc",
        "https://images.unsplash.com/photo-1618038454548-f5fc74d6da25",
    ],
    "bangles": [
        "https://images.unsplash.com/photo-1611652022419-a9419f74343a",
        "https://images.unsplash.com/photo-1601121141461-9d6647bca1ed",
        "https://images.unsplash.com/photo-1611591437281-460bfbe1220a",
        "https://images.unsplash.com/photo-1602751584552-8ba73aad10e1",
    ],
    "rings": [
        "https://images.unsplash.com/photo-1605100804763-247f67b3557e",
        "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338",
        "https://images.unsplash.com/photo-1603561591411-07134e71a2a9",
        "https://images.unsplash.com/photo-1611591437281-460bfbe1220a",
    ],
    "anklets": [
        "https://images.unsplash.com/photo-1611652022419-a9419f74343a",
        "https://images.unsplash.com/photo-1601121141461-9d6647bca1ed",
    ],
    "general": [
        "https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f",
        "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338",
        "https://images.unsplash.com/photo-1611591437281-460bfbe1220a",
    ]
}

BANNER_IMAGES = [
    "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338",
    "https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f",
    "https://images.unsplash.com/photo-1611591437281-460bfbe1220a",
    "https://images.unsplash.com/photo-1535632066927-ab7c9ab60908",
    "https://images.unsplash.com/photo-1617038260897-41a1f14a8ca0",
]

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

# Step 4: Create 100+ Sample Products
def create_products(token, category_ids):
    print("\n🛍️ Creating 100+ sample products...")
    headers = {"Authorization": f"Bearer {token}"}
    
    products = []
    product_count = 1
    
    # Necklaces (20 products)
    necklace_designs = ["Gold Chain", "Silver Chain", "Pearl Necklace", "Diamond Necklace", "Choker", 
                        "Temple Jewelry", "Antique Necklace", "Designer Necklace", "Beaded Necklace", "Kundan Necklace"]
    for i, design in enumerate(necklace_designs):
        for variant in ["Simple", "Designer"]:
            price = 99 if i < 2 else (199 if i < 5 else 399 + (i * 50))
            offer_price = price - 20 if i % 3 == 0 else None
            # Assign 2-3 images from the necklace category
            image_idx = (i * 2 + (1 if variant == "Designer" else 0)) % len(JEWELRY_IMAGES["necklace"])
            product_images = [
                JEWELRY_IMAGES["necklace"][image_idx],
                JEWELRY_IMAGES["necklace"][(image_idx + 1) % len(JEWELRY_IMAGES["necklace"])]
            ]
            products.append({
                "product_code": f"NK{product_count:03d}",
                "name": f"{variant} {design}",
                "details": f"Beautiful {variant.lower()} {design.lower()} perfect for all occasions. Handcrafted with care.",
                "normal_price": price,
                "offer_price": offer_price,
                "category_id": category_ids["Necklace"],
                "images": product_images,
                "stock_quantity": 50 + (i * 10)
            })
            product_count += 1
    
    # Earrings (20 products)
    earring_designs = ["Jhumka", "Studs", "Hoops", "Chandbali", "Drop Earrings", 
                       "Temple Earrings", "Pearl Earrings", "Diamond Studs", "Hanging Earrings", "Clip-on"]
    for i, design in enumerate(earring_designs):
        for variant in ["Classic", "Modern"]:
            price = 99 if i < 3 else (199 if i < 6 else 299 + (i * 30))
            offer_price = price - 15 if i % 2 == 0 else None
            # Assign 2-3 images from the earrings category
            image_idx = (i * 2 + (1 if variant == "Modern" else 0)) % len(JEWELRY_IMAGES["earrings"])
            product_images = [
                JEWELRY_IMAGES["earrings"][image_idx],
                JEWELRY_IMAGES["earrings"][(image_idx + 1) % len(JEWELRY_IMAGES["earrings"])]
            ]
            products.append({
                "product_code": f"ER{product_count:03d}",
                "name": f"{variant} {design}",
                "details": f"Elegant {variant.lower()} {design.lower()} that add charm to your look.",
                "normal_price": price,
                "offer_price": offer_price,
                "category_id": category_ids["Earrings"],
                "images": product_images,
                "stock_quantity": 80 + (i * 5)
            })
            product_count += 1
    
    # Bangles & Bracelets (15 products)
    bangle_designs = ["Gold Bangles", "Silver Bangles", "Designer Bangles", "Stone Bangles", "Antique Bangles"]
    for i, design in enumerate(bangle_designs):
        for j, qty in enumerate(["Set of 2", "Set of 4", "Set of 6"]):
            price = 199 if "2" in qty else (299 if "4" in qty else 499)
            offer_price = price - 50 if i % 2 == 0 else None
            # Assign 2 images from the bangles category
            image_idx = (i * 3 + j) % len(JEWELRY_IMAGES["bangles"])
            product_images = [
                JEWELRY_IMAGES["bangles"][image_idx],
                JEWELRY_IMAGES["bangles"][(image_idx + 1) % len(JEWELRY_IMAGES["bangles"])]
            ]
            products.append({
                "product_code": f"BG{product_count:03d}",
                "name": f"{design} - {qty}",
                "details": f"Beautiful {design.lower()} {qty.lower()} for traditional and modern look.",
                "normal_price": price,
                "offer_price": offer_price,
                "category_id": category_ids["Bangles & Bracelets"],
                "images": product_images,
                "stock_quantity": 60 + (i * 8)
            })
            product_count += 1
    
    # Rings (15 products)
    ring_designs = ["Gold Ring", "Silver Ring", "Diamond Ring", "Stone Ring", "Band Ring"]
    for i, design in enumerate(ring_designs):
        for j, style in enumerate(["Simple", "Designer", "Antique"]):
            price = 99 if style == "Simple" else (199 if style == "Designer" else 349)
            offer_price = price - 20 if i % 3 == 0 else None
            # Assign 2 images from the rings category
            image_idx = (i * 3 + j) % len(JEWELRY_IMAGES["rings"])
            product_images = [
                JEWELRY_IMAGES["rings"][image_idx],
                JEWELRY_IMAGES["rings"][(image_idx + 1) % len(JEWELRY_IMAGES["rings"])]
            ]
            products.append({
                "product_code": f"RG{product_count:03d}",
                "name": f"{style} {design}",
                "details": f"{style} {design.lower()} perfect for everyday wear or special occasions.",
                "normal_price": price,
                "offer_price": offer_price,
                "category_id": category_ids["Rings"],
                "images": product_images,
                "stock_quantity": 100 + (i * 10)
            })
            product_count += 1
    
    # Haarams (10 products)
    haaram_designs = ["Temple Haaram", "Lakshmi Haaram", "Peacock Haaram", "Antique Haaram", "Designer Haaram"]
    for i, design in enumerate(haaram_designs):
        for j, variant in enumerate(["Traditional", "Modern"]):
            price = 599 + (i * 100)
            offer_price = price - 100 if i % 2 == 0 else None
            # Assign 2 images from the necklace category (similar to haarams)
            image_idx = (i * 2 + j) % len(JEWELRY_IMAGES["necklace"])
            product_images = [
                JEWELRY_IMAGES["necklace"][image_idx],
                JEWELRY_IMAGES["necklace"][(image_idx + 1) % len(JEWELRY_IMAGES["necklace"])]
            ]
            products.append({
                "product_code": f"HR{product_count:03d}",
                "name": f"{variant} {design}",
                "details": f"Exquisite {variant.lower()} {design.lower()} with detailed craftsmanship.",
                "normal_price": price,
                "offer_price": offer_price,
                "category_id": category_ids["Haarams"],
                "images": product_images,
                "stock_quantity": 20 + (i * 3)
            })
            product_count += 1
    
    # Maangtikkas (10 products)
    maangtikka_designs = ["Bridal Maangtikka", "Pearl Maangtikka", "Stone Maangtikka", "Gold Maangtikka", "Diamond Maangtikka"]
    for i, design in enumerate(maangtikka_designs):
        for j, style in enumerate(["Classic", "Contemporary"]):
            price = 299 + (i * 50)
            offer_price = price - 30 if i % 2 == 0 else None
            # Assign 2 images from the general jewelry category
            image_idx = (i * 2 + j) % len(JEWELRY_IMAGES["general"])
            product_images = [
                JEWELRY_IMAGES["general"][image_idx],
                JEWELRY_IMAGES["general"][(image_idx + 1) % len(JEWELRY_IMAGES["general"])]
            ]
            products.append({
                "product_code": f"MT{product_count:03d}",
                "name": f"{style} {design}",
                "details": f"Stunning {style.lower()} {design.lower()} perfect for weddings and festivals.",
                "normal_price": price,
                "offer_price": offer_price,
                "category_id": category_ids["Maangtikkas"],
                "images": product_images,
                "stock_quantity": 30 + (i * 5)
            })
            product_count += 1
    
    # Hipchains (8 products)
    hipchain_designs = ["Gold Hipchain", "Silver Hipchain", "Designer Hipchain", "Antique Hipchain"]
    for i, design in enumerate(hipchain_designs):
        for j, variant in enumerate(["Simple", "Heavy"]):
            price = 399 if variant == "Simple" else 599
            offer_price = price - 50 if i % 2 == 0 else None
            # Assign 2 images from the general jewelry category
            image_idx = (i * 2 + j + 2) % len(JEWELRY_IMAGES["general"])
            product_images = [
                JEWELRY_IMAGES["general"][image_idx],
                JEWELRY_IMAGES["general"][(image_idx + 1) % len(JEWELRY_IMAGES["general"])]
            ]
            products.append({
                "product_code": f"HP{product_count:03d}",
                "name": f"{variant} {design}",
                "details": f"Traditional {variant.lower()} {design.lower()} with beautiful patterns.",
                "normal_price": price,
                "offer_price": offer_price,
                "category_id": category_ids["Hipchains"],
                "images": product_images,
                "stock_quantity": 25 + (i * 3)
            })
            product_count += 1
    
    # Anklets (8 products)
    anklet_designs = ["Silver Anklets", "Gold Anklets", "Designer Anklets", "Bell Anklets"]
    for i, design in enumerate(anklet_designs):
        for j, qty in enumerate(["Single", "Pair"]):
            price = 149 if qty == "Single" else 249
            offer_price = price - 20 if i % 2 == 0 else None
            # Assign 2 images from the general jewelry category
            image_idx = (i * 2 + j + 4) % len(JEWELRY_IMAGES["general"])
            product_images = [
                JEWELRY_IMAGES["general"][image_idx],
                JEWELRY_IMAGES["general"][(image_idx + 1) % len(JEWELRY_IMAGES["general"])]
            ]
            products.append({
                "product_code": f"AN{product_count:03d}",
                "name": f"{design} ({qty})",
                "details": f"Beautiful {design.lower()} ({qty.lower()}) with delicate design.",
                "normal_price": price,
                "offer_price": offer_price,
                "category_id": category_ids["Anklets"],
                "images": product_images,
                "stock_quantity": 60 + (i * 5)
            })
            product_count += 1
    
    # Nose Pins (6 products)
    nosepin_designs = ["Diamond Nose Pin", "Gold Nose Pin", "Stone Nose Pin"]
    for i, design in enumerate(nosepin_designs):
        for j, style in enumerate(["Small", "Medium"]):
            price = 99 if style == "Small" else 149
            offer_price = price - 10 if i % 2 == 0 else None
            # Assign 2 images from the general jewelry category
            image_idx = (i * 2 + j + 6) % len(JEWELRY_IMAGES["general"])
            product_images = [
                JEWELRY_IMAGES["general"][image_idx],
                JEWELRY_IMAGES["general"][(image_idx + 1) % len(JEWELRY_IMAGES["general"])]
            ]
            products.append({
                "product_code": f"NP{product_count:03d}",
                "name": f"{style} {design}",
                "details": f"Sparkling {style.lower()} {design.lower()} for everyday elegance.",
                "normal_price": price,
                "offer_price": offer_price,
                "category_id": category_ids["Nose Pin"],
                "images": product_images,
                "stock_quantity": 150 + (i * 10)
            })
            product_count += 1
    
    # Hair Accessories (6 products)
    hair_designs = ["Hair Pin", "Hair Clip", "Hair Band"]
    for i, design in enumerate(hair_designs):
        for j, style in enumerate(["Simple", "Designer"]):
            price = 99 if style == "Simple" else 149
            # Assign 2 images from the general jewelry category
            image_idx = (i * 2 + j + 8) % len(JEWELRY_IMAGES["general"])
            product_images = [
                JEWELRY_IMAGES["general"][image_idx],
                JEWELRY_IMAGES["general"][(image_idx + 1) % len(JEWELRY_IMAGES["general"])]
            ]
            products.append({
                "product_code": f"HA{product_count:03d}",
                "name": f"{style} {design}",
                "details": f"{style} {design.lower()} to complete your look.",
                "normal_price": price,
                "offer_price": None,
                "category_id": category_ids["Hair Accessories"],
                "images": product_images,
                "stock_quantity": 80 + (i * 10)
            })
            product_count += 1
    
    # Matti (4 products)
    matti_designs = ["Traditional Matti", "Designer Matti"]
    for i, design in enumerate(matti_designs):
        for j, size in enumerate(["Small", "Large"]):
            price = 199 if size == "Small" else 299
            # Assign 2 images from the general jewelry category
            image_idx = (i * 2 + j + 10) % len(JEWELRY_IMAGES["general"])
            product_images = [
                JEWELRY_IMAGES["general"][image_idx],
                JEWELRY_IMAGES["general"][(image_idx + 1) % len(JEWELRY_IMAGES["general"])]
            ]
            products.append({
                "product_code": f"MA{product_count:03d}",
                "name": f"{size} {design}",
                "details": f"{size} {design.lower()} with traditional patterns.",
                "normal_price": price,
                "offer_price": None,
                "category_id": category_ids["Matti"],
                "images": product_images,
                "stock_quantity": 40 + (i * 5)
            })
            product_count += 1
    
    print(f"Total products to create: {len(products)}")
    
    product_ids = []
    created_count = 0
    
    for idx, product in enumerate(products):
        try:
            # Debug: print first product to verify structure
            if idx == 0:
                print(f"First product structure: {json.dumps(product, indent=2)}")
            
            # Prepare form data for the endpoint
            form_data = {
                'product_code': product['product_code'],
                'name': product['name'],
                'details': product.get('details', ''),
                'normal_price': str(product['normal_price']),
                'category_id': str(product['category_id']),
                'stock_quantity': str(product.get('stock_quantity', 50)),
                'is_active': 'true'
            }
            
            # Add offer_price if it exists
            if product.get('offer_price'):
                form_data['offer_price'] = str(product['offer_price'])
            
            # Add images as JSON string if they exist
            if product.get('images'):
                form_data['image_urls'] = json.dumps(product['images'])
            
            response = requests.post(
                f"{BASE_URL}/admin/products",
                headers=headers,
                data=form_data,
                timeout=10
            )
            if response.status_code == 201:
                prod_data = response.json()
                product_ids.append(prod_data["id"])
                created_count += 1
                if created_count % 10 == 0:
                    print(f"✅ Created {created_count}/{len(products)} products...")
            else:
                print(f"❌ Failed: {product['name']} - {response.text[:100]}")
        except Exception as e:
            print(f"❌ Error creating {product['name']}: {str(e)[:100]}")
        
        # Small delay to avoid overwhelming the server
        if idx % 10 == 0:
            time.sleep(0.5)
    
    print(f"✅ Successfully created {created_count} products!")
    return product_ids

# Step 5: Create Combos
def create_combos(token, product_ids):
    if len(product_ids) < 10:
        print("\n⚠️ Not enough products to create combos, skipping...")
        return []
    
    print("\n🎁 Creating combo offers...")
    headers = {"Authorization": f"Bearer {token}"}
    
    combos = [
        {
            "combo_code": "COMBO001",
            "name": "Bridal Complete Set",
            "description": "Complete bridal jewelry set - necklace, earrings, maangtikka, bangles",
            "combo_price": 1199,
            "products": [{"product_id": pid, "quantity": 1} for pid in product_ids[0:4]],
            "is_active": True
        },
        {
            "combo_code": "COMBO002",
            "name": "Daily Wear Combo",
            "description": "Perfect for everyday wear - chain, earrings, ring",
            "combo_price": 249,
            "products": [{"product_id": pid, "quantity": 1} for pid in product_ids[5:8]],
            "is_active": True
        },
        {
            "combo_code": "COMBO003",
            "name": "Traditional Jewelry Set",
            "description": "Temple jewelry collection - haaram, jhumkas, bangles",
            "combo_price": 799,
            "products": [{"product_id": pid, "quantity": 1} for pid in product_ids[10:13]],
            "is_active": True
        },
        {
            "combo_code": "COMBO004",
            "name": "Party Wear Special",
            "description": "Shine at parties - designer necklace, earrings, ring",
            "combo_price": 449,
            "products": [{"product_id": pid, "quantity": 1} for pid in product_ids[15:18]],
            "is_active": True
        },
        {
            "combo_code": "COMBO005",
            "name": "Festive Collection",
            "description": "Celebrate in style - complete jewelry set for festivals",
            "combo_price": 699,
            "products": [{"product_id": pid, "quantity": 1} for pid in product_ids[20:24]],
            "is_active": True
        }
    ]
    
    combo_ids = []
    for combo in combos:
        response = requests.post(
            f"{BASE_URL}/admin/combos",
            headers=headers,
            json=combo
        )
        if response.status_code == 201:
            combo_data = response.json()
            combo_ids.append(combo_data["id"])
            print(f"✅ Created: {combo['name']} (₹{combo['combo_price']})")
        else:
            print(f"❌ Failed: {combo['name']} - {response.text[:100]}")
    
    return combo_ids

# Step 6: Add New Arrivals
def add_new_arrivals(token, product_ids):
    print("\n🆕 Adding new arrivals...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Add 20 products as new arrivals (recent additions)
    new_arrival_count = min(20, len(product_ids))
    for i, product_id in enumerate(product_ids[:new_arrival_count]):
        response = requests.post(
            f"{BASE_URL}/admin/new-arrivals",
            headers=headers,
            json={"product_id": product_id}
        )
        if response.status_code == 201:
            if (i + 1) % 5 == 0:
                print(f"✅ Added {i + 1}/{new_arrival_count} products to new arrivals...")
        else:
            print(f"❌ Failed to add product {product_id}: {response.text[:50]}")
    
    print(f"✅ Successfully added {new_arrival_count} new arrivals!")
    return new_arrival_count

# Step 7: Upload Banner Images
def upload_banners(token):
    print("\n🎨 Uploading banner images...")
    headers = {"Authorization": f"Bearer {token}"}
    
    banners = [
        {
            "title": "New Collection 2024",
            "link_url": "/products?sort=newest",
            "display_order": 1,
            "is_active": True
        },
        {
            "title": "Bridal Jewelry Special",
            "link_url": "/collections/bridal",
            "display_order": 2,
            "is_active": True
        },
        {
            "title": "Flat 20% Off on 99 Store",
            "link_url": "/99-store",
            "display_order": 3,
            "is_active": True
        },
        {
            "title": "Traditional Temple Jewelry",
            "link_url": "/category/haarams",
            "display_order": 4,
            "is_active": True
        },
        {
            "title": "Festive Season Sale",
            "link_url": "/combos",
            "display_order": 5,
            "is_active": True
        }
    ]
    
    banner_ids = []
    for i, banner in enumerate(banners):
        try:
            # Download image from Unsplash
            img_url = BANNER_IMAGES[i]
            img_response = requests.get(img_url, timeout=15)
            
            if img_response.status_code == 200:
                # Create multipart form data
                files = {
                    'image': ('banner.jpg', BytesIO(img_response.content), 'image/jpeg')
                }
                data = {
                    'title': banner['title'],
                    'link_url': banner['link_url'],
                    'display_order': banner['display_order'],
                    'is_active': banner['is_active']
                }
                
                response = requests.post(
                    f"{BASE_URL}/admin/banners/upload",
                    headers=headers,
                    files=files,
                    data=data
                )
                
                if response.status_code == 201:
                    banner_data = response.json()
                    banner_ids.append(banner_data["id"])
                    print(f"✅ Uploaded banner: {banner['title']}")
                else:
                    print(f"❌ Failed to upload banner: {banner['title']} - {response.text[:100]}")
            else:
                print(f"❌ Failed to download image for: {banner['title']}")
            
            # Small delay between uploads
            time.sleep(0.5)
            
        except Exception as e:
            print(f"❌ Error uploading banner {banner['title']}: {str(e)[:100]}")
    
    print(f"✅ Successfully uploaded {len(banner_ids)} banners!")
    return banner_ids

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
        
        # Create products (100+)
        product_ids = create_products(token, category_ids)
        
        # Create combos
        if len(product_ids) >= 10:
            combo_ids = create_combos(token, product_ids)
        else:
            combo_ids = []
        
        # Add new arrivals
        if len(product_ids) >= 3:
            new_arrival_count = add_new_arrivals(token, product_ids)
        else:
            new_arrival_count = 0
        
        # Upload banners
        banner_ids = upload_banners(token)
        
        print("\n" + "=" * 60)
        print("✅ Sample data setup completed successfully!")
        print("\n📊 Summary:")
        print(f"   - Categories: {len(category_ids)}")
        print(f"   - Products: {len(product_ids)}")
        print(f"   - Combos: {len(combo_ids)}")
        print(f"   - New Arrivals: {new_arrival_count}")
        print(f"   - Banners: {len(banner_ids)}")
        print("\n🔗 Access the API:")
        print(f"   - Documentation: {BASE_URL}/docs")
        print(f"   - Public Products: {BASE_URL}/products")
        print(f"   - 99 Store: {BASE_URL}/99-store")
        print(f"   - 199 Store: {BASE_URL}/199-store")
        print(f"   - Banners: {BASE_URL}/banners")
        print("\n🔐 Admin Credentials:")
        print("   - Username: admin")
        print("   - Password: admin123")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        print("\nMake sure the API server is running at http://localhost:8000")

if __name__ == "__main__":
    main()
