FROM python:3.11-slim

WORKDIR /app

COPY . /app
COPY main_billing.py /app
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main_billing.py"]
