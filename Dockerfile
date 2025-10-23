FROM python:3.11-slim
WORKDIR /app
COPY mac_subscriber.py .
# Pin to paho-mqtt 1.x to avoid the v2 callback API change
RUN pip install --no-cache-dir paho-mqtt==1.6.1
ENV PYTHONUNBUFFERED=1
CMD ["python", "mac_subscriber.py"]