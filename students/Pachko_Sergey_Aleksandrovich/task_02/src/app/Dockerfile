# ---- Builder stage ----
FROM python:3.11-alpine AS builder

ARG PIP_NO_CACHE_DIR=1
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apk add --no-cache build-base=0.5-r3

WORKDIR /app

COPY requirements.txt ./
# --no-cache-dir для pip исключает кэш, сокращая размер промежуточного слоя
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---- Final stage ----
FROM python:3.11-alpine AS final

LABEL org.bstu.student.fullname="Логинов Глеб Олегович" \
      org.bstu.student.id="220018" \
      org.bstu.group="АС-63" \
      org.bstu.variant="14" \
      org.bstu.course="RSIOT" \
      org.bstu.owner="gleb7499" \
      org.bstu.student.slug="as63-220018-v14"

ENV STU_ID=220018 \
    STU_GROUP=АС-63 \
    STU_VARIANT=14 \
    APP_PORT=8062 \
    APP_HOST=0.0.0.0 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Создание non-root пользователя для безопасности
RUN adduser -D -u 10001 appuser

WORKDIR /app

# Копирование установленных зависимостей из builder stage
COPY --from=builder /install /usr/local

# Копирование исходного кода приложения
COPY src/app.py ./

EXPOSE 8062

# Установка wget для healthcheck
RUN apk add --no-cache wget=1.25.0-r1 \
    && echo 'hosts: files dns' > /etc/nsswitch.conf

# Health endpoint для liveness/readiness проверок
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --no-hsts -qO- http://127.0.0.1:${APP_PORT}/healthz || exit 1

# Запуск от non-root пользователя (UID 10001)
USER 10001

ENTRYPOINT ["python", "app.py"]
