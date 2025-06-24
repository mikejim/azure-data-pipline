FROM python:3.10-slim

WORKDIR /app

COPY generator.py .

RUN pip install azure-eventhub faker

CMD ["python", "generator.py"]
