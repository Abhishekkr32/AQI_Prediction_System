FROM maven:3.9.4-eclipse-temurin-17 AS builder

RUN apt-get update && apt-get install -y python3 python3-pip python3-pytest

WORKDIR /app

COPY . .

RUN mvn clean package -B

FROM python:3.10-slim

WORKDIR /app

COPY --from=builder /app .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["python3", "app.py"]