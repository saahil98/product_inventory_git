import pandas as pd
import psycopg2
import os
from sqlalchemy import create_engine,text
def create_product_table():
    """
    Creates the product_details table if it doesn't exist and loads initial data from Excel
    """
    try:
        
        conn = psycopg2.connect(dbname="postgres",
            user="postgres",
            password="54321",
            host="127.0.0.1",
            port="5432")
        cursor = conn.cursor()

        # Create table with common product fields
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS product_details (
                TransId SERIAL PRIMARY KEY,
                BillNumber TEXT NOT NULL,
                ProductId TEXT,
                ProductModelNumber TEXT,
                ProductPrice INTEGER,
                QtyPurchased INTEGER,
                BillStatus TEXT,
                TotalAmount INTEGER
            )
        ''')
        conn.commit()

        # Check if table is empty
        cursor.execute("SELECT COUNT(*) FROM product_details")
        count = cursor.fetchone()[0]
        print(count)
        # Load data from Excel only if table is empty
        if count == 0:
            try:
                df = pd.read_excel(r"C:\Users\saahil.ali\OneDrive - Accenture\KT Documents\crewAI\product_inventory_git\Product_details.xlsx", sheet_name="Sheet1")
                print(df)
                # Create SQLAlchemy engine for pandas to_sql
                engine = create_engine('postgresql://postgres:54321@127.0.0.1:5432/postgres')
                
                # Use the engine to write the dataframe to PostgreSQL
                df.to_sql(
                    name='product_details', 
                    con=engine, 
                    if_exists='append',
                    index=False
                )
                return "Table created and data loaded successfully"
            except Exception as e:
                return f"Error loading Excel data: {str(e)}"
        else:
            return "Table already exists and contains data"

    except psycopg2.Error as e:
        return f"Database error: {str(e)}"
    # finally:
    #     # conn.close()

# Modified create_db function to use the new structure
def create_db():
    result = create_product_table()
    print(result)
# create_db()
# f'postgresql://{user_id}:{passw_str}@{server_name}:{port}/{db_name}'
connection_string = "postgresql:postgres:54321//@localhost:5432/postgres"
# {"host":"127.0.0.1", "port":5432, "database":"postgres", "user": "postgres", "password": "54321", "driver":"","schema":"Structured_KB"}



def get_db_engine():
    """Create and return database engine"""
    return create_engine('postgresql://postgres:54321@127.0.0.1:5432/postgres')

def insert_data(table_name="product_details", data_dict=None):
    """
    Insert data into specified table
    
    Args:
        table_name (str): Name of the table
        data_dict (dict): Dictionary containing column:value pairs to insert
    
    Returns:
        str: Success or error message
    """
    try:
        engine = get_db_engine()
        
        with engine.connect() as conn:
            # Extract columns and values
            # Remove TransId if it exists in data_dict since it's SERIAL
            if 'TransId' in data_dict:
                del data_dict['TransId']

            columns = list(data_dict.keys())
            values = list(data_dict.values())
            
            # Create placeholders for SQL query
            placeholders = ', '.join(f':{key}' for key in columns)
            columns_str = ', '.join(columns)
            
            # Build INSERT query
            query = f"""
                INSERT INTO {table_name} 
                ({columns_str}) 
                VALUES ({placeholders})
                RETURNING TransId
            """
            
            # Execute query with parameters
            result = conn.execute(text(query), data_dict)
            conn.commit()
            
            # Get the ID of inserted record
            inserted_id = result.scalar()
            
            return f"Data inserted successfully with ID: {inserted_id}"
            
    except Exception as e:
        return f"Error inserting data: {str(e)}"

def bulk_insert_data(table_name="product_details", data_list=None):
    """
    Insert multiple records at once
    
    Args:
        table_name (str): Name of the table
        data_list (list): List of dictionaries containing data to insert
    
    Returns:
        str: Success or error message
    """
    try:
        engine = get_db_engine()
        
        # Convert list of dictionaries to DataFrame
        df = pd.DataFrame(data_list)
        
        # Insert data using pandas to_sql
        df.to_sql(
            name=table_name,
            con=engine,
            if_exists='append',
            index=False
        )
        
        return f"Successfully inserted {len(data_list)} records"
        
    except Exception as e:
        return f"Error in bulk insert: {str(e)}"

def update_data(table_name="product_details", update_dict=None, condition_dict=None):
    """
    Update records in specified table
    
    Args:
        table_name (str): Name of the table
        update_dict (dict): Dictionary containing column:value pairs to update
        condition_dict (dict): Dictionary containing column:value pairs for WHERE clause
    
    Returns:
        str: Success or error message with number of rows updated
    """
    try:
        engine = get_db_engine()
        
        with engine.connect() as conn:
            # Prepare SET clause
            set_clause = ', '.join(f"{key} = :{key}" for key in update_dict.keys())
            
            # Prepare WHERE clause
            where_clause = ' AND '.join(f"{key} = :condition_{key}" 
                                      for key in condition_dict.keys())
            
            # Build UPDATE query
            query = f"""
                UPDATE {table_name} 
                SET {set_clause} 
                WHERE {where_clause}
            """
            
            # Combine parameters from both dictionaries
            params = {**update_dict}
            params.update({f"condition_{k}": v for k, v in condition_dict.items()})
            
            # Execute query
            result = conn.execute(text(query), params)
            conn.commit()
            
            return f"Successfully updated {result.rowcount} record(s)"
            
    except Exception as e:
        return f"Error updating data: {str(e)}"

def bulk_update_data(table_name="product_details", update_data=None):
    """
    Update multiple records with different values
    
    Args:
        table_name (str): Name of the table
        update_data (list): List of dictionaries containing update data and conditions
    
    Returns:
        str: Success or error message
    """
    try:
        engine = get_db_engine()
        updated_count = 0
        
        with engine.connect() as conn:
            for item in update_data:
                update_dict = item.get('update', {})
                condition_dict = item.get('condition', {})
                
                # Prepare SET and WHERE clauses
                set_clause = ', '.join(f"{key} = :{key}" 
                                     for key in update_dict.keys())
                where_clause = ' AND '.join(f"{key} = :condition_{key}" 
                                          for key in condition_dict.keys())
                
                # Build and execute query
                query = f"""
                    UPDATE {table_name} 
                    SET {set_clause} 
                    WHERE {where_clause}
                """
                
                params = {**update_dict}
                params.update({f"condition_{k}": v for k, v in condition_dict.items()})
                
                result = conn.execute(text(query), params)
                updated_count += result.rowcount
            
            conn.commit()
            return f"Successfully updated {updated_count} record(s)"
            
    except Exception as e:
        return f"Error in bulk update: {str(e)}"
    

def fetch_data(table_name="product_details", conditions=None, columns=None, limit=None):
    """
    Fetch data from the specified table with optional filtering
    
    Args:
        table_name (str): Name of the table to query
        conditions (dict): Dictionary of conditions for WHERE clause
        columns (list): List of columns to fetch. If None, fetches all columns
        limit (int): Maximum number of records to return
    
    Returns:
        list: List of dictionaries containing the fetched records
    """
    try:
        # Create database engine
        engine = create_engine('postgresql://postgres:54321@127.0.0.1:5432/postgres')
        
        with engine.connect() as conn:
            # Build the SELECT part of query
            select_columns = "*" if not columns else ", ".join(columns)
            query = f"SELECT {select_columns} FROM {table_name}"
            
            # Add WHERE clause if conditions exist
            params = {}
            if conditions:
                where_clauses = []
                for key, value in conditions.items():
                    where_clauses.append(f"{key} = :{key}")
                    params[key] = value
                query += " WHERE " + " AND ".join(where_clauses)
            
            # Add LIMIT clause if specified
            if limit:
                query += f" LIMIT {limit}"
            
            # Execute query with parameters
            result = conn.execute(text(query), params)
            
            # Fetch all rows and convert to list of dictionaries
            rows = result.fetchall()
            columns = result.keys()
            
            return [dict(zip(columns, row)) for row in rows]

    except Exception as e:
        print(f"Error fetching data: {e}")
        return []
# print(fetch_data())
# data_dict = {"BillNumber":123, "ProductId":"Refr1",\
#              "ProductModelNumber":"Refrig1","ProductPrice":10000,\
#                 "QtyPurchased":2, "BillStatus":"Approved","TotalAmount":20000}

# print(insert_data("product_details", data_dict))
# print(update_data("product_details", {"BillStatus":"Rejected"}, {"TransId":1}))

# Single Insert
new_record = {
    "BillNumber": "B128",
    "ProductId": "P792",
    "ProductPrice": 10000,
    "QtyPurchased": 1,
    "BillStatus": "Pending",
    "TotalAmount": 10000
}
# result = insert_data(data_dict=new_record)
# print(result)

# Single Update
update_values = {
    "BillStatus": "Approved",
    "TotalAmount": 21000,
    "ProductModelNumber": "B138"
}
conditions = {
    "BillNumber": "B128"
}
# result = update_data(update_dict=update_values, condition_dict=conditions)
# print(result)


if __name__ == '__main__':
    create_db()
    