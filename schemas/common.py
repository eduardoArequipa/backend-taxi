from pydantic import BaseModel
from typing import List

class Point(BaseModel):
    type: str = "Point"
    coordinates: List[float]
