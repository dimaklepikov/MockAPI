### To create migrations:

flask db migrate


### To set head migration if database is not up to date

flask db stamp head


### To run migrations:

flask db upgrade

### To rollback:

flask db downgrade
