from pydantic import BaseModel
from typing import List


class MeetingPlan(BaseModel):
    chosen_specialists: List[str] = []

class CustomerServiceState(BaseModel):
    query: str = ""
    image_path: str = ""
    pdf_path: str = ""
    json_path: str = ""
    database_connection: str = ""
    table: str = ""
    chosen_specialists: List[str] = []
    opinions: List[str] = []
    response: str = ""

#will be used for adding to cart functionality
class CartItem(BaseModel):
    productid: str
    productmodelnumber: str
    productprice: str
    productquantity: str

class Cart(BaseModel):
    items: List[CartItem] = []