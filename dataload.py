import json
import psycopg2
from datetime import datetime

def transform_user_data(user):
    user_id = user['_id']['$oid'] if user['_id'] and '$oid' in user['_id'] else None
    active = user.get('active', False)
    created_date = datetime.fromtimestamp(user['createdDate']['$date'] / 1000.0) if 'createdDate' in user and '$date' in user['createdDate'] else None
    last_login = datetime.fromtimestamp(user['lastLogin']['$date'] / 1000.0) if 'lastLogin' in user and '$date' in user['lastLogin'] else None
    role = user.get('role', 'unknown')
    sign_up_source = user.get('signUpSource', None)
    state = user.get('state', None)
    userIdset = set(user_id)
    #print(len(userIdset))
    return {
        'user_id': user_id,
        'active': active,
        'created_date': created_date,
        'last_login': last_login,
        'role': role,
        'sign_up_source': sign_up_source,
        'state': state
    }

def transform_receipt_data(receipt):
    receipt_id = receipt['_id']['$oid'] if receipt['_id'] and '$oid' in receipt['_id'] else None
    user_id = receipt.get('userId', None)
    create_date = datetime.fromtimestamp(receipt['createDate']['$date'] / 1000.0) if 'createDate' in receipt and '$date' in receipt['createDate'] else None
    date_scanned = datetime.fromtimestamp(receipt['dateScanned']['$date'] / 1000.0) if 'dateScanned' in receipt and '$date' in receipt['dateScanned'] else None
    finished_date = datetime.fromtimestamp(receipt['finishedDate']['$date'] / 1000.0) if 'finishedDate' in receipt and '$date' in receipt['finishedDate'] else None
    modify_date = datetime.fromtimestamp(receipt['modifyDate']['$date'] / 1000.0) if 'modifyDate' in receipt and '$date' in receipt['modifyDate'] else None
    points_awarded_date = datetime.fromtimestamp(receipt['pointsAwardedDate']['$date'] / 1000.0) if 'pointsAwardedDate' in receipt and '$date' in receipt['pointsAwardedDate'] else None
    purchase_date = datetime.fromtimestamp(receipt['purchaseDate']['$date'] / 1000.0) if 'purchaseDate' in receipt and '$date' in receipt['purchaseDate'] else None
    points_earned = float(receipt['pointsEarned']) if 'pointsEarned' in receipt else 0.0
    total_spent = float(receipt['totalSpent']) if 'totalSpent' in receipt else 0.0
    bonus_points_earned = receipt.get('bonusPointsEarned', 0)
    bonus_points_earned_reason = receipt.get('bonusPointsEarnedReason', None)
    purchased_item_count = receipt.get('purchasedItemCount', 0)
    rewards_receipt_status = receipt.get('rewardsReceiptStatus', None)
    
    items = receipt.pop('rewardsReceiptItemList', [])
    receipt_items = []
    for item in items:
        receipt_items.append(transform_receipt_item(item, receipt_id))
    
    receipt['items'] = receipt_items
    
    return {
        'receipt_id': receipt_id,
        'user_id': user_id,
        'create_date': create_date,
        'date_scanned': date_scanned,
        'finished_date': finished_date,
        'modify_date': modify_date,
        'points_awarded_date': points_awarded_date,
        'purchase_date': purchase_date,
        'points_earned': points_earned,
        'total_spent': total_spent,
        'bonus_points_earned': bonus_points_earned,
        'bonus_points_earned_reason': bonus_points_earned_reason,
        'purchased_item_count': purchased_item_count,
        'rewards_receipt_status': rewards_receipt_status,
        'items': receipt_items
    }

def transform_receipt_item(item, receipt_id):
    return {
        'receipt_id': receipt_id,
        'barcode': item.get('barcode', 'unknown'),
        'description': item.get('description', None),
        'final_price': float(item['finalPrice']) if 'finalPrice' in item else 0.0,
        'item_price': float(item['itemPrice']) if 'itemPrice' in item else 0.0,
        'needs_fetch_review': item.get('needsFetchReview', False),
        'needs_fetch_review_reason': item.get('needsFetchReviewReason', None),
        'partner_item_id': item.get('partnerItemId', None),
        'points_not_awarded_reason': item.get('pointsNotAwardedReason', None),
        'points_payer_id': item.get('pointsPayerId', None),
        'prevent_target_gap_points': item.get('preventTargetGapPoints', False),
        'quantity_purchased': item.get('quantityPurchased', 0),
        'rewards_group': item.get('rewardsGroup', None),
        'rewards_product_partner_id': item.get('rewardsProductPartnerId', None),
        'user_flagged_barcode': item.get('userFlaggedBarcode', None),
        'user_flagged_description': item.get('userFlaggedDescription', None),
        'user_flagged_new_item': item.get('userFlaggedNewItem', False),
        'user_flagged_price': float(item['userFlaggedPrice']) if 'userFlaggedPrice' in item else None,
        'user_flagged_quantity': item.get('userFlaggedQuantity', None)
    }

def load_receipt_items(data, conn):
    cursor = conn.cursor()

    print("Loading receipt items ....")
    print("data", data)
    
    all_items = []
    for line in data:
        items = line.pop('items', [])  # Default to an empty list if 'items' key is not found
        all_items.extend(items)  # Collect all items from each dictionary
    
    for item in all_items:
        columns = item.keys()
        columns_str = ', '.join(columns)
        values_str = ', '.join([f"%({col})s" for col in columns])

        query = f"""
        WITH receipt_exists AS (
            SELECT 1 FROM receipts WHERE receipt_id = %(receipt_id)s
        )
        INSERT INTO receipt_items ({columns_str}) 
        SELECT {values_str} 
        FROM receipt_exists 
        ON CONFLICT DO NOTHING
        """

        cursor.execute(query, item)
    
    conn.commit()
    cursor.close()


def transform_brand_data(brand):
    brand_id = brand['_id']['$oid'] if brand['_id'] and '$oid' in brand['_id'] else None
    barcode = brand.get('barcode', 'unknown')
    brand_code = brand.get('brandCode', 'unknown')
    category = brand.get('category', 'unknown')
    category_code = brand.get('categoryCode', 'unknown')
    cpg = brand['cpg']['$id']['$oid'] if 'cpg' in brand and '$id' in brand['cpg'] else None
    top_brand = brand.get('topBrand', False)
    name = brand.get('name', 'unknown')
    
    return {
        'brand_id': brand_id,
        'barcode': barcode,
        'brand_code': brand_code,
        'category': category,
        'category_code': category_code,
        'cpg': cpg,
        'top_brand': top_brand,
        'name': name
    }

def load_json_to_postgres(file_path, table_name, conn, transform_function=None):
    with open(file_path, 'r') as file:
        cursor = conn.cursor()
        
        for line in file:
            data = json.loads(line.strip())

            if transform_function:
                data = transform_function(data)
            #print("data", data) 


            if table_name == 'users':
                print("Loading Users ....")
                columns = data.keys()
                columns_str = ', '.join(columns)
                values_str = ', '.join([f"%({col})s" for col in columns])
                query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({values_str}) ON CONFLICT DO NOTHING"
            
            if table_name == 'receipts':
                print("Loading receipts ....")
                if 'items' in data:
                    data.pop('items')

                columns = data.keys()
                columns_str = ', '.join(columns)
                values_str = ', '.join([f"%({col})s" for col in columns])
                query = f"""
                WITH user_exists AS (
                    SELECT 1 FROM users WHERE user_id = %(user_id)s
                )
                INSERT INTO {table_name} ({columns_str}) 
                SELECT {values_str} 
                FROM user_exists 
                ON CONFLICT DO NOTHING
                """
            
            if table_name == 'brands':  
                print("Loading Brands ....")
                columns = data.keys()
                columns_str = ', '.join(columns)
                values_str = ', '.join([f"%({col})s" for col in columns])
                query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({values_str})"      

            
            

            #print("columns_str", columns_str)
            #print("values_str", values_str)
            
            cursor.execute(query, data)
        
        conn.commit()
        cursor.close()

def main():
    conn = psycopg2.connect(
        dbname='receipts_database',
        user='abhishekannabathula',
        password='postgres123',  # Replace with your actual password
        host='localhost',  # Replace with your actual host
        port='5432'   
    )

    load_json_to_postgres('users.json', 'users', conn, transform_function=transform_user_data)

    with open('receipts.json', 'r') as file:
        receipts_data = [transform_receipt_data(json.loads(line.strip())) for line in file]

    load_json_to_postgres('receipts.json', 'receipts', conn, transform_function=transform_receipt_data)
    load_json_to_postgres('brands.json', 'brands', conn, transform_function=transform_brand_data)
    load_receipt_items(receipts_data, conn)
    conn.close()

if __name__ == '__main__':
    main()
