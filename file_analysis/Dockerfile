FROM python:3.11-slim

WORKDIR /srv
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

COPY file_analysis/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY file_analysis/app app
COPY config config

EXPOSE 8001
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
