import jwt
import datetime
# from sqlalchemy.orm.exc import NoResultFound


from src import db, app
class ModelUser(db.Model):
    default_locale = "ru-RU"
    default_role = "ADMIN"
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=False, unique=False, nullable=False)
    email = db.Column(db.String(150), index=True, unique=True, nullable=False)
    login = db.Column(db.String(80), index=True, unique=False, nullable=True, default=email)
    age = db.Column(db.Integer, index=True, unique=False, nullable=True)
    phone = db.Column(db.String(12), index=True, unique=False, nullable=True)
    role = db.Column(db.String(64), index=True, unique=False, nullable=False, default=default_role)
    locale = db.Column(db.String(12), index=True, unique=False, nullable=True, default=default_locale)
    password = db.Column(db.String(500), index=True, unique=False, nullable=True)
    notify = db.Column(db.Boolean, default=False, nullable=False)
    personal_data_access = db.Column(db.Boolean, default=True, nullable=False)
    
    def encode_auth_token(self, user_id):
        try:
            payload = {
                "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1, seconds=0),
                "iat": datetime.datetime.utcnow(),
                "sub": user_id
            }
            return jwt.encode(
                payload,
                app.config.get("SECRET_KEY"),
                algorithm="HS256"
            )
        except Exception as e:
            return e

    @staticmethod
    def decode_auth_token(auth_token):
        try:
            payload = jwt.decode(auth_token, app.config.get("SECRET_KEY"))
            ModelUser.query.get(payload["sub"]).locale
            return payload["sub"]
        except (AttributeError, jwt.ExpiredSignatureError):
            return {
                "1" : "expired" 
            }         
        except jwt.InvalidTokenError:
            return {
                "1" : "invalid" 
            }
    
    def __repr__(self) -> str:
        return f"{self.name}, {self.email}"    
