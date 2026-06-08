# Лабораторная работа 03: Kubernetes - состояние и хранение

<p align="center">Министерство образования Республики Беларусь</p>
<p align="center">Учреждение образования</p>
<p align="center">"Брестский Государственный технический университет"</p>
<p align="center">Кафедра ИИТ</p>
<br><br><br><br><br><br>
<p align="center"><strong>Лабораторная работа №03</strong></p>
<p align="center"><strong>По дисциплине:</strong> "Распределенные системы и облачные технологии"</p>
<p align="center"><strong>Тема:</strong> Kubernetes: состояние и хранение (StatefulSet)</p>
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

Изучить механизмы управления состоянием и хранением данных в Kubernetes. Развернуть StatefulSet с Redis, настроить постоянное хранилище (PersistentVolume/PersistentVolumeClaim), реализовать автоматическое резервное копирование через CronJob и восстановление данных через Job.

---

## Метаданные студента

- **ФИО:** Пачко Сергей Александрович
- **Группа:** АС-576
- **№ студенческого (StudentID):** 230489
- **Email (учебный):** serg25@gmail.com
- **GitHub username:** Siarhei-0788
- **Вариант №:** 14
- **ОС и версия:** Windows 11 25H2
- **Дата выполнения:** 08.06.2026
- **Slug:** as576-230489-v14

---

## Параметры варианта 14

- **База данных:** Redis
- **Размер PVC:** 5Gi
- **StorageClass:** standard (default)
- **Расписание backup:** `*/30 * * * *` (каждые 30 минут)

---

## Технологический стек

- **ОС:** Windows 11 25H2
- **Docker Desktop:** v4.45.0
- **kubectl:** v1.31.0
- **Kind:** v0.27.0
- **Redis:** 7-alpine

---

## Архитектура решения

### Схема компонентов (с S3-хранилищем)

```
┌┌──────────────────────────────────────────────────────────────────────────┐
│ Namespace: state-230489-v14 │
│ │
│ ┌──────────────┐ ┌─────────────────────────────┐ │
│ │ Secret │────────>│ StatefulSet │ │
│ │ (password) │ │ redis │ │
│ └──────────────┘ │ │ │
│ │ ┌─────────────────────┐ │ │
│ ┌──────────────┐ │ │ Pod: redis-0 │ │ │
│ │ Headless │────────>│ │ ┌─────────────┐ │ │ │
│ │ Service │ │ │ │ Redis 7 │ │ │ │
│ │ (DNS) │ │ │ │ Port: 6379 │ │ │ │
│ └──────────────┘ │ │ └─────────────┘ │ │ │
│ │ │ │ │ │ │
│ ┌──────────────┐ │ │ v │ │ │
│ │ StorageClass │ │ │ ┌────────┐ │ │ │
│ │ standard │────────>│ │ │ Volume │ │ │ │
│ └──────────────┘ │ │ │ 5Gi │ │ │ │
│ │ │ └────────┘ │ │ │
│ │ └─────────────────────┘ │ │
│ └─────────────────────────────┘ │
│ │
│ ┌──────────────────────────────────────────────────────────────────┐ │
│ │ Backup System │ │
│ │ ┌──────────────┐ ┌──────────────────────┐ │ │
│ │ │ CronJob │──────>│ Redis SAVE │ │ │
│ │ │ */30 * * * * │ │ (dump.rdb) │ │ │
│ │ └──────────────┘ └──────────────────────┘ │ │
│ │ │ │
│ │ ┌──────────────┐ │ │
│ │ │ Job Restore │────────────────────────────────────────────────┘ │
│ │ └──────────────┘ │
│ └──────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────┘
```

### Компоненты системы

1. **Namespace** - изолированное пространство имен `state-230489-v14`
2. **StatefulSet** - управление Redis инстансом с гарантированным постоянным хранилищем
3. **Headless Service** - стабильные DNS-имена для подов StatefulSet
4. **PersistentVolumeClaim** - постоянное хранение данных Redis (5Gi)
5. **StorageClass** - динамическое провизионирование томов (standard)
6. **Secret** - безопасное хранение пароля Redis
7. **CronJob** - автоматическое резервное копирование каждые 30 минут
8. **Job** - восстановление данных из резервной копии

---

## Структура репозитория

```
task_03/
├── k8s/
│ ├── namespace.yaml
│ ├── secret.yaml
│ ├── headless-service.yaml
│ ├── statefulset.yaml
│ ├── cronjob-backup.yaml
│ └── job-restore.yaml
└── README.md```

---

## Подробное описание выполнения

### Шаг 1: Подготовка окружения

#### 1.1. Запуск Kubernetes кластера (Kind)

```powershell
# Создание кластера
kind create cluster --name state-cluster

# Проверка доступности кластера
kubectl cluster-info
kubectl get nodes
```

### Шаг 2: Развертывание базовой инфраструктуры

#### 2.1. Создание Namespace

```
kubectl apply -f k8s/namespace.yaml
kubectl get ns state-230489-v14
```

#### 2.2. Создание Secret с паролем Redis

```
kubectl apply -f k8s/secret.yaml
kubectl get secret -n state-230489-v14
```

Пароль Redis: password123 (в base64: cGFzc3dvcmQxMjM=)

#### 2.3. Создание Headless Service

```
kubectl apply -f k8s/headless-service.yaml
kubectl get svc -n state-230489-v14
```

### Шаг 3: Развертывание StatefulSet с Redis

#### 3.1. Применение манифеста StatefulSet

```
kubectl apply -f k8s/statefulset.yaml
```

#### 3.2. Ожидание готовности

```bash
kubectl get pods -n state-230489-v14 -w
```

#### 3.3. Проверка развертывания

```
# Проверить StatefulSet
kubectl get sts -n state-230489-v14

# Проверить поды
kubectl get pods -n state-230489-v14 -o wide

# Проверить PVC
kubectl get pvc -n state-230489-v14
```

Результат:
NAME                 STATUS   VOLUME   CAPACITY   ACCESS MODES   STORAGECLASS
redis-data-redis-0   Bound    pvc-xxx  5Gi        RWO            standard

NAME      READY   STATUS    RESTARTS   AGE
redis-0   1/1     Running   0          21s


### Шаг 4: Тестирование сохранности данных

#### 4.1. Создание тестовых данных

```
kubectl exec -it redis-0 -n state-230489-v14 -- redis-cli -a password123
```

В Redis CLI выполнить:

```redis
SET test_key "Hello from Lab3"
SET student_id "230489"
SET variant "14"
SAVE
exit
```

#### 4.2.Проверка созданных данных
```
kubectl exec redis-0 -n state-230489-v14 -- sh -c "redis-cli -a password123 GET test_key"
```
Ответ: "Hello from Lab3"


#### 4.3. Удаление пода для проверки персистентности

```
# Удалить под
kubectl delete pod redis-0 -n state-230489-v14

# Дождаться пересоздания
kubectl get pods -n state-230489-v14 -w
```

#### 4.4. Проверка данных после перезапуска

```
kubectl exec redis-0 -n state-230489-v14 -- sh -c "redis-cli -a password123 GET test_key"
```
Результат: "Hello from Lab3" — данные сохранились! 

### Шаг 5: Настройка автоматического резервного копирования

#### 5.1. Создание CronJob

```
kubectl apply -f k8s/cronjob-backup.yaml
kubectl get cronjob -n state-230489-v14
```
Результат:
NAME           SCHEDULE       SUSPEND   ACTIVE   LAST SCHEDULE
redis-backup   */30 * * * *   False     0        23s

#### 5.2. Ручной запуск backup для тестирования

```
kubectl create job --from=cronjob/redis-backup backup-manual -n state-230489-v14
kubectl get jobs -n state-230489-v14
kubectl logs -l app=redis-backup -n state-230489-v14 --tail=20
```

### Шаг 6: Тестирование восстановления данных

#### 6.1. Удаление данных (симуляция потери)

```
kubectl exec -it redis-0 -n state-230489-v14 -- redis-cli -a password123 FLUSHALL
kubectl exec redis-0 -n state-230489-v14 -- sh -c "redis-cli -a password123 GET test_key"
```
Ответ: (nil)

#### 6.2. Запуск Job восстановления

```
kubectl apply -f k8s/job-restore.yaml
kubectl get jobs -n state-230489-v14
kubectl logs -l app=redis-restore -n state-230489-v14 --tail=20
```

#### 6.3. Проверка восстановленных данных

```
kubectl exec redis-0 -n state-230489-v14 -- sh -c "redis-cli -a password123 GET test_key"
```
Результат: "Hello from Lab3" — данные восстановлены!

## Результаты тестирования

### Таблица 1: Сохранность данных после перезапуска пода

Ключ	        Значение до	Значение после	 Статус
test_key	Hello from Lab3	Hello from Lab3	 ✅
student_id	230489	        230489	         ✅
variant	        14	        14	         ✅

### Таблица 2: Параметры системы резервного копирования

Параметр	        Значение
Расписание CronJob	*/30 * * * * (каждые 30 минут)
Политика конкурентности	Forbid
Команда backup	        redis-cli SAVE

### Таблица 3: Параметры восстановления данных

Метрика	                   Значение
Способ восстановления	   FLUSHALL + загрузка dump.rdb
Успешность восстановления  Успешно ✅
---
Контрольный список выполнения
Структура проекта
- Создана директория task_03/
- Создана поддиректория k8s/ с манифестами
- Создан README.md с документацией

Kubernetes манифесты
- namespace.yaml с правильными лейблами
- secret.yaml с паролем Redis
- headless-service.yaml (clusterIP: None)
- statefulset.yaml с volumeClaimTemplates (5Gi)
- cronjob-backup.yaml (расписание */30 * * * *)
- job-restore.yaml

Именование и лейблы
- Namespace: state-230489-v14
- Все ресурсы содержат обязательные лейблы:
org.bstu.student.fullname
org.bstu.student.id
org.bstu.group
org.bstu.variant
org.bstu.course
org.bstu.owner
org.bstu.student.slug

Функциональность
- StatefulSet развертывается и работает
- PVC создается и привязывается (5Gi)
- Данные сохраняются после удаления пода
- CronJob создает backup каждые 30 минут
- Job восстанавливает данные из backup
- README.md оформлен по шаблону

Выводы
Достигнутые результаты
StatefulSet успешно развернут
- Redis 7-alpine запущен и работает стабильно
- Настроены Liveness и Readiness probes

Постоянное хранилище работает корректно
- PersistentVolume динамически провизионируется через StorageClass
- Данные сохраняются после удаления и пересоздания пода (PVC 5Gi)

Headless Service настроен
- Стабильные DNS-имена для подов StatefulSet

Резервное копирование автоматизировано 
- CronJob создает backup каждые 30 минут по расписанию

Восстановление данных работает
- Job успешно восстанавливает данные из последнего backup

Все обязательные лейблы применены
- Каждый ресурс содержит метаданные студента

Освоенные навыки
Управление состоянием в Kubernetes:
- Работа со StatefulSet для stateful-приложений
- Понимание различий между StatefulSet и Deployment

Постоянное хранилище:
- Настройка PersistentVolumeClaim
- Динамическое провизионирование через StorageClass
- VolumeClaimTemplates в StatefulSet

Сетевая идентичность:
- Headless Service для стабильных DNS-имён

Резервное копирование и восстановление:
- Автоматизация backup через CronJob
- Создание Job для восстановления данных

Безопасность:
- Использование Secret для хранения паролей

Полезные команды
powershell
# Просмотр всех ресурсов в namespace
kubectl get all,pvc,secret -n state-230489-v14

# Логи Redis
kubectl logs -f -n state-230489-v14 redis-0

# Подключение к Redis CLI
kubectl exec -it -n state-230489-v14 redis-0 -- redis-cli -a password123

# Проверка состояния backup
kubectl get cronjob,job -n state-230489-v14

# Описание StatefulSet
kubectl describe sts redis -n state-230489-v14

# События в namespace
kubectl get events -n state-230489-v14 --sort-by='.lastTimestamp'

# Получение пароля Redis
kubectl get secret redis-secret -n state-230489-v14 -o jsonpath='{.data.redis-password}' | base64 -d
Дата сдачи: 08.06.2026
Выполнил: Пачко Сергей Александрович, АС-576, 230489
Вариант: 14 (Redis, 5Gi, standard, */30 * * * *)
GitHub: https://github.com/Siarhei-0788/task_03
Email: serg25@gmail.com
