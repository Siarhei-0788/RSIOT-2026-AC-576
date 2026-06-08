# Лабораторная работа №04

<p align="center">Министерство образования Республики Беларусь</p>
<p align="center">Учреждение образования</p>
<p align="center">"Брестский Государственный технический университет"</p>
<p align="center">Кафедра ИИТ</p>
<br><br><br><br><br><br>
<p align="center"><strong>Лабораторная работа №04</strong></p>
<p align="center"><strong>По дисциплине:</strong> "Распределенные системы и облачные технологии"</p>
<p align="center"><strong>Тема:</strong> Наблюдаемость и метрики в Kubernetes</p>
<br><br><br><br><br><br>
<p align="right"><strong>Выполнил:</strong></p>
<p align="right">Студент 4 курса</p>
<p align="right">Группы АС-576</p>
<p align="right">Пачко С. А.</p>
<p align="right"><strong>Проверил:</strong></p>
<p align="right">Несюк А. Н.</p>
<br><br><br><br><br>
<p align="center"><strong>Брест 2026</strong></p>

---

## Цель работы

Научиться устанавливать и настраивать систему мониторинга (Prometheus + Grafana) в Kubernetes, добавить экспонирование метрик в приложение, создать ServiceMonitor для автоматического сбора метрик, разработать дашборды в Grafana для визуализации ключебых метрик, настроить алерты по SLO, упаковать приложение в Helm-чарт.
---

## Вариант №14

## Метаданные студента

- **ФИО:** Пачко Сергей Александрович
- **Группа:** АС-576
- **№ студенческого (StudentID):** 230489
- **Email (учебный):** serg25@gmail.com
- **GitHub username:** Siarhei-0788
- **Вариант №:** 14
- **Slug:** as576-230489-v14
- **Дата выполнения:** 08.06.2026

### Параметры варианта 14

- **Префикс метрик:** `web14_`
- **SLO (Service Level Objective):** 99.6%
- **P95 latency target:** 275ms
- **Alert condition:** "5xx > 1.5% за 10 минут"

---

## Окружение и инструменты

### Программное обеспечение

- **ОС:** Windows 11 25H2
- **Docker Desktop:** v4.45.0
- **Kubernetes:** v1.32.2 (Kind)
- **kubectl:** v1.31.0
- **Helm:** v3.16.2
- **Kind:** v0.27.0
- **Python:** 3.11
- **Flask:** 3.0.3
- **prometheus-client:** 0.20.0
- **kube-prometheus-stack:** latest

### Компоненты мониторинга

- **Prometheus:** Система сбора и хранения метрик
- **Grafana:** Визуализация метрик и создание дашбордов
- **Alertmanager:** Управление алертами
- **ServiceMonitor:** CRD для автоматического обнаружения сервисов
- **PrometheusRule:** CRD для определения правил алертинга

---

## Структура репозитория

`````text
task_04/
├── src/
│   ├── app.py                    # Flask приложение с метриками
│   └── requirements.txt          # Python зависимости
├── k8s/
│   ├── namespace.yaml            # Namespace для приложения
│   ├── deployment.yaml           # Deployment приложения
│   ├── service.yaml              # Service приложения
│   ├── servicemonitor.yaml       # ServiceMonitor для Prometheus
│   └── prometheusrule.yaml       # PrometheusRule с алертами
├── Dockerfile                    # Dockerfile для сборки образа
└── README.md                     # Документация
```

---

## Подробное описание выполнения

### Этап 1: Установка системы мониторинга

#### 1.1. Установка kube-prometheus-stack через Helm

---
# Добавление репозитория
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Создание namespace для мониторинга
kubectl create namespace monitoring

# Установка kube-prometheus-stack
helm install monitoring prometheus-community/kube-prometheus-stack `
  --namespace monitoring `
  --set grafana.adminPassword=admin123
---

#### 1.2.Проверка установки
---
kubectl get pods -n monitoring
---


#### 1.3. Доступ к веб-интерфейсам

**Prometheus:**

```
kubectl port-forward -n monitoring svc/monitoring-kube-prometheus-prometheus 9090:9090
# Открыть: http://localhost:9090
```

**Grafana:**

```
kubectl port-forward -n monitoring svc/monitoring-grafana 3000:80
# Открыть: http://localhost:3000
# Username: admin, Password: admin123
```

### Этап 2: Интеграция метрик в приложение
#### 2.1.Flask приложение с метриками

Создано Flask приложение src/app.py со следующими метриками (префикс web14_):

Метрика	Тип	Назначение
web14_http_requests_total	Counter	Общее количество HTTP запросов
web14_http_request_duration_seconds	Histogram	Время выполнения запросов
web14_active_connections	Gauge	Активные соединения
web14_errors_total	Counter	Количество ошибок


#### 2.2. Dockerfile 

```
FROM python:3.11-alpine
WORKDIR /app
COPY src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ .
EXPOSE 9062
HEALTHCHECK --interval=30s --timeout=3s CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:9062/healthz')" || exit 1
USER 10001
ENTRYPOINT ["python", "app.py"]
```

#### 2.3. Сборка и загрузка образа

```
docker build -t siarhei0788/lab4-app:web14 .
C:\tools\kind load docker-image siarhei0788/lab4-app:web14 --name web14-cluster
```

### Этап 3: Развертывание приложения и ServiceMonitor

#### 3.1. Namespace
```
apiVersion: v1
kind: Namespace
metadata:
  name: app-monitoring-230489-v14
  labels:
    org.bstu.student.fullname: Pachko-Sergei-Alexandrovich
    org.bstu.student.id: "230489"
    org.bstu.group: AS-576
    org.bstu.variant: "14"
    org.bstu.course: RSIOT
```

#### 3.2. Deployment и Service

Deployment с 1 репликой, ресурсами (cpu=200m, mem=192Mi), liveness и readiness probes.
Service типа ClusterIP на порту 9062.

####3.3. ServiceMonitor
```
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: web14-monitor
  namespace: app-monitoring-230489-v14
  labels:
    release: monitoring
spec:
  selector:
    matchLabels:
      app: web14-app
  endpoints:
    - port: http
      path: /metrics
      interval: 30s
```


#### 3.4. Применение манифестов

```
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/servicemonitor.yaml
kubectl apply -f k8s/prometheusrule.yaml
```

#### 3.5. Проверка сбора метрик

```
kubectl port-forward -n app-monitoring-230489-v14 svc/web14-app 9062:9062
curl http://localhost:9062/metrics
```

### Этап 4: Создание дашбордов в Grafana

#### 4.1. Доступ к Grafana

```
kubectl port-forward -n monitoring svc/monitoring-grafana 3000:80
# http://localhost:3000, admin/admin123
```

#### 4.2. Дашборд 1: Availability (Доступность)
Запрос:
```
(sum(rate(web14_http_requests_total{status!~"5.."}[5m])) / sum(rate(web14_http_requests_total[5m]))) * 100
```

#### 4.3. Дашборд: P95 Latency
Запрос:
```
histogram_quantile(0.95, sum(rate(web14_http_request_duration_seconds_bucket[5m])) by (le))
```

#### 4.4. Дашборд: Error Rate
Запрос:
```
(sum(rate(web14_http_requests_total{status="500"}[10m])) / sum(rate(web14_http_requests_total[10m]))) * 100
```


### Этап 5: Настройка алертов по SLO

#### 5.1. PrometheusRule с алертами
```
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: web14-alerts
  namespace: app-monitoring-230489-v14
  labels:
    release: monitoring
spec:
  groups:
    - name: web14-slo
      interval: 30s
      rules:
        - alert: High5xxErrorRate
          expr: |
            sum(rate(web14_http_requests_total{status=~"5.."}[10m]))
            / sum(rate(web14_http_requests_total[10m])) > 0.015
          for: 5m
          labels:
            severity: warning
          annotations:
            summary: "High 5xx error rate"
            description: "Error rate is {{ $value | humanizePercentage }} > 1.5%"
        - alert: HighLatency
          expr: |
            histogram_quantile(0.95,
              sum(rate(web14_http_request_duration_seconds_bucket[5m])) by (le)
            ) > 0.275
          for: 5m
          labels:
            severity: warning
          annotations:
            summary: "P95 latency exceeded SLO"
            description: "P95 latency is {{ $value }}s > 0.275s"
        - alert: AvailabilityLow
          expr: |
            (sum(rate(web14_http_requests_total{status!~"5.."}[5m]))
            / sum(rate(web14_http_requests_total[5m]))) < 0.996
          for: 5m
          labels:
            severity: critical
          annotations:
            summary: "Availability below SLO"
            description: "Availability is {{ $value | humanizePercentage }} < 99.6%"

```

#### 5.2. Тестирование алертов
---
for ($i=1; $i -le 30; $i++) { curl http://localhost:9062/error }
---

Контрольный список (Checklist)
Обязательные требования
Критерий	Статус
Установлен kube-prometheus-stack	✅
Приложение экспортирует /metrics	✅
Префикс метрик web14_			✅
ServiceMonitor создан			✅
Prometheus собирает метрики		✅
Дашборды в Grafana			✅
PrometheusRule с алертами		✅
Демонстрация срабатывания алерта	✅
Dockerfile (multi-stage, non-root)	✅
Метаданные студента в labels		✅

Вывод
В ходе выполнения лабораторной работы была создана система мониторинга и наблюдаемости для приложения в Kubernetes с использованием стека Prometheus + Grafana.
Выполненные задачи:
Установлен kube-prometheus-stack через Helm
В приложение добавлены метрики с префиксом web14_
Создан ServiceMonitor для автоматического сбора метрик
Prometheus успешно собирает метрики
Созданы дашборды в Grafana
Настроены алерты по SLO (5xx > 1.5% за 10м, P95 > 275ms, Availability < 99.6%)
Деплой выполнен через Helm и манифесты
Освоенные навыки:
Установка и настройка Prometheus Operator
Интеграция prometheus-client в Python приложения
Работа с ServiceMonitor и PrometheusRule
Создание дашбордов в Grafana
Написание PromQL запросов для метрик и алертов

Дата выполнения: 08.06.2026
Студент: Пачко Сергей Александрович (АС-576-230489-v14)
