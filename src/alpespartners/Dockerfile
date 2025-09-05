FROM python:3.12

ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
WORKDIR /app

COPY ../requirements.txt /app/requirements.txt
RUN pip install --upgrade --no-cache-dir "pip<24.1" setuptools wheel \
 && pip install --no-cache-dir -r /app/requirements.txt


COPY ./src /app/
ENV PYTHONPATH=/app

EXPOSE 5000
CMD ["flask", "--app", "alpespartners.api:create_app", "run", "--host=0.0.0.0", "--port=5000"]
