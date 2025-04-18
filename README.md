# Notification System and Transaction Reports

A scalable microservice architecture for multi-channel notifications and transaction reporting, fully containerized with Docker.

---

## 🚀 Features

### 1. Notification System
- **Multi‐channel delivery**  
  - SMS  
  - Email  
  - Telegram  
- **Templated messages with variable placeholders**  
- **Asynchronous processing with automatic retries**  
- **Full delivery status tracking** (Success, Pending, Failed)  

### 2. Transaction Reports
- **Time intervals**  
  - Daily  
  - Weekly  
  - Monthly  
- **Report types**  
  - Transaction count  
  - Total amount  
- **Optional** `merchantId` **filtering**  
- **Performance‐optimized with caching**  
- **Jalali (Persian) calendar support**  

---

## 🛠️ Technology Stack

- **Backend**  
  - Django  
  - Django REST Framework  
- **Database**  
  - MongoDB  
  - MongoEngine (ODM)  
- **Task Queue**  
  - Celery  
  - Redis (broker)  
- **Containerization**  
  - Docker  
  - Docker Compose  
  - Persistent volumes for database  

---

## 🏗️ Architecture (Docker Compose)

```yaml
version: '3.8'
services:
  web:
    build: .
    image: your-django-image
    ports:
      - "8000:8000"
    depends_on:
      - mongodb
      - redis

  mongodb:
    image: mongo:5.0
    volumes:
      - mongo_data:/data/db
    ports:
      - "27017:27017"

  redis:
    image: redis:6.2
    ports:
      - "6379:6379"

  celery:
    build: .
    image: your-celery-image
    depends_on:
      - redis
      - web

volumes:
  mongo_data:
```
## ⚡ Quick Start

```bash
git clone <repository-url>
cd <project-directory>
docker-compose up -d
docker-compose ps
```
## 📊 API Endpoints

1. **Notification API**

   ### Send Notification
   ```http
   POST /api/notifications/send/
   Content-Type: application/json
   ```
   ```json
   {
     "recipient_id": "user_id",
     "template_id": "template_id",
     "mediums": ["sms", "email", "telegram"]
   }
   ```

   ### Check Notification Status
   ```http
   GET /api/notifications/{notification_id}/status/
   ```

2. **Transaction Reports API**

   ### Generate On‑Demand Report
   ```http
   GET /reports/?type={count|amount}&mode={daily|weekly|monthly}&merchantId={optional}
   ```

   ### Get Cached Report
   ```http
   GET /reports/cached/?type={count|amount}&mode={daily|weekly|monthly}&merchantId={optional}
   ```

---

## 🧪 Testing & Sample Data

### Insert Test Data into MongoDB
```bash
docker exec -it proj-mongodb-1 mongosh zibal_db
```
```js
db.recipients.insertOne({
  user_id: "test_user",
  email: "test@example.com",
  phone: "09123456789",
  telegram_id: "test_telegram"
});

db.notification_templates.insertOne({
  name: "test_template",
  content: "This is a test message with amount {amount} Rial"
});
```

### Test with Postman

**Send Notification**  
```bash
POST http://localhost:8000/api/notifications/send/
```
Body:
```json
{
  "recipient_id": "test_user",
  "template_id": "your_template_id",
  "mediums": ["sms", "email"]
}
```

**Check Status**  
```bash
GET http://localhost:8000/api/notifications/{id}/status/
```

---

## 📁 Database Access

**MongoDB Shell**  
```bash
docker exec -it proj-mongodb-1 mongosh zibal_db
```

**DataGrip**  
```
Host: localhost  
Port: 27017  
Database: zibal_db
```

**MongoDB Compass**  
```bash
mongodb://localhost:27017/zibal_db
```

---

## 🔍 Monitoring & Logs

**Web service logs:**  
```bash
docker-compose logs -f web
```

**Celery worker logs:**  
```bash
docker-compose logs -f celery
```

---

## 🐳 Docker Services & Volumes

| Service  | Role                 | Port  | Volume       |
| -------- | -------------------- | ----- | ------------ |
| web      | Django application   | 8000  | ―            |
| mongodb  | MongoDB (persistent) | 27017 | `mongo_data` |
| redis    | Redis broker         | 6379  | ―            |
| celery   | Celery worker        | ―     | ―            |


