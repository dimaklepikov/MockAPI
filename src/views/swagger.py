from flask_restful import Resource

from src import app
from src.lib.docs import get_apispec
class SwaggerUi(Resource): 
    def get(self):
        return get_apispec(app).to_dict()
