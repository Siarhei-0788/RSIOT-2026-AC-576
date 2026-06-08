import os
import time
import logging
import random
from flask import Flask, request, jsonify
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

# Конфигурация из переменных окружения
PORT = int(os.getenv('APP_PORT', 9062))
STU_ID = os.getenv('STU_ID', '230489')
STU_GROUP = os.getenv('STU_GROUP', 'AS-576')
STU_VARIANT = os.getenv('STU_VARIANT', '14')

# Префикс метрик по варианту (web14_)
PREFIX = "web14_"

# Метрики Prometheus
requests_total = Counter(f'{PREFIX}http_requests_total', 'Total HTTP requests', ['method', 'status'])
request_duration = Histogram(f'{PREFIX}http_request_duration_seconds', 'HTTP request duration', ['method'])
active_connections = Gauge(f'{PREFIX}active_connections', 'Active connections')
error_counter = Counter(f'{PREFIX}errors_total', 'Total errors', ['type'])

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.before_request
def before_request():
    request.start_time = time.time()
    active_connections.inc()

@app.after_request
def after_request(response):
    duration = time.time() - request.start_time
    request_duration.labels(method=request.method).observe(duration)
    requests_total.labels(method=request.method, status=response.status_code).inc()
    active_connections.dec()
    return response

@app.route('/healthz')
def health():
    return 'OK', 200

@app.route('/ready')
def ready():
    return 'READY', 200

@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

@app.route('/')
def index():
    logger.info(f"Request from {STU_ID}, variant {STU_VARIANT}")
    return jsonify({
        'status': 'ok',
        'student_id': STU_ID,
        'group': STU_GROUP,
        'variant': STU_VARIANT
    })

@app.route('/visit')
def visit():
    return jsonify({'visits': 1, 'student_id': STU_ID})

@app.route('/error')
def error():
    error_counter.labels(type='manual').inc()
    logger.error("Manual error triggered")
    return jsonify({'error': 'Internal Server Error'}), 500

@app.route('/random')
def random_status():
    statuses = [200, 200, 200, 200, 500]
    status = random.choice(statuses)
    if status == 500:
        error_counter.labels(type='random').inc()
    return jsonify({'status_code': status}), status

if __name__ == '__main__':
    logger.info(f"Student ID: {STU_ID}")
    logger.info(f"Group: {STU_GROUP}")
    logger.info(f"Variant: {STU_VARIANT}")
    logger.info(f"Starting server on port {PORT}")
    app.run(host='0.0.0.0', port=PORT)