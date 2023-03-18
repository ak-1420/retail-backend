from models import User
from passlib.context import CryptContext
from fastapi import HTTPException , Security
from datetime import datetime , timedelta
from fastapi.security import HTTPAuthorizationCredentials , HTTPBearer
import jwt


class AuthHandler():
    security = HTTPBearer()
    pwd_context = CryptContext(schemes=['bcrypt'] , deprecated = 'auto')
    secret = "SECRET"

    def get_hashed_password(self, password):
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password  , hashed_password):
        return self.pwd_context.verify(plain_password , hashed_password)
    
    def encode_token(self, user_id):        
        payload = {
            'exp': datetime.utcnow() + timedelta(days=0, minutes=30),
            'iat': datetime.utcnow(),
            'sub': user_id
        }
        return jwt.encode(
            payload,
            self.secret,
            algorithm='HS256'
        )

    def decode_token(self, token):
        try:
            payload = jwt.decode(token, self.secret, algorithms=['HS256'])
            return payload['sub']
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail='Signature has expired')
        except jwt.InvalidTokenError as e:
            raise HTTPException(status_code=401, detail='Invalid token')

    def auth_wrapper(self, auth: HTTPAuthorizationCredentials = Security(security)):
        return self.decode_token(auth.credentials)

    
    async def token_generator(self , username : str , password : str):

        user = await self.authenticate_user(username , password)
        if not user:
            raise HTTPException(
                status_code= 401,
                detail="Invalid Username or Password",
                headers={"WWW-Authenticate" : "Bearer"}
            )
        payload = {
            'exp': datetime.utcnow() + timedelta(days=0, minutes=2),
            'iat': datetime.utcnow(),
            'sub': {
                "id" : user.id,
                "username" : user.username
            } 
        }
        token = jwt.encode(payload , self.secret , algorithm="HS256")
        return token
    

    async def authenticate_user(self , username : str , password : str):
        user = await User.get(username = username)

        if user and self.verify_password(password , user.password):
            return user
            
        return False