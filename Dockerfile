FROM python:3.11-slim

ENV PYTHONUNBUFFERED True

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app
COPY ./templates /code/templates
COPY ./static /code/static

CMD ["uvicorn", "app.main:app", "--host", "::", "--port", "8080"]
