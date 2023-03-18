from typing import Union
from fastapi.middleware.cors import CORSMiddleware
from auth import AuthHandler
from fastapi import Depends, FastAPI , HTTPException
from tortoise.contrib.fastapi import register_tortoise
from models import *


app = FastAPI()

auth_handler = AuthHandler()

#CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"]
)

#user login request 
class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/register" , status_code=201)
async def user_register(user : user_pydanticIn):
    user_info = user.dict(exclude_unset=True)
    user_info["password"] = auth_handler.get_hashed_password(user_info["password"])
    user_obj = await User.create(**user_info)
    new_user = await user_pydantic.from_tortoise_orm(user_obj)
    return{
        "status" : "ok",
        "data" : {
            "username" : new_user.dict()["username"],
            "email" : new_user.dict()["email"],
            "userId" : new_user.dict()["id"]
        }
    }

@app.post("/login")
async def login(user : LoginRequest):
    token = await auth_handler.token_generator(user.username , user.password)
    return {
        "status" : "ok",
        "token" : token
    }


# products

## get products
@app.get('/products')
async def get_products(product_name : Union[str, None] = None,payload = Depends(auth_handler.auth_wrapper)):
    
    all_products = []

    if product_name:
        all_products = await product_pydanticOut.from_queryset(Product.filter(name = product_name).all())

    else:
        all_products = await product_pydanticOut.from_queryset(Product.all())

    return {
        "status": "ok",
        "data" :  all_products
    }

## get product by id
@app.get('/products/{id}',status_code=200)
async def get_product_by_id(id : int , payload = Depends(auth_handler.auth_wrapper)):
    product = await product_pydanticOut.from_queryset_single(Product.get(id = id))

    return {
        "status" : "ok",
        "data" : product
    }

# add product
@app.post("/product" , status_code=201)
async def add_product(product : product_pydanticIn):

    product_info = product.dict(exclude_unset=True)
    product_obj = await Product.create(**product_info)
    new_product = await product_pydantic.from_tortoise_orm(product_obj)
    return {
        "status" : "ok",
        "data" : new_product
    }



# cart

## add product to cart
@app.post("/cart" , status_code = 201)
async def add_to_cart(cart_item : cart_pydanticIn, payload= Depends(auth_handler.auth_wrapper)):
    cart_info = cart_item.dict(exclude_unset=True)
    cart_obj = await Cart.create(**cart_info)
    new_cart_item = await cart_pydantic.from_tortoise_orm(cart_obj)
    return {
        "status" : "ok",
        "data" : new_cart_item
    }

## get products in cart
@app.get("/cart" , status_code=200)
async def get_cart_items(payload = Depends(auth_handler.auth_wrapper)):
    
    id = payload["id"]
    cart_items = await cart_pydanticOut.from_queryset(Cart.filter(user_id = id).all())
    
    response = []

    for item in cart_items:
        cart_item = item.dict()
        product_id = cart_item["product_id"]
        product =  await product_pydanticOut.from_queryset_single(Product.get(id = product_id))
        cart_item["product"] = product
        response.append(cart_item)

    return {
        "status" : "ok",
        "data" : response
    }

## update product in cart
@app.patch("/cart" , status_code=200)
async def update_cart_item(cart_item : cart_pydanticIn,payload = Depends(auth_handler.auth_wrapper)):
    user_id = payload["id"]
    cart_info = cart_item.dict(exclude_unset=True)
    if cart_info["quantity"] <= 0:
        deleted_cart_item = await Cart.filter(user_id = user_id , product_id = cart_info["product_id"]).delete()
        
        if not deleted_cart_item:
            raise HTTPException(status_code = 404 , detail = "cart item not found")
        return {
            "status" : "ok",
            "data" : {}
        }
    else:
        await Cart.filter(user_id = user_id , product_id = cart_info["product_id"]).update(**cart_info)
        updated_cart_item = await cart_pydantic.from_queryset_single(Cart.filter(user_id = user_id , product_id = cart_info["product_id"]).get())
        return {
        "status" : "ok",
        "data" : updated_cart_item
        }


## delete product from cart
@app.delete("/cart" , status_code = 200)
async def delete_cart_item(product_id: int , payload = Depends(auth_handler.auth_wrapper)):

    user_id = payload["id"]

    deleted_cart_item = await Cart.filter(user_id = user_id , product_id = product_id).delete()

    if not deleted_cart_item:
        raise HTTPException(status_code = 404 , detail = "cart item not found")

    return {
        "status" : "ok",
        "data" : {}
    }


## get total cart price
@app.get("/cart/price" , status_code = 200)
async def get_total_price(payload = Depends(auth_handler.auth_wrapper)):
    user_id = payload["id"]
    total_amount = 0
    cart_items = await cart_pydanticOut.from_queryset(Cart.filter(user_id = user_id).all())
    
    for item in cart_items:
        cart_item = item.dict()
        total_amount += cart_item["quantity"] * cart_item["unit_price"]
    
    return {
        "status" : "ok",
        "data" : {
            "total" : total_amount
        }
    }

@app.get("/")
def index():
    return {"message" : "working!!"}




# mysql://<db-user>:<db-user-password>@localhost:3306/<db-name>
register_tortoise(
    app,
    db_url="mysql://root:root@localhost:3306/fast_api",
    modules={"models" : ["models"]},
    generate_schemas=True,
    add_exception_handlers=True
)