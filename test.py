from pydantic import BaseModel, EmailStr
from typing import Optional

class User(BaseModel):
    name: str
    age: int
    email: Optional[str]=None
    is_active: bool = True
    role: str = "Viewer"

user = User(name="Anurag",age="51"s)
print(user,type(user))
print(user.name)
print(user.email)
print(user.is_active)
print(user.role)
print(user.model_dump())
print(user.model_dump_json())
print(user.model_validate_json(user.model_dump_json()))