FROM python:3.9-buster

ENV POETRY_VIRTUALENVS_CREATE false
ENV PROJECT_DIR /app

COPY . ${PROJECT_DIR}
WORKDIR ${PROJECT_DIR} 
RUN pip install poetry
RUN python -m poetry export --quiet --without-hashes --format=requirements.txt -o ${PROJECT_DIR}/requirements.txt 
RUN pip install -r ${PROJECT_DIR}/requirements.txt

CMD ["/usr/local/bin/python", "app.py"]