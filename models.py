from email.policy import default
from tortoise import Model , fields
from pydantic import BaseModel
from datetime import datetime
from tortoise.contrib.pydantic import pydantic_model_creator

class User(Model):
    id = fields.IntField(pk = True , index = True)
    username = fields.CharField(max_length=32, null = False , unique = True)
    email = fields.CharField(max_length=200 , null = False , unique = True)
    password = fields.CharField(max_length=100 , null = False)
    is_verified = fields.BooleanField(default = False)
    join_date = fields.DatetimeField(default = datetime.utcnow)


class Product(Model):
    id = fields.IntField(pk = True , index = True)
    name = fields.CharField(max_length=200 , null = False)
    price = fields.FloatField(null = False)
    description = fields.CharField(max_length=10000,null = False)
    category = fields.CharField(max_length=100 , null = False)
    image = fields.CharField(max_length = 500, null = False)

class Cart(Model):
    id = fields.IntField(pk = True , index = True)
    user_id = fields.IntField(null = False)
    product_id = fields.IntField(null = False)
    quantity = fields.IntField(null = False)
    unit_price = fields.FloatField(null = False)


user_pydantic = pydantic_model_creator(User , name = "User" , exclude=("is_verified" ,))
user_pydanticIn = pydantic_model_creator(User , name = "UserIn" , exclude_readonly=True, exclude=("is_verified" , "join_date"))
user_pydanticOut = pydantic_model_creator(User , name = "UserOut" , exclude=("password"))


product_pydantic = pydantic_model_creator(Product , name = "Product")
product_pydanticIn = pydantic_model_creator(Product , name = "ProductIn" , exclude_readonly=True)
product_pydanticOut = pydantic_model_creator(Product , name = "ProductOut")


cart_pydantic = pydantic_model_creator(Cart , name = "Cart")
cart_pydanticIn = pydantic_model_creator(Cart , name = "CartIn" , exclude_readonly=True)
cart_pydanticOut = pydantic_model_creator(Cart , name="CartOut")


