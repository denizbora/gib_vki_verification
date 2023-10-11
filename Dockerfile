FROM python:3.8
WORKDIR /app
EXPOSE 8080
COPY requirements.txt requirements.txt
RUN python -m pip install --upgrade pip

RUN pip install -r requirements.txt

COPY static/ static/
COPY www/ www/
COPY app.py app.py


CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]