from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import sys, json, os
from .models import CartItem, Product, CustomerRequest
from .product_data import products_db
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.product_inventory.flows import CustomerServiceFlow
from app.models import Product,CartItem
from typing import List
import os
from typing import List


cart_db = []
app = FastAPI()

@app.post("/customer-service")
def handle_customer_request(request: CustomerRequest):
    try:
        # Initialize the flow
        flow = CustomerServiceFlow()
        
        # Prepare inputs
        inputs = {
            "query": request.query,
            "image_path": str(request.image_path) or "",
            # "image_path": os.path.join(os.path.dirname(__file__), 'data', 'image.jpg'),
            # "C:\Users\priyanka.b.chila\Documents\product_inventory_flow\product_inventory_git\src\product_inventory\data\Product Details.pdf"
            "pdf_path": os.path.join(os.path.dirname(__file__), 'data', 'Product Details.pdf'),
            # "json_path": str(request.json_path) or "",
            "json_path": os.path.join(os.path.dirname(__file__), 'data', 'cart_output.json'),
            "database_connection": str(request.database_connection) or "postgresql:postgres:54321//@localhost:5432/postgres",
            "table": request.table or "product_details"
        }

        # Execute the flow
        result =  flow.kickoff(inputs=inputs)
        flow_state = flow.state
        print(result, flow_state, "resposne")
        # result["State"] = flow_state
        return json.loads(result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/products", response_model=List[Product])
async def get_products():
    return products_db

@app.post("/cart")
async def add_to_cart(cart_item: CartItem):
    print(cart_item)
    product = next((item for item in products_db if item["ProdID"] == cart_item.ProdID), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    cart_db.append({"ProdID": cart_item.ProdID, "Qty": cart_item.Qty})
    return {"cart": cart_db, "message": "Item added successfully"}



# Example usage with curl:
"""
curl -X POST     \
-H "Content-Type: application/json" \
-d '{
    "query": "add 5 items of LG Direct-Cool Single Door Refrigerator to the cart",
    "database_connection": "postgresql:postgres:54321//@localhost:5432/postgres",
    "table": "product_details"
}'
"""
 