FROM python:3.8-slim

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

RUN pip install python-dotenv

EXPOSE 5000

COPY . /app

CMD ["python", "app.py"]
