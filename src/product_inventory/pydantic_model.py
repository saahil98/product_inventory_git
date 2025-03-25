from pydantic import BaseModel
from typing import List


class MeetingPlan(BaseModel):
    chosen_specialists: List[str] = []

class CustomerServiceState(BaseModel):
    query: str = ""
    chosen_specialists: List[str] = []
    opinions: List[str] = []
    response: str = ""
