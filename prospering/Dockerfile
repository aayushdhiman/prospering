FROM python:3.11-slim

WORKDIR /prospering

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "driver.py"]
