from crewai.tools import BaseTool
from google import genai
from googleapiclient.discovery import build
from sqlalchemy import create_engine, text
import re
import json

import os, requests
import PIL.Image
from dotenv import load_dotenv
import uuid

dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../.env'))
load_dotenv(dotenv_path=dotenv_path)
# print(dotenv_path)

api_key = os.getenv("GOOGLEKEY")
cse_id = os.getenv("CSEID")

class SearchWebTool(BaseTool):
    name: str = "Internet Search"
    description: str = "Useful for Internet search-based queries. Use this to find price of a product based on a model, brand, etc."

    def _run(self, query: str) -> str:
        try:
            service = build("customsearch", "v1", developerKey=api_key)
            result = service.cse().list(q=query, cx=cse_id).execute()
            return result
        except Exception as e:
            raise Exception(f"An error occurred: {e}")

class ShoppingAPITool(BaseTool):
    name: str = "Shopping API Tool"
    description: str = "A tool for making API calls to get details of product list, shopping cart or billing amount"

    def _run(self, endpoint: str, method: str = "GET", body: dict = None): 
        """Execute the API call and return results"""
        base_url = "http://127.0.0.1:8000/"
        api_endpoint = base_url + endpoint
        try:
            response = requests.request(method, api_endpoint, json=body)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return f"Error making API call: {str(e)}"

class SearchImageTool(BaseTool):
    name: str = "Image Search"
    description: str = "Useful for search context based on the Iamge given as input"

    def _run(self, prompt: str, image_path: str):
        # Implementation goes here
        try:
            client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
            image = PIL.Image.open(image_path)
            response = client.models.generate_content(
                        model="gemini-2.0-flash",
                        contents=[prompt, image])
            return response.text
        except Exception as e:
            raise Exception(f"An error occurred: {e}")


class JsonReadTool(BaseTool):
    name:str = "Json Read Tool"
    description:str = "Reads the json file and returns the content"
    def _run(self, file_path: str) -> str:
        try:
            # file_path = r"C:\Users\priyanka.b.chila\Documents\GenAIML\Downloads\product_details_data.json"
            with open(file_path, 'r') as file:
                data = file.read()
                data = json.loads(data)
                bill_number= str(uuid.uuid4())
                for item in data['items']:
                    if 'billnumber' not in item:
                        item['billnumber'] = bill_number
                    if 'totalamount' not in item:
                        item['totalamount'] = int(item['productprice']) * int(item['productquantity'])
                return data['items']
        except Exception as e:
            return f"Error reading file: {str(e)}"

class GetSchemaTool(BaseTool):
    name:str = "Get Schema"
    description:str = "Gets the database schema for a specified table"
        

    def _run(self, table_name: str, db_uri:str) -> str:
        try:
            db_uri = 'postgresql://postgres:54321@127.0.0.1:5432/postgres'
            engine = create_engine(db_uri)
            with engine.connect() as conn:
                schema_query = """
                    SELECT column_name, data_type, character_maximum_length, is_nullable
                    FROM information_schema.columns
                    WHERE table_name = :table_name
                    ORDER BY ordinal_position;
                """
                result = conn.execute(text(schema_query), {"table_name": table_name})
                print(result, "schema result")
                schema = result.fetchall()
                
                schema_info = []
                for col in schema:
                    col_info = f"{col[0]} {col[1]}"
                    if col[2]:
                        col_info += f"({col[2]})"
                    col_info += f" {'NULL' if col[3] == 'YES' else 'NOT NULL'}"
                    schema_info.append(col_info)
                
                return "\n".join(schema_info)
        except Exception as e:
            return f"Error getting schema: {str(e)}"


class DatabaseTool(BaseTool):
    name: str = "Database Tool"
    description: str = "Executes SQL queries on the product_details table with input validation"
    # args_schema: Type[BaseTool] = DatabaseToolInput

    def _sanitize_query(self, query: str) -> str:
        """Basic query sanitization"""
        # Remove any multiple semicolons
        query = re.sub(r';+', ';', query)
        # Remove any trailing semicolon
        query = query.strip(';')
        return query

    def _validate_query(self, query: str) -> bool:
        """Basic query validation"""
        query_lower = query.lower()
        # Check for basic SQL injection patterns
        dangerous_keywords = [
            "drop table", "truncate table", "delete from",
            "alter table"
        ]
        # Only allow SELECT statements for safety
        if not query_lower.strip().startswith("select" or "insert" or "update"):
            raise ValueError("Only SELECT queries are allowed")
        
        for keyword in dangerous_keywords:
            if keyword in query_lower:
                raise ValueError(f"Dangerous operation detected: {keyword}")
        
        return True

 
    def _run(self, query: str, db_uri: str) -> dict:
        """Execute the query and return results"""
        try:
            # Sanitize and validate the query
            sanitized_query = self._sanitize_query(query)

            # self._validate_query(sanitized_query)

            # Create database connection using environment variables
            engine = create_engine(db_uri)
            
            with engine.connect() as conn:

                result = conn.execute(text(sanitized_query))
                # data= result.fetchall()
                if query.lower().startswith("insert"):
                    conn.commit()
                    inserted_id = ""  # Fetch last inserted ID (if applicable)
                    message = f"Data inserted successfully with ID {inserted_id}" if inserted_id else "Data inserted successfully"
                    return {"status": "success", "data": [], "message": message}
            
                elif query.lower().startswith("update"):
                    conn.commit()
                    message = f"{result.rowcount} record(s) updated"
                    return {"status": "success", "data": [], "message": message}
                
                elif query.lower().startswith("select"):
                    data = result.fetchall()
                    return {"status": "success", "data": list(data), "message": "Data retrieved successfully"}
                
                else:
                    return {"status": "error", "data": [], "message": "Not a valid SQL query"}
            
        except ValueError as ve:
            return {
                "status": "error",
                "data": [],
                "message": f"Validation error: {str(ve)}"
            }
        except Exception as e:
            return {
                "status": "error",
                "data": [],
                "message": f"Database operation error: {str(e)}"
            }

# obj_1 = DatabaseTool()
# result = obj_1._run("select * from product_details", "postgresql://postgres:54321@127.0.0.1:5432/postgres")
# print(result, "result of the query")


# obj_1 = JsonReadTool()
# result = obj_1._run(r"C:\Users\priyanka.b.chila\Documents\product_inventory_flow\product_inventory_git\src\product_inventory\data\cart_output.json")
# print(result, "result of the query")