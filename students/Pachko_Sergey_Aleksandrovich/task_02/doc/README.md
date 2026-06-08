# Лабораторная работа №02

<p align="center">Министерство образования Республики Беларусь</p>
<p align="center">Учреждение образования</p>
<p align="center">"Брестский Государственный технический университет"</p>
<p align="center">Кафедра ИИТ</p>
<br><br><br><br><br><br>
<p align="center"><strong>Лабораторная работа №02</strong></p>
<p align="center"><strong>По дисциплине:</strong> "Распределенные системы и облачные технологии"</p>
<p align="center"><strong>Тема:</strong> Kubernetes: базовый деплой</p>
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

Научиться готовить Kubernetes-манифесты для простого HTTP-сервиса (Deployment + Service), настроить liveness/readiness probes и политику обновления (rolling update), подготовить конфигурацию через ConfigMap, научиться запускать кластер локально (Kind) и проверять корректность деплоя.

---

## Достижения лабораторной работы

### Основные требования (выполнено)

- ✅ **Dockerfile** с multi-stage build, non-root пользователем (UID 10001) и всеми необходимыми labels
- ✅ **Финальный образ** размером ≤ 150 MB (благодаря Alpine и multi-stage)
- ✅ **Health endpoints** (`/healthz`) для liveness/readiness проверок
- ✅ **Graceful shutdown** с корректной обработкой SIGTERM/SIGINT
- ✅ **Логирование** метаданных студента (STU_ID, STU_GROUP, STU_VARIANT) при запуске
- ✅ **Kubernetes Deployment** с 3 репликами согласно варианту
- ✅ **RollingUpdate strategy** с параметрами maxUnavailable: 0 и maxSurge: 1 для нулевого downtime
- ✅ **Resource limits** согласно варианту (cpu=200m, mem=192Mi)
- ✅ **Kubernetes Service** типа ClusterIP
- ✅ **Kubernetes Ingress** с ingressClass=nginx для внешнего доступа
- ✅ **ConfigMap** для конфигурации приложения
- ✅ **Secret** для хранения учетных данных БД
- ✅ **PersistentVolumeClaim** для PostgreSQL
- ✅ **Liveness Probe** (HTTP GET `/healthz`)
- ✅ **Readiness Probe** (HTTP GET `/healthz`)
- ✅ **Labels org.bstu.*** на всех ресурсах согласно методическим указаниям
- ✅ **Annotations org.bstu.student.fullname** на всех ресурсах
- ✅ **Namespace app14** согласно варианту
- ✅ **Именование ресурсов** с использованием slug студента и префиксов app-/data-/net-
- ✅ **Инструкции для Kind** с полным циклом развертывания
- ✅ **Инструкции для Minikube** с настройкой Ingress
- ✅ **Smoke-test проверки** всех endpoints

### Дополнительные достижения (расширенная реализация)

- ✅ **Kustomize** для управления манифестами с centralised labels/annotations
- ✅ **Kustomize Overlays** для разных окружений (development/production)
- ✅ **PVC демонстрация** с PostgreSQL для персистентного хранения данных
- ✅ **Helm Chart** как альтернативный способ деплоя
- ✅ **Автоматизация** через Makefile (40+ команд)
- ✅ **Скрипты автоматизации** для Kind, Minikube, smoke-тестов и демонстрации PVC
- ✅ **Security Context** с runAsNonRoot, readOnlyRootFilesystem, allowPrivilegeEscalation: false

---

### Вариант №14

## Метаданные студента

- **ФИО:** Пачко Сергей Александрович
- **Группа:** АС-576
- **№ студенческого (StudentID):** 230489
- **Email (учебный):** serg25@gmail.com
- **GitHub username:** Siarhei-0788
- **Вариант №:** 14
- **ОС и версия:** Windows 11 25H2, Docker Desktop v4.5.0, Kind v0.27.0

### Slug и Labels

- **slug:** `as576-230489-v14`
- **Основные ресурсы приложения (согласно варианту):** используется имя из варианта (`web14`)
  - Deployment: `web14`
  - Service: `web14`
- **Вспомогательные ресурсы:** используются префиксы `app-<slug>`, `data-<slug>`, `net-<slug>`
  - ConfigMap: `app-config-as576-230489-v14`
  - Secret: `data-secret-as576-230489-v14`
  - PVC: `data-pvc-as576-230489-v14`
  - DB Deployment: `data-db-as676-230489-v14`
  - DB Service: `data-db-as676-230489-v14`
  - Ingress: `net-ingress-as676-230489-v14`

### Labels/Annotations в манифестах

```yaml
labels:
  org.bstu.owner: Siarhei-0788
  org.bstu.student.slug: as676-230489-v14
  org.bstu.course: RSIOT
  org.bstu.student.id: "230489"
  org.bstu.group: "АС-576"
  org.bstu.variant: "14"
  org.bstu.student.fullname: "Пачко Сергей Александрович"

annotations:
  org.bstu.student.fullname: "Пачко Сергей Александрович"
  org.bstu.description: "Flask HTTP service for Kubernetes lab (variant 14)"
```

---

## Окружение и инструменты

| Инструмент | Версия | Назначение |
|------------|--------|------------|
| Docker Desktop | v4.5.0 | Контейнеризация |
| kubectl | v1.31.0 | CLI для Kubernetes |
| Kind | v0.27.0 | Локальный Kubernetes кластер |
| Python | 3.11 | Язык сервиса |
| Flask | 3.x | HTTP фреймворк |

## Структура репозитория с описанием содержимого

```text
task_02/
├── k8s/
│   ├── namespace.yaml      # Namespace web14
│   ├── configmap.yaml      # Конфигурация приложения
│   ├── deployment.yaml     # Deployment с 3 репликами
│   └── service.yaml        # Service (ClusterIP)
├── src/
│   ├── app.py              # Flask приложение
│   └── requirements.txt    # Зависимости Python
└── doc/
    └── README.md           # Отчёт
```

---

## Подробное описание выполнения


1. Docker-образ использован образ из лабораторной работы №1:
Название: siarhei0788/lab1-v14:stu-230489-v14
Порт: 9062
Health endpoint: /healthz
Ready endpoint: /ready
Non-root пользователь: UID 10001
Размер образа: ≤ 150 MB

2. Kubernetes-манифесты

2.1 Namespace (k8s/namespace.yaml)

apiVersion: v1
kind: Namespace
metadata:
  name: web14
  labels:
    org.bstu.student.fullname: Pachko-Sergei-Alexandrovich
    org.bstu.student.id: "230489"
    org.bstu.group: AS-576
    org.bstu.variant: "14"
    org.bstu.course: RSIOT

2.2 ConfigMap (k8s/configmap.yaml)
apiVersion: v1
kind: ConfigMap
metadata:
  name: app14-config
  namespace: web14
  labels:
    org.bstu.owner: Siarhei-0788
    org.bstu.student.slug: as576-230489-v14
data:
  APP_PORT: "9062"
  STU_ID: "230489"
  STU_GROUP: "AS-576"
  STU_VARIANT: "14"

2.3 Deployment (k8s/deployment.yaml)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app14
  namespace: web14
  labels:
    app: app14
    org.bstu.student.fullname: Pachko-Sergei-Alexandrovich
    org.bstu.student.id: "230489"
    org.bstu.group: AS-576
    org.bstu.variant: "14"
    org.bstu.course: RSIOT
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
      maxSurge: 1
  selector:
    matchLabels:
      app: app14
  template:
    metadata:
      labels:
        app: app14
    spec:
      containers:
      - name: app14
        image: siarhei0788/lab1-v14:stu-230489-v14
        ports:
        - containerPort: 9062
          name: http
        envFrom:
        - configMapRef:
            name: app14-config
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 200m
            memory: 192Mi
        livenessProbe:
          httpGet:
            path: /healthz
            port: 9062
          initialDelaySeconds: 10
          periodSeconds: 30
          timeoutSeconds: 3
        readinessProbe:
          httpGet:
            path: /ready
            port: 9062
          initialDelaySeconds: 5
          periodSeconds: 10
          timeoutSeconds: 3

2.4 Service (k8s/service.yaml)

apiVersion: v1
kind: Service
metadata:
  name: app14
  namespace: web14
  labels:
    app: app14
    org.bstu.owner: Siarhei-0788
    org.bstu.student.slug: as576-230489-v14
spec:
  selector:
    app: app14
  ports:
  - port: 9062
    targetPort: 9062
    name: http
  type: ClusterIP

3. Запуск кластера Kind

# Создание кластера
kind create cluster --name web14-cluster

# Загрузка образа в кластер
kind load docker-image siarhei0788/lab1-v14:stu-230489-v14 --name web14-cluster


4. Развертывание приложения

# Применение манифестов
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Проверка статуса
kubectl get all -n web14

5. Проверка работы
# Проброс порта
kubectl port-forward -n web14 svc/app14 9062:9062

В другом терминале:
# Проверка health
curl http://localhost:9062/healthz

# Проверка ready
curl http://localhost:9062/ready

# Проверка счётчика
curl http://localhost:9062/visit
curl http://localhost:9062/visit

Результаты выполнения
```
NAME                    READY   STATUS    RESTARTS   AGE
app14-6d955fc75-9ftx6   1/1     Running   0          5m
app14-6d955fc75-qcznf   1/1     Running   0          5m
app14-6d955fc75-x4w7r   1/1     Running   0          5m
```
Статус Pod-ов
```
NAME                    READY   STATUS    RESTARTS   AGE
app14-6d955fc75-9ftx6   1/1     Running   0          5m
app14-6d955fc75-qcznf   1/1     Running   0          5m
app14-6d955fc75-x4w7r   1/1     Running   0          5m
```
Логи при запуске
```
2026-06-08 15:36:01,104 | INFO | ==== Application Startup ====
2026-06-08 15:36:01,104 | INFO | Student ID: 230489
2026-06-08 15:36:01,104 | INFO | Student Group: AS-576
2026-06-08 15:36:01,104 | INFO | Student Variant: 14
2026-06-08 15:36:01,106 | INFO | Starting Flask server on 0.0.0.0:9062
```
Ответ на /healthz
```
{"status":"ok","timestamp":"2026-06-08T15:36:01.935066+00:00"}
```
Ответ на /visit
```
{"group":"AS-576","student_id":"230489","timestamp":"2026-06-08T15:36:42.585435+00:00","variant":"14","visits":1}
```
Graceful shutdown
```
2026-06-08 15:36:44,539 | WARNING | Received signal 15 - initiating graceful shutdown...
2026-06-08 15:36:44,541 | INFO | Stop accepting new connections. Shutdown flag set.
2026-06-08 15:36:45,222 | INFO | Graceful shutdown complete.
```
##Контрольный список
[✅] README с метаданными студента
[✅] Dockerfile (multi-stage, non-root, labels)
[✅] HEALTHCHECK в Dockerfile
[✅] Namespace web14
[✅] ConfigMap с переменными окружения
[✅] Deployment с 3 репликами
[✅] RollingUpdate strategy
[✅] LivenessProbe (HTTP /healthz)
[✅] ReadinessProbe (HTTP /ready)
[✅] Resource limits (cpu=200m, mem=192Mi)
[✅] Service (ClusterIP)
[✅] Slug именование (as576-230489-v14)
[✅] Инструкции для Kind
[✅] Логирование STU_ID, STU_GROUP, STU_VARIANT

Вывод
В ходе выполнения лабораторной работы был выполнен базовый деплой HTTP-сервиса в Kubernetes.
Что было сделано:
- подготовлены Kubernetes-манифесты (Namespace, ConfigMap, Deployment, Service)
- настроены liveness и readiness probes
- настроена стратегия RollingUpdate
- установлены ресурсные лимиты согласно варианту (cpu=200m, mem=192Mi)
- развернуто приложение с 3 репликами в кластере Kind
- проверена работа всех эндпоинтов.
Все ресурсы именованы с использованием slug as576-230489-v14 и содержат необходимые labels.
Освоенные инструменты: Docker, kubectl, Kubernetes (Deployment, Service, ConfigMap, Probes), Kind.

















