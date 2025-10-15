# 🚀 Project Setup & Local Development Guide

This project uses **MongoDB, Redis, Docker, and AI model integration (Gemini recommended)**. Follow the instructions below to run it locally.

---

## ✅ Prerequisites

Make sure you have the following installed on your system:

| Requirement    | Version/Info        |
| -------------- | ------------------- |
| Docker         | Latest recommended  |
| Docker Compose | v2+                 |

---

## ⚙️ Environment Configuration

1. **Create your environment file**
   Copy the sample environment file:

   ```bash
   cp .env.example .env
   ```

2. **Update AI API keys inside `.env`**

   ```env
   # AI Provider Selection: The app checks API keys in this order: OPENAI → ANTHROPIC → GEMINI. Only GEMINI is tested, so use GEMINI for best results.
   OPENAI_API_KEY=<your_api_key>
   ANTHROPIC_API_KEY=<your_api_key>
   GEMINI_API_KEY=<your_gemini_api_key>
   ```

   ✅ **Important:** Use a **Gemini API Key** for reliable setup, as the project is currently tested with Gemini only.

---

## 🐳 Run with Docker

To build and start all services (backend, database, redis, celery and frontend):

```bash
docker-compose up --build -d
```

This will:

* Start MongoDB with your configured credentials
* Launch Redis cache
* Run celery
* Run the backend service
* Run the frontend app (Next.js)
* Attach everything to a Docker network

---

## 🌐 Access the App

Once Docker is up, open your browser and visit:

👉 **[http://localhost:3000](http://localhost:3000)**

The backend API should also be available at:

👉 **[http://localhost:8000](http://localhost:8000)**

---

## 🧪 Testing Connection

Verify MongoDB connection:

```bash
docker exec -it mongodb mongosh -u synchron -p synchron
```

Check Redis connection:

```bash
docker exec -it redis redis-cli ping
```

---

## 🛠 Development Tips

* Restart services if `.env` is updated:

  ```bash
  docker-compose down
  docker-compose up --build -d
  ```

* View logs:

  ```bash
  docker-compose logs -f
  ```

---

## ❗ Troubleshooting

| Issue                            | Solution                                                      |
| -------------------------------- | ------------------------------------------------------------- |
| Port 3000 or 8000 already in use | Close other apps or change ports in `docker-compose.yml`      |
| MongoDB auth failed              | Check `MONGO_URL`, `MONGO_INITDB_ROOT_USERNAME`, and password |
| AI API request errors            | Ensure a valid **Gemini** key is added to `.env`              |
| Can't access localhost           | Try `127.0.0.1:3000`                                          |

---

## ✅ Summary

| Task                               | Status |
| ---------------------------------- | ------ |
| Copy `.env.example` → `.env`       | ✅      |
| Add Gemini API key                 | ✅      |
| Run `docker-compose up --build -d` | ✅      |
| Visit `http://localhost:3000`      | ✅      |

