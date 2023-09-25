# Mock Backend

## Install dependencies

poetry install

## Configure settings in cfg/settings.yaml

set database URI and secret key for token encrypting

## Run application

flask app.py

# Deploy project
1. Pull repo via git pull
2. run docker-compose up -d --build
3. Check logs if app & database started
4. Run migrations
5. For changes git reset --hard && git pull && git status
