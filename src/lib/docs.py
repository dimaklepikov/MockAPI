from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin

from .schemas import SignupInputSchema, SignupOutputSchema, ErrorSchema

def create_tags(spec):
   tags = [
       {'name': 'signup', 'description': 'Регистрация нового пользователя'},
           ]

   for tag in tags:
       print(f"Добавляем тег: {tag['name']}")
       spec.tag(tag)

def load_docstrings(spec, app):
   for fn_name in app.view_functions:
       if fn_name == 'static':
           continue
       print(f'Загружаем описание для функции: {fn_name}')
       view_fn = app.view_functions[fn_name]
       spec.path(view=view_fn)


def get_apispec(app):
   spec = APISpec(
       title="QAStart",
       version="1.0.0",
       openapi_version="3.0.0",
       plugins=[FlaskPlugin(), MarshmallowPlugin()],
   )

   spec.components.schema("Input", schema=SignupInputSchema)
   spec.components.schema("Output", schema=SignupOutputSchema)
   spec.components.schema("Error", schema=ErrorSchema)

   create_tags(spec)

   load_docstrings(spec, app)

   return spec
