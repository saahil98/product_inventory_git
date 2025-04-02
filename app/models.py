from pydantic import BaseModel
from typing import List

class Product(BaseModel):
    ProdID: int
    ProdName: str
    Brand: str
    Model: str
    productprice: int

class CartItem(BaseModel):
    ProdID: int
    Qty: int


