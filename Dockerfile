# Этап Сборки
FROM python:3.10-slim AS builder

# Установка необходимых системных пакетов
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Установка рабочего каталога
WORKDIR /app

# Копирование и установка зависимостей
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir pyinstaller

# Копирование исходного кода приложения
COPY . .

# Создание исполняемого файла с помощью PyInstaller
RUN pyinstaller --onefile app.py

# Этап Выполнения
FROM python:3.10-slim

# Установка необходимых системных пакетов
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Установка рабочего каталога
WORKDIR /app

# Копирование исполняемого файла из этапа сборки
COPY --from=builder /app/dist/app /usr/local/bin/app

# Убедитесь, что исполняемый файл имеет права на выполнение
RUN chmod +x /usr/local/bin/app

# Открытие порта
EXPOSE 8000

# Команда для запуска приложения
CMD ["/usr/local/bin/app"]
