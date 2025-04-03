from pydantic import BaseModel
from typing import List , Optional

class Product(BaseModel):
    ProdID: int
    ProdName: str
    Brand: str
    Model: str
    productprice: int

class CartItem(BaseModel):
    ProdID: int
    Qty: int

class CustomerRequest(BaseModel):
    query: str
    image_path: Optional[str] = None
    pdf_path: Optional[str] = None
    json_path: Optional[str] = None
    database_connection: Optional[str] = None
    table: Optional[str] = None