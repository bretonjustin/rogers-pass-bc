FROM tiangolo/uvicorn-gunicorn:python3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app
COPY ./templates /code/templates
COPY ./satic /code/sttic

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
