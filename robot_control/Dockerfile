FROM python:3.11
WORKDIR /app
COPY . /app
RUN pip install flask
CMD ["python", "app.py"]

RUN apt-get update && apt-get install -y sqlite3
