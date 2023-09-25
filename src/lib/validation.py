import re
import phonenumbers
from phonenumbers import carrier
from phonenumbers.phonenumberutil import number_type, NumberParseException
from loguru import logger
import json


from src import app
from src.lib.i18n import Message as m
from .constants import ROLES, STR_BOOLEANS


msg = m()

@app.errorhandler(404) 
def invalid_route(e): 
    return {
        "message": msg.get('page.invalid')
    }, 404

    # @app.errorhandler(500) 
    # def server_error(self, e):
    #     logger.add("file_{time}.log")
    #     return {
    #         "message": "Server error. Something went wrong"
    # }, 500

class Validate:
    def email(email):
        # ^([A-Za-z0-9._-])+@([A-Za-z0-9._-])+\.([A-Za-z]{2,63})$
        if re.match(r"[A-Za-z0-9._-]+@[A-Za-z0-9._-]+\.[A-Za-z]+", email) and len(email) <=150 and len(email) >= 6:
            return True
            
        else:
            return False
    
    def name(name):
        if re.match(r"[a-zA-Z0-9]", name) and len(name) >=3 and len(name) <= 30:
            return True
            
        else:
            return False
    
    def phone(phone):
        if phone is None:
            return True
        else:
            try: 
                return carrier._is_mobile(number_type(phonenumbers.parse(phone)))
            except NumberParseException:
                return False
           
    def password(password):
        # Simplified without p cehck
        if password is None:
            return True
        l, u, d = 0, 0, 0
        if (len(password) >= 8 and len(password) <= 50):
            for i in password:
        
                if (i.islower()):
                    l+=1           
        
                if (i.isupper()):
                    u+=1           
        
                if (i.isdigit()):
                    d+=1           
        
                # if(i=='@'or i=='$' or i=='_'):
                #     p+=1          
            if (l>=1 and u>=1 and d>=1 and l+u+d==len(password)):
                return True
            else:
                return False
            
    def role(role):
        return True if role in ROLES or role is None else False
    
    def string_to_bool(value):
        # return True if value in STR_BOOLEANS else False 
        if isinstance(value, str) and value in STR_BOOLEANS:
            return json.loads(value.lower())
        if isinstance(value, bool):
            return value
        if value is None:
            return None
        else:
            raise ValueError
        
    def is_admin(user):
         pass
