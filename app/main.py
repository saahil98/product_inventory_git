from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.product_inventory.flows import CustomerServiceFlow
import os

app = FastAPI()

class CustomerRequest(BaseModel):
    query: str
    image_path: Optional[str] = None
    pdf_path: Optional[str] = None
    json_path: Optional[str] = None
    database_connection: Optional[str] = None
    table: Optional[str] = None

@app.post("/customer-service")
def handle_customer_request(request: CustomerRequest):
    try:
        # Initialize the flow
        flow = CustomerServiceFlow()
        
        # Prepare inputs
        inputs = {
            "query": request.query,
            "image_path":r"C:\Users\priyanka.b.chila\Documents\product_inventory_flow\product_inventory_git\src\product_inventory\data\image.jpg",
            # "image_path": os.path.join(os.path.dirname(__file__), 'data', 'image.jpg'),
            "pdf_path": "",
            "json_path": r"C:\Users\priyanka.b.chila\Documents\product_inventory_flow\product_inventory_git\src\product_inventory\data\cart_output.json",
            # "json_path": os.path.join(os.path.dirname(__file__), 'data', 'cart_output.json'),
            "database_connection": "postgresql:postgres:54321//@localhost:5432/postgres",
            "table": "product_details"
        }

        # Execute the flow
        result =  flow.kickoff(inputs=inputs)

        return {
            "status": "success",
            "result": result,
            "flow_state": str(flow.state)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint specifically for cart operations
@app.post("/cart")
async def handle_cart_request(request: CustomerRequest):
    try:
        flow = CustomerServiceFlow()
        
        # Specific cart-related inputs
        inputs = {
            "query": request.query,
            "json_path": request.json_path or os.path.join(os.path.dirname(__file__), 'data', 'cart_output.json'),
            "database_connection": request.database_connection or "postgresql:postgres:54321//@localhost:5432/postgres",
            "table": "product_details"
        }

        result = flow.kickoff(inputs=inputs)

        return {
            "status": "success",
            "cart_result": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
