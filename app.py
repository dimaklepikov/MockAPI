from flask_restful import Api
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint

from src import app, cfg
from src.lib.constants import Url


if __name__ == '__main__':
    api = Api(app)

    from src.views.user import Signin, Signup, Users, User, Health
    from src.views.swagger import SwaggerUi
    api.add_resource(Health, '/health')
    api.add_resource(SwaggerUi, '/swagger')
    api.add_resource(Signup, '/signup')
    api.add_resource(Signin, '/signin')
    api.add_resource(Users, '/users')
    api.add_resource(User, '/user', '/user/<int:user_id>')

    swagger = get_swaggerui_blueprint(
        Url.SWAGGER_URL,
        Url.SWAGGER_API_URL,
        config={
            'app_name': cfg['app']['name']
        }
    )
    
    CORS(app)
    
    app.register_blueprint(swagger)
 
    app.run(
        host=cfg['bind']['host'],
        port=cfg['bind']['port'],
        debug=cfg['app']['debug'],
    )
