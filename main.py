#https://realpython.com/python-pydantic/

from pydantic_models import Employee

# emp = Employee(
#     employee_id="123",
#     name=False,
#     email="cdetumaexamplecom",
#     date_of_birth="1939804-02",
#     salary="high paying",
#     department="PRODUCT",
#     elected_benefits=300,
# )
# print(emp)
new_employee_dict = {
    "name": "Chris DeTuma",
    "email": "cdetuma@example.com",
    "date_of_birth": "1998-04-02",
    "salary": 123_000.00,
    "department": "IT",
    "elected_benefits": True,
}
Employee.model_validate(new_employee_dict)
json_schema= Employee.model_json_schema()
print(json_schema)