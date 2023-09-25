from marshmallow import Schema, fields, ValidationError, validates_schema

# ADD QUERY PARAMS TO SCHEMA
# Localize mashmellow

class StringBoolean(fields.Field):
    def _deserialize(self, value, attr, data, **kwargs):
        if isinstance(value, str) or isinstance(value, bool):
            return value
        else:
            raise ValidationError('Field should be str or bool')

class SignupInputSchema(Schema):
    name = fields.String(description="Имя", required=True, example="Иван")
    email = fields.String(description="Email", required=True)
    password = fields.String(description="Пароль", required=True)
    notify = fields.Boolean(description="Получать уведомления", required=False, truthy={True}, falsy={False})
    personal_data_access = fields.Boolean(description="Согласие на обработку персональных данных", required=True, truthy={True}, falsy={False})
    locale = fields.Str(description="", required=False)

class GetUsersSchema(Schema):
    name = fields.String(description="Имя", required=False)
    email = fields.String(description="Email", required=False)
    page = fields.Integer(description="Страница", required=False)
    per_page = fields.Integer(description="Кол-во пользоватлей на странице", required=False)

class CreateUserSchema(Schema):
    name = fields.String(description="Имя", required=True)
    email = fields.String(description="Email", required=True)
    age = fields.Integer(description="Возраст", required=False)
    login = fields.String(description="Login", required=False)
    password = fields.String(description="Пароль", required=False)
    phone = fields.Number(description="Телефон", required=False)
    role = fields.String(description="Роль", required=False)
    locale = fields.String(description="Язык", required=False)
    notify = fields.Boolean(description="Получать уведомления", required=False, truthy={True}, falsy={False})

class UpdateUserSchema(Schema):
    name = fields.String(description="Имя", required=True)
    role = fields.String(description="Роль", required=True)
    locale = fields.String(description="Язык", required=False)
    age = fields.Integer(description="Возраст", required=False)
    phone = fields.Number(description="Телефон", required=True)
    notify = fields.Boolean(description="Получать уведомления", required=True, truthy={True}, falsy={False})

class SigninInputSchema(Schema):
    email = fields.String(description="Email", required=True)
    password = fields.String(description="Пароль", required=True)

class SignupOutputSchema(Schema):
    message = fields.String(description="Сообщение", required=True)
    uuid = fields.Integer(description="Id пользователя", required=True)
    email = fields.String(description="Email пользователя", required=True)
    notify = fields.Boolean(description="Получать уведомления", required=False, truthy={True}, falsy={False})
    personal_data_access = fields.Boolean(description="Согласие на обработку персональных данных", required=True, truthy={True}, falsy={False})

class ErrorSchema(Schema):
    message = fields.String(description="Сообщение", required=True)
