from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import sys, json, os
from .models import CartItem, Product, CustomerRequest
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.product_inventory.flows import CustomerServiceFlow
from app.models import Product,CartItem
from typing import List

import os
from typing import List

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
            "pdf_path": str(request.pdf_path) or "",
            "json_path": str(request.json_path) or "",
            # "json_path": os.path.join(os.path.dirname(__file__), 'data', 'cart_output.json'),
            "database_connection": str(request.database_connection) or "postgresql:postgres:54321//@localhost:5432/postgres",
            "table": request.table or "product_details"
        }

        # Execute the flow
        result =  flow.kickoff(inputs=inputs)

        return json.loads(result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint specifically for cart operations
# @app.post("/cart")
# async def handle_cart_request(request: CustomerRequest):
#     try:
#         flow = CustomerServiceFlow()
        
#         # Specific cart-related inputs
#         inputs = {
#             "query": request.query,
#             "json_path": request.json_path or os.path.join(os.path.dirname(__file__), 'data', 'cart_output.json'),
#             "database_connection": request.database_connection or "postgresql:postgres:54321//@localhost:5432/postgres",
#             "table": "product_details"
#         }

#         result = flow.kickoff(inputs=inputs)

#         return {
#             "status": "success",
#             "cart_result": result
#         }

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# Sample product data
products_db = [
    {
        "ProdID": 1, 
        "ProdName": "LG 185 L 5 Star Inverter Direct-Cool Single Door Refrigerator", 
        "Brand": "LG",
        "Model": "GL-D201ABEU",
        "productprice": 17490
    },
    {
        "ProdID": 2, 
        "ProdName": "LG 322 L 3 Star Frost-Free Smart Inverter Double Door Refrigerator (GL-S342SDSX, Dazzle Steel, Convertible with Express Freeze)", 
        "Brand": "LG",
        "Model": "GL-S342SDSX",
        "productprice": 36990
    },
    {
        "ProdID": 3, 
        "ProdName": "Bosch 10kg 5 Star Anti Stain & AI Active Water Plus Fully Automatic Front Load Washing Machine with Built-in Heater (WGA252ZSIN, Pretreatment, Iron Steam Assist & Allergy Plus, Silver)", 
        "Brand": "Bosch",
        "Model": "WGA252ZSIN",
        "productprice": 42990
    },
    {
        "ProdID": 4, 
        "ProdName": "Samsung 12 kg, 5 Star, AI Ecobubble, Super Speed, Wi-Fi, Hygiene Steam with Inbuilt Heater, Digital Inverter, Fully-Automatic Front Load Washing Machine (WW12DG6B24ASTL, Navy)", 
        "Brand": "Samsung",
        "Model": "WW12DG6B24ASTL",
        "productprice": 46990
    },
    {
        "ProdID": 5, 
        "ProdName": "Sony Alpha ILCE-6100L APS-C Camera (16-50mm Lens) | 24.2 MP | Fast Auto Focus, Real-time Eye AF, Real-time Tracking | 4K Vlogging Camera – Black", 
        "Brand": "Sony",
        "Model": "ILCE-6100L",
        "productprice": 61490
    },
    {
        "ProdID": 6, 
        "ProdName": "Fujifilm X-T5 40MP APS-C X-Trans Sensor | Pixel Shift | IBIS System | Ultra High Resolution Mirrorless Camera | 6.2k 30p | Subject Tracking | 1/180000 Shutter Speed | Touchtracking | Quick Lever for Photo/Video - S", 
        "Brand": "Fujifilm",
        "Model": "203399",
        "productprice": 143000
    }
]


cart_db = []


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



# Sample product data
products_db = [
    {
        "ProdID": 1, 
        "ProdName": "LG 185 L 5 Star Inverter Direct-Cool Single Door Refrigerator", 
        "Brand": "LG",
        "Model": "GL-D201ABEU",
        "productprice": 17490
    },
    {
        "ProdID": 2, 
        "ProdName": "LG 322 L 3 Star Frost-Free Smart Inverter Double Door Refrigerator (GL-S342SDSX, Dazzle Steel, Convertible with Express Freeze)", 
        "Brand": "LG",
        "Model": "GL-S342SDSX",
        "productprice": 36990
    },
    {
        "ProdID": 3, 
        "ProdName": "Bosch 10kg 5 Star Anti Stain & AI Active Water Plus Fully Automatic Front Load Washing Machine with Built-in Heater (WGA252ZSIN, Pretreatment, Iron Steam Assist & Allergy Plus, Silver)", 
        "Brand": "Bosch",
        "Model": "WGA252ZSIN",
        "productprice": 42990
    },
    {
        "ProdID": 4, 
        "ProdName": "Samsung 12 kg, 5 Star, AI Ecobubble, Super Speed, Wi-Fi, Hygiene Steam with Inbuilt Heater, Digital Inverter, Fully-Automatic Front Load Washing Machine (WW12DG6B24ASTL, Navy)", 
        "Brand": "Samsung",
        "Model": "WW12DG6B24ASTL",
        "productprice": 46990
    },
    {
        "ProdID": 5, 
        "ProdName": "Sony Alpha ILCE-6100L APS-C Camera (16-50mm Lens) | 24.2 MP | Fast Auto Focus, Real-time Eye AF, Real-time Tracking | 4K Vlogging Camera – Black", 
        "Brand": "Sony",
        "Model": "ILCE-6100L",
        "productprice": 61490
    },
    {
        "ProdID": 6, 
        "ProdName": "Fujifilm X-T5 40MP APS-C X-Trans Sensor | Pixel Shift | IBIS System | Ultra High Resolution Mirrorless Camera | 6.2k 30p | Subject Tracking | 1/180000 Shutter Speed | Touchtracking | Quick Lever for Photo/Video - S", 
        "Brand": "Fujifilm",
        "Model": "203399",
        "productprice": 143000
    }
]


cart_db = []


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
