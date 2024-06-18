import pandas as pd
import json
from dataload import transform_user_data, transform_receipt_data, transform_brand_data

print("entered dq checks")
# Load users data
with open('users.json', 'r') as file:
    users_data = [transform_user_data(json.loads(line)) for line in file]
users_df = pd.DataFrame(users_data)

print("user data count",len(users_df))

# Load receipts data
with open('receipts.json', 'r') as file:
    receipts_data = [transform_receipt_data(json.loads(line)) for line in file]
receipts_df = pd.DataFrame(receipts_data)

print("receipts count",len(receipts_df))

# Load brands data
with open('brands.json', 'r') as file:
    brands_data = [transform_brand_data(json.loads(line)) for line in file]
brands_df = pd.DataFrame(brands_data)

print("brands count",len(brands_df))

expanded_data = receipts_df.explode('items')

# Normalize the JSON objects to create a new DataFrame
receipt_items_df = pd.json_normalize(expanded_data['items'])

print("items df count", len(receipt_items_df))

def check_duplicates(df, columns):
    # Check if columns is a single string, if so, convert to list
    if isinstance(columns, str):
        columns = [columns]
    # Now columns is always a list, whether it was initially or converted
    duplicates = df[df.duplicated(subset=columns, keep=False)]
    return duplicates


# Check for duplicates in user_id
duplicates_users = check_duplicates(users_df, 'user_id')
print("Duplicate users count", duplicates_users['user_id'].count())

# Check for duplicates in receipt_id
duplicates_receipts = check_duplicates(receipts_df, 'receipt_id')

print("Duplicate Receipts count", duplicates_receipts['receipt_id'].count())

# Check for duplicates in item_id
ri_column = ['receipt_id','barcode']
duplicates_receipt_items = check_duplicates(receipt_items_df, ri_column)

print("Duplicate Receipt items count", duplicates_receipt_items[ri_column].count())

# Check for duplicates in brand_id
duplicates_brands = check_duplicates(brands_df, 'brand_id')

print("Duplicate brands count", duplicates_brands['brand_id'].count())

def check_missing_values(df):
    missing_values = df.isnull().sum()
    return missing_values

# Check for missing values in users
missing_values_users = check_missing_values(users_df)
print(f"Missing values in users:\n{missing_values_users}")

print("Count of missing values in users",len(missing_values_users))

# Check for missing values in receipts
missing_values_receipts = check_missing_values(receipts_df)
print(f"Missing values in receipts:\n{missing_values_receipts}")

print("Count of missing values in receipts",len(missing_values_receipts))

# Check for missing values in receipt items
missing_values_receipt_items = check_missing_values(receipt_items_df)
print(f"Missing values in receipt items:\n{missing_values_receipt_items}")

print("Count of missing values in receipt items",len(missing_values_receipt_items))

# Check for missing values in brands
missing_values_brands = check_missing_values(brands_df)
print(f"Missing values in brands:\n{missing_values_brands}")

print("Count of missing values in brands",len(missing_values_brands))

def check_data_types(df):
    data_types = df.dtypes
    return data_types

# Check data types in users
data_types_users = check_data_types(users_df)
print(f"Data types in users:\n{data_types_users}")

# Check data types in receipts
data_types_receipts = check_data_types(receipts_df)
print(f"Data types in receipts:\n{data_types_receipts}")

# Check data types in receipt items
data_types_receipt_items = check_data_types(receipt_items_df)
print(f"Data types in receipt items:\n{data_types_receipt_items}")

# Check data types in brands
data_types_brands = check_data_types(brands_df)
print(f"Data types in brands:\n{data_types_brands}")

def check_referential_integrity(parent_df, child_df, parent_key, child_key):
    invalid_references = ~child_df[child_key].isin(parent_df[parent_key])
    return child_df[invalid_references]

# Check referential integrity for user_id in receipts
invalid_user_references = check_referential_integrity(users_df, receipts_df, 'user_id', 'user_id')
print(f"Invalid user references in receipts:\n{invalid_user_references}")

# Check referential integrity for receipt_id in receipt items
invalid_receipt_references = check_referential_integrity(receipts_df, receipt_items_df, 'receipt_id', 'receipt_id')
print(f"Invalid receipt references in receipt items:\n{invalid_receipt_references}")
