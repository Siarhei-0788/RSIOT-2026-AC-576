FROM python:3.11-alpine
WORKDIR /app
COPY src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ .
EXPOSE 9062
HEALTHCHECK --interval=30s --timeout=3s CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:9062/healthz')" || exit 1
USER 10001
ENTRYPOINT ["python", "app.py"]