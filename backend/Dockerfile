FROM selenium/standalone-chrome:latest

USER root
WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "universal_scraper.py"]