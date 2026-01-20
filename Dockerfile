# 🎰 NFTY ULTRA PRO - Dockerfile
# תצורת Docker מתקדמת עם ביצועים גבוהים

FROM python:3.11-slim-bullseye as builder

# התקנת דרישות מערכת
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libjpeg-dev \
    zlib1g-dev \
    libpq-dev \
    curl \
    gnupg \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# יצירת סביבה וירטואלית
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# העתקת קבצי הפרויקט
WORKDIR /app
COPY requirements.txt .
COPY requirements_prod.txt .

# התקנת חבילות Python
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# שלב ריצה
FROM python:3.11-slim-bullseye

# התקנת דרישות מערכת לקרונולוגיה
RUN apt-get update && apt-get install -y \
    libjpeg62-turbo \
    zlib1g \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# העתקת הסביבה הוירטואלית
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# יצירת משתמש לא-רוט
RUN groupadd -r nifty && useradd -r -g nifty -m -d /app nifty
USER nifty

# העתקת קבצי האפליקציה
WORKDIR /app
COPY --chown=nifty:nifty . .

# משתני סביבה
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PATH="/opt/venv/bin:$PATH"

# אתחול
RUN mkdir -p /app/logs /app/data /app/exports

# יצירת volume
VOLUME ["/app/logs", "/app/data", "/app/exports"]

# חשיפת פורטים
EXPOSE 8080 9090

# נקודת כניסה
ENTRYPOINT ["python", "Main.py"]
