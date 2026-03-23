from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    name: str
    age: int
    password: str
    bio: Optional[str] = None

user = User(name="Anurag", age=35, password="secret", bio=None)

# Basic dump
print(user.model_dump())