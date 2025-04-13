from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
from datetime import datetime
import time
import csv
from tqdm import tqdm
import os

def print_nested_structure(data, indent=0, max_depth=3, current_depth=0):
    if current_depth >= max_depth:
        return
    
    prefix = "  " * indent
    if isinstance(data, dict):
        for key, value in data.items():
            print(f"{prefix}Key: {key}")
            if isinstance(value, (dict, list)):
                print_nested_structure(value, indent + 1, max_depth, current_depth + 1)
            else:
                print(f"{prefix}Value: {value} ({type(value)})")
    elif isinstance(data, list):
        print(f"{prefix}List length: {len(data)}")
        if data:
            print_nested_structure(data[0], indent + 1, max_depth, current_depth + 1)

def extract_product_data(snippet, category, location, timestamp):
    """Extract product data from a product container snippet"""
    if not isinstance(snippet, dict):
        return None
    
    # Save snippet structure
    # snippet_filename = f"blinkit_snippet_structure_{category['l1_category_id']}_{category['l2_category_id']}_{location['latitude']}_{location['longitude']}_{timestamp}.json"
    # with open(snippet_filename, "w", encoding="utf-8") as file:
    #     json.dump({
    #         "widget_type": snippet.get('widget_type'),
    #         "snippet_keys": list(snippet.keys()),
    #         "data_keys": list(snippet.get('data', {}).keys()) if snippet.get('data') else []
    #     }, file, indent=2, ensure_ascii=False)
    
    # Check if this is a product container or product card
    widget_type = snippet.get('widget_type')
    if widget_type not in ['product_container', 'product_card_snippet_type_2']:
        return None
    
    # Get the data section
    data = snippet.get('data', {})
    if not data:
        return None
    
    # For product_card_snippet_type_2, the product data is directly in the data section
    if widget_type == 'product_card_snippet_type_2':
        product = data
    else:
        # For product_container, get items
        items = data.get('items', [])
        if not items:
            # Try to find items in nested structure
            for key, value in data.items():
                if isinstance(value, list) and value and isinstance(value[0], dict):
                    items = value
                    break
        
        if not items:
            return None
        
        # Extract product data from the first item
        item = items[0]
        
        # Get product details
        product = item.get('product', {})
        if not product:
            product = item  # If no nested product, use item directly
    
    # Save product data structure
    # product_filename = f"blinkit_product_data_{category['l1_category_id']}_{category['l2_category_id']}_{location['latitude']}_{location['longitude']}_{timestamp}.json"
    # with open(product_filename, "w", encoding="utf-8") as file:
    #     json.dump({
    #         "product_keys": list(product.keys()),
    #         "sample_values": {k: str(v)[:100] for k, v in product.items()}
    #     }, file, indent=2, ensure_ascii=False)
    
    # Extract text from nested JSON structures
    def extract_text_from_json(value):
        if isinstance(value, dict):
            return value.get('text', '')
        return str(value)
    
    # Extract price from nested JSON structure
    def extract_price(value):
        if isinstance(value, dict):
            price_text = value.get('text', '')
            # Remove currency symbol and convert to float
            return float(price_text.replace('₹', '').strip())
        return 0.0
    
    # Get merchant_id (store_id) and product_id (variant_id)
    merchant_id = product.get('merchant_id', '')
    product_id = product.get('product_id', '')
    
    # Get brand_id or set to NA if not found
    brand_id = product.get('brand_id', 'NA')
    
    # Check product availability
    product_state = product.get('product_state', '')
    is_sold_out = product.get('is_sold_out', False)
    in_stock = not (product_state == 'out_of_stock' or is_sold_out)
    
    # Check if product is sponsored
    is_sponsored = True  # Default to True
    atc_actions = product.get('atc_actions_v2', {})
    if isinstance(atc_actions, dict):
        count_map = atc_actions.get('count_map', {})
        if isinstance(count_map, dict):
            # Get the array under key '0'
            actions_array = count_map.get('0', [])
            if isinstance(actions_array, list):
                # Find the fetch_api action
                for action in actions_array:
                    if isinstance(action, dict) and action.get('type') == 'fetch_api':
                        fetch_api = action.get('fetch_api', {})
                        if isinstance(fetch_api, dict):
                            extra_params = fetch_api.get('extra_params', {})
                            if isinstance(extra_params, dict):
                                recommendation_type = extra_params.get('recommendation_type', '')
                                if recommendation_type == 'DEFAULT':
                                    is_sponsored = False
                                break
    
    return {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'l1_category': extract_text_from_json(product.get('l1_category', '')),
        'l1_category_id': product.get('l1_category_id', ''),
        'l2_category': extract_text_from_json(product.get('l2_category', '')),
        'l2_category_id': product.get('l2_category_id', ''),
        'store_id': merchant_id,  # Using merchant_id as store_id
        'variant_id': product_id,  # Using product_id as variant_id
        'variant_name': extract_text_from_json(product.get('name', '')),
        'group_id': product.get('group_id', ''),
        'selling_price': extract_price(product.get('normal_price', '')),
        'mrp': extract_price(product.get('mrp', '')),
        'in_stock': in_stock, 
        'inventory': product.get('inventory', 0),
        'is_sponsored': is_sponsored,  
        'image_url': product.get('image', ''),
        'brand_id': brand_id,  
        'brand': extract_text_from_json(product.get('brand_name', ''))
    }

def read_categories():
    """Read categories from CSV file"""
    categories = []
    with open('blinkit_categories.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            categories.append({
                'l1_category': row['l1_category'],
                'l1_category_id': row['l1_category_id'],
                'l2_category': row['l2_category'],
                'l2_category_id': row['l2_category_id']
            })
    return categories

def read_locations():
    """Read locations from CSV file"""
    locations = []
    with open('blinkit_locations.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            locations.append({
                'latitude': row['latitude'],
                'longitude': row['longitude']
            })
    return locations

def fetch_blinkit_data():
    # Initialize timestamp at the start
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create output directory if it doesn't exist
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Read categories and locations
    categories = read_categories()
    locations = read_locations()
    
    print(f"Found {len(categories)} categories and {len(locations)} locations")
    total_combinations = len(categories) * len(locations)
    print(f"Total combinations to process: {total_combinations}")
    
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Run in headless mode
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    # Initialize the Chrome WebDriver
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # First visit the main page
        print("Initializing browser session...")
        driver.get("https://blinkit.com/")
        
        # Wait for the page to load
        time.sleep(5)  # Give Cloudflare time to process
        
        all_products = []
        processed_count = 0
        
        # Create progress bar
        pbar = tqdm(total=total_combinations, desc="Processing combinations")
        
        # Iterate through all combinations of categories and locations
        for category in categories:
            for location in locations:
                # Update progress bar description
                pbar.set_description(f"Processing {category['l1_category']} > {category['l2_category']} at {location['latitude']}, {location['longitude']}")
                
                # Now make the API request using JavaScript
                api_url = f"https://blinkit.com/v1/layout/listing_widgets?l0_cat={category['l1_category_id']}&l1_cat={category['l2_category_id']}"
                
                # Execute JavaScript to make the API request
                script = """
                return fetch(arguments[0], {
                    method: 'POST',
                    headers: {
                        'Accept': 'application/json, text/plain, */*',
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Connection': 'keep-alive',
                        'Content-Type': 'application/json',
                        'Origin': 'https://blinkit.com',
                        'Referer': 'https://blinkit.com/',
                        'lat': arguments[1],
                        'lon': arguments[2]
                    }
                }).then(response => response.json());
                """
                
                # Execute the script and get the response
                response = driver.execute_script(script, api_url, location['latitude'], location['longitude'])
                
                # Process the response
                if response and isinstance(response, dict) and 'response' in response:
                    response_data = response['response']
                    
                    if 'snippets' in response_data:
                        print(f"\nFound {len(response_data['snippets'])} snippets")
                        for snippet in response_data['snippets']:
                            product_data = extract_product_data(snippet, category, location, timestamp)
                            if product_data:
                                # Add category and location information
                                product_data.update({
                                    'l1_category': category['l1_category'],
                                    'l1_category_id': category['l1_category_id'],
                                    'l2_category': category['l2_category'],
                                    'l2_category_id': category['l2_category_id'],
                                    'latitude': location['latitude'],
                                    'longitude': location['longitude']
                                })
                                all_products.append(product_data)
                                # print(f"\nFound product: {product_data['variant_name']}")
                    else:
                        print(f"\nNo snippets found in response for {category['l1_category']} > {category['l2_category']}")
                else:
                    print(f"\nInvalid response format for {category['l1_category']} > {category['l2_category']}")
                
                # Update progress
                processed_count += 1
                pbar.update(1)
                
                # Add a small delay between requests
                time.sleep(2)
        
        pbar.close()
        
        if all_products:
            # Save to CSV in output directory
            csv_filename = os.path.join(output_dir, f"blinkit_products_{timestamp}.csv")
            
            # Define CSV headers based on the schema
            headers = [
                'date',
                'l1_category',
                'l1_category_id',
                'l2_category',
                'l2_category_id',
                'store_id',
                'variant_id',
                'variant_name',
                'group_id',
                'selling_price',
                'mrp',
                'in_stock',
                'inventory',
                'is_sponsored',
                'image_url',
                'brand_id',
                'brand',
                'latitude',
                'longitude'
            ]
            
            # Open CSV file and write data
            with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=headers)
                writer.writeheader()
                writer.writerows(all_products)
            
            print(f"\nSaved {len(all_products)} products to {csv_filename}")
        else:
            print("\nNo products found in any response")
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        error_data = {
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "url": "https://blinkit.com/v1/layout/listing_widgets"
        }
        # Save error log to output directory
        error_filename = os.path.join(output_dir, f"exception_{timestamp}.json")
        with open(error_filename, "w", encoding="utf-8") as file:
            json.dump(error_data, file, indent=2, ensure_ascii=False)
        print(f"\nError log saved to {error_filename}")
    
    finally:
        # Clean up
        driver.quit()

if __name__ == "__main__":
    fetch_blinkit_data()
