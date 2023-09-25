from turtle import pd
from flask import request
from loguru import logger
from flask_restful import Resource, reqparse
from flask import request
from werkzeug.security import generate_password_hash, check_password_hash

import pdb


from ..models.user import db, ModelUser
from src.lib.validation import Validate as v
from src.lib.utils import Utils as u
from src.lib.schemas import *
from src.lib.i18n import Message as m


# TODO:

# Добавить оргс, чтобы они тоже могли управлять юзерами - High Prior
# Локализация Marshmallow - high prior
# Автоматизировать документацию - low priority

# TODO:
# Transfer token validation to v module - medium priority
# Refactor error handlers (returns) to less code - medium priority

class Health(Resource):
    def get(self):
        return {
            "status": u().check()
        }, 200

class Signup(Resource):
    
    def post(self):
        try: 
            SignupInputSchema().load(request.json)
        except ValidationError as err:
            return {"message": err.messages_dict}, 400
        logger.debug(isinstance(request.json['personal_data_access'], str))
        parser = reqparse.RequestParser()
        parser.add_argument("name", type=str)
        parser.add_argument("email", type=str)
        parser.add_argument("password", type=str)
        parser.add_argument("notify", type=bool)
        parser.add_argument("personal_data_access", type=bool)
        parser.add_argument("locale", type=str)
        params = parser.parse_args(strict=True)
        hashed_password = generate_password_hash(params["password"])
        
        msg = m(lang=params["locale"])
        
        if db.session.query(ModelUser).filter(ModelUser.email == params["email"]).all() != []:
            return {"message": msg.get("user.exists")}, 400

        if not params["name"]:
            return {"message": msg.get("user.params.name.missed")}, 400
            
        if not params["email"]:
            return {"message": msg.get("user.params.email.missed")}, 400
            
        if not params["password"]:
            return {"message": msg.get("user.params.password.missed")}, 400
            
        if not params["personal_data_access"]:
            return {"message": msg.get("user.params.personal_data_access.missed")}, 400

        if not v.password(params["password"]):
            return {"message": msg.get("user.params.password.not_valid")}, 400
        
        if not v.name(params["name"]):
            return {"message": msg.get("user.params.name.not_valid")}, 400

        if not v.email(params["email"]):
            return {"message": msg.get("user.params.email.not_valid"),
                    "hint": msg.get("user.params.email.not_valid_hint")}, 400
            
        if (params["email"], params["name"], params ["password"], params["personal_data_access"]) is not None:
                new_user = ModelUser(
                    name=params["name"].replace(" ", ""),
                    email=params["email"].replace(" ", ""),
                    password=hashed_password,
                    notify=params["notify"],
                    personal_data_access=params["personal_data_access"]
                )
                if db.session.query(ModelUser).filter(ModelUser.role == "ADMIN").all() == []:
                    new_user.role = "ADMIN"
                db.session.add(new_user)
                db.session.commit()
                return {
                    "message": msg.get("user.create"),
                    "uuid": new_user.id,
                    "name": new_user.name,
                    "email": new_user.email,
                }, 201
        
class Signin(Resource):
    def post(self):
        try: 
            SigninInputSchema().load(request.json)
        except ValidationError as err:
            return {"message": err.messages_dict}, 400
        parser = reqparse.RequestParser()
        parser.add_argument("email", type=str)
        parser.add_argument("password", type=str)
        params = parser.parse_args()
        msg = m()
        try:
            user = ModelUser.query.filter_by(email=params["email"].replace(" ", "")).first()
            if user is None:
                return {"message": msg.get("user.missing")}, 400
            msg = m(lang=user.locale)
            
            if check_password_hash(user.password, params["password"]):
                token = user.encode_auth_token(user.id)
                return {
                    "message": msg.get("user.params.token.success"),
                    "uuid": user.id,
                    "token": str(token.decode())
                }, 200
            else: 
                return {"message": msg.get("user.params.password.wrong")}, 400
            
        except Exception:
            return {"message": msg.get("user.unexpected")}, 400

class Users(Resource):
    # Add whitespace trailing
    def get(self):
        try: 
            GetUsersSchema().load(request.args)
        except ValidationError as err:
            return {"message": err.messages_dict}, 400
        parser = reqparse.RequestParser()
        parser.add_argument("Access-Token", type=str, location='headers')
        parser.add_argument("email", type=str, location='args')
        parser.add_argument("name", type=str, location='args')
        parser.add_argument("page", type=int, location='args')
        parser.add_argument("per_page", type=int, location='args')
        params =  parser.parse_args()
        msg = m()
        utils = u()
        if params["Access-Token"]:
            decoded_token = ModelUser.decode_auth_token(params["Access-Token"])
            if not isinstance(decoded_token, dict): 
                lang = db.session.query(ModelUser).get(decoded_token).locale
                msg = m(lang=lang)
                users = []
                if params["email"]:
                    users.append(ModelUser.query.filter(ModelUser.email.like(params["email"].replace(" ", ""))).all())
                if params["name"]:
                    users.append(ModelUser.query.filter(ModelUser.name.like(params["name"].replace(" ", ""))).all())
                if not params["email"] and not params["name"]:
                    users.append(ModelUser.query.all())
                if users == []:
                    return 
                users = [
                    {
                    "uuid": user.id,
                    "name": user.name,
                    "email": user.email,
                    "role": user.role,
                    }  for query in users for user in query 
                    ]
                unique_users = list({u["uuid"]:u for u in users}.values())
                if params["page"] and params["per_page"]:
                    result = utils.get_paginated_response(obj=unique_users, page=params["page"], per_page=params["per_page"])
                    return result[0], result[1]
                if params["page"]: 
                    result = utils.get_paginated_response(obj=unique_users, page=params["page"])
                    return result[0], result[1]
                if params["per_page"]:
                    result = utils.get_paginated_response(obj=unique_users, per_page=params["per_page"])
                    return result[0], result[1]
                else: 
                    result = utils.get_paginated_response(obj=unique_users)
                    return result[0], result[1]
            else:
                if decoded_token['1'] == 'expired':
                    return {"message": msg.get("user.params.token.expired")}, 401
                if decoded_token['1'] == 'invalid':
                    return {"message": msg.get("user.params.token.invalid")}, 401
        else:
            return {"message": msg.get("user.params.token.missed")}, 401

class User(Resource):
    def get(self, user_id=None):
        msg = m()
        parser = reqparse.RequestParser()
        parser.add_argument("Access-Token", type=str, location='headers')
        params =  parser.parse_args()
        if user_id is None:
            {"message": msg.get("user.params.id.missed")}, 400 
        if params["Access-Token"]:
            decoded_token = ModelUser.decode_auth_token(params["Access-Token"])
            if not isinstance(decoded_token, dict):
                # pdb.set_trace()
                lang = db.session.query(ModelUser).get(decoded_token).locale
                msg=m(lang=lang if lang else None)
                try:
                    user = ModelUser.query.get(user_id)
                except Exception:
                    return {"message": msg.get("user.unexpected")}, 400
                if user: 
                    return {
                    "uuid": user.id,
                    "name": user.name,
                    "email": user.email,
                    "age": user.age,
                    "login": user.login,
                    "phone": user.phone,
                    "role": user.role,
                    "locale": user.locale,
                    "notify": user.notify,
                    "personal_data_access": user.personal_data_access,
                    }
                else: 
                    # pdb.set_trace()
                    return {"message": msg.get("user.missing")}, 400
            else:
                if decoded_token['1'] == 'expired':
                    return {"message": msg.get("user.params.token.expired")}, 401
                if decoded_token['1'] == 'invalid':
                    return {"message": msg.get("user.params.token.invalid")}, 401
        else:
            return {"message": msg.get("user.params.token.missed")}, 401

    def post(self):
        try: 
            CreateUserSchema().load(request.json)
        except ValidationError as err:
            return {"message": err.messages_dict}, 400

        parser = reqparse.RequestParser()
        parser.add_argument("name", type=str)
        parser.add_argument("email", type=str)
        parser.add_argument("age", type=int)
        parser.add_argument("login", type=str)
        parser.add_argument("password", type=str)
        parser.add_argument("phone", type=str)
        parser.add_argument("role", type=str)
        parser.add_argument("locale", type=str)
        parser.add_argument("notify", type=bool)
        parser.add_argument("Access-Token", type=str, location="headers")
        params = parser.parse_args()
        msg = m()
        if params["Access-Token"]:
            decoded_token = ModelUser.decode_auth_token(params["Access-Token"])
            if not isinstance(decoded_token, dict):
                lang = db.session.query(ModelUser).get(decoded_token).locale
                msg=m(lang=lang)
                if params["password"] and not v.password(params["password"]):
                    hashed_password = generate_password_hash(params["password"])
                    return {"message": msg.get("user.params.password.not_valid")}, 400
                else:
                    hashed_password = None
                    
                if not v.name(params["name"]):
                    return {"message": msg.get("user.params.name.not_valid")}, 400


                if not v.email(params["email"]):
                    return {"message": msg.get("user.params.email.not_valid")}, 400

                    # try:
                if db.session.query(ModelUser).get(decoded_token).role == "ADMIN" or "ORGANIZATION":
                    if db.session.query(ModelUser).filter(ModelUser.email == params["email"]).all() != []:
                        return {"message": msg.get("user.exists")}, 400
                        
                    if not v.phone(params["phone"]):
                        return {"message": msg.get("user.params.phone.not_valid")}, 400
                
                    if not v.role(params["role"]):
                        return {"message": msg.get("user.params.role.not_valid")}, 400
                        
                    if not v.password(params["password"]):
                        return {"message": msg.get("user.params.password.not_valid")}, 400
                        
                    if params["email"] and params["name"]:
                        new_user = ModelUser(
                            name=params["name"].replace(" ", ""),
                            email=params["email"].replace(" ", ""),
                            password=hashed_password,
                            age=params["age"],
                            login=params["login"].replace(" ", "") if params["login"] is not None else None,
                            phone=params["phone"],
                            role=params["role"],
                            locale=params["locale"],
                            notify=params["notify"],
                        )
                        db.session.add(new_user)
                        db.session.commit()

                        if new_user:
                            return {
                            "uuid": new_user.id,
                            "name": new_user.name,
                            "email": new_user.email,
                            "age": new_user.age,
                            "login": new_user.login,
                            "phone": new_user.phone,
                            "role": new_user.role,
                            "locale": new_user.locale,
                            "notify": new_user.notify,
                            "personal_data_access": new_user.personal_data_access,
                            }, 201
                else:
                    return {"message": msg.get("user.params.role.not_allowed_to_create")}, 403
            else:
                if decoded_token['1'] == 'expired':
                    return {"message": msg.get("user.params.token.expired")}, 401
                if decoded_token['1'] == 'invalid':
                    return {"message": msg.get("user.params.token.invalid")}, 401
        else:
            return {"message": msg.get("user.params.token.missed")}, 401


    def put(self, user_id=None):
        try: 
            UpdateUserSchema().load(request.json)
        except ValidationError as err:
            return {"message": err.messages_dict}, 400

        parser = reqparse.RequestParser()
        parser.add_argument("name", type=str)
        parser.add_argument("age", type=int)
        parser.add_argument("locale", type=str)
        parser.add_argument("role", type=str)
        parser.add_argument("phone", type=str)
        parser.add_argument("notify", type=bool)
        parser.add_argument("Access-Token", type=str, location="headers")
        params = parser.parse_args()
        msg = m()
        if user_id is None:
            return {"message": msg.get("user.params.id.missed")}, 400 

        if params["Access-Token"]:
            decoded_token = ModelUser.decode_auth_token(params["Access-Token"])
            if not isinstance(decoded_token, dict):
                lang = db.session.query(ModelUser).get(decoded_token).locale
                msg=m(lang=lang)
                try:
                    if  db.session.query(ModelUser).get(decoded_token).role == "ADMIN" or "ORGANIZATION":
                        if not v.role(params["role"]):
                            return {"message": msg.get("user.params.role.not_valid")}, 400
                        
                        if not v.name(params["name"]):
                            return {"message": msg.get("user.params.name.not_valid")}, 400

                            
                        if not v.phone(params["phone"]):
                            return {"message": msg.get("user.params.phone.not_valid")}, 400

                        try:
                            user = ModelUser.query.filter_by(id=user_id).first()
                            # pdb.set_trace()      
                            if (params["name"], params["role"], params["phone"], params["notify"]) is not None:
                                user.name = params["name"].replace(" ", "")
                                user.role = params["role"]
                                user.phone = params["phone"]
                                user.notify = params["notify"]
                                user.age = params["age"] if params["age"] is not None else user.age
                                user.locale = params["locale"] if params["locale"] is not None else user.locale
                                db.session.commit()
                                if user:
                                    return {
                                    "message": msg.get("user.update"),
                                    "uuid": user.id,
                                    "name": user.name,
                                    "email": user.email,
                                    "login": user.login,
                                    "age": user.age,
                                    "phone": user.phone,
                                    "role": user.role,
                                    "locale": user.locale,
                                    "notify": user.notify,
                                    "personal_data_access": user.personal_data_access,
                                    }, 201
                                else: 
                                    return {"message": msg.get("user.not_updated")}, 400
                        except AttributeError:
                            return {"message": msg.get("user.params.id.missed")}, 400
                    else:
                        return {"message": msg.get("user.params.role.not_allowed_to_update")}, 403
                except AttributeError:
                    return {"message": msg.get("user.params.token.unauthorized")}, 401
            else:
                if decoded_token['1'] == 'expired':
                    return {"message": msg.get("user.params.token.expired")}, 401
                if decoded_token['1'] == 'invalid':
                    return {"message": msg.get("user.params.token.invalid")}, 401
        else:
            return {"message": msg.get("user.params.token.missed")}, 401
            
    def delete(self, user_id=None):
        parser = reqparse.RequestParser()
        parser.add_argument("Access-Token", type=str, location="headers")
        params = parser.parse_args() 
        msg = m()
        if user_id is None:
            return {"message": msg.get("user.params.id.missed")}, 400 
             
        if params["Access-Token"]:
            decoded_token = ModelUser.decode_auth_token(params["Access-Token"])
            if not isinstance(decoded_token, dict):
                lang = db.session.query(ModelUser).get(decoded_token).locale
                msg=m(lang=lang)
                try:
                    if db.session.query(ModelUser).get(decoded_token).role == "ADMIN" or "ORGANIZATION":
                        if ModelUser.query.get(user_id) is None:
                            return {"message": msg.get("user.missing")}, 400 
                        try:
                            user = ModelUser.query.filter_by(id=user_id)
                            user.delete()
                            db.session.commit()
                            return {"message": msg.get("user.delete")}, 200
                        except Exception as e:
                            return {"message": msg.get("user.unexpected")}, 400
                    else:
                        return {"message": msg.get("user.params.role.not_allowed_to_delete")}, 403
                except AttributeError:
                    return {"message": msg.get("user.params.token.unauthorized")}, 401
            else:
                if decoded_token['1'] == 'expired':
                    return {"message": msg.get("user.params.token.expired")}, 401
                if decoded_token['1'] == 'invalid':
                    return {"message": msg.get("user.params.token.invalid")}, 401
        else:
            return {"message": msg.get("user.params.token.missed")}, 401
