# QAStart Backend

## Install dependencies

poetry install

## Configure settings in cfg/settings.yaml

set database URI and secret key for token encrypting

## Run application

flask app.py

# Deploy project
1. SSH to server ssh username@ip
2. Pull repo via git pull
3. Go to the project directory, run docker-compose up -d --build
4. Check logs if app & database started
5. Run migrations
6. For changes git reset --hard && git pull && git status