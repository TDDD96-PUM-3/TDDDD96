FROM python:3.12.6-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_ENV=development

CMD ["flask", "--app", "app:create_app", "run", "--debug", \
    "--host=0.0.0.0", "--port=8000"]