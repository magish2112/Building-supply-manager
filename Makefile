# Makefile для системы управления снабжением

.PHONY: help install run test clean lint format docker-build docker-run deploy

# По умолчанию показываем помощь
help:
	@echo "🚀 Система управления снабжением - команды Makefile"
	@echo ""
	@echo "📦 Основные команды:"
	@echo "  install     - Установка зависимостей"
	@echo "  run         - Запуск приложения в режиме разработки"
	@echo "  test        - Запуск тестов"
	@echo "  lint        - Проверка кода линтерами"
	@echo "  format      - Форматирование кода"
	@echo "  clean       - Очистка временных файлов"
	@echo ""
	@echo "🐳 Docker команды:"
	@echo "  docker-build - Сборка Docker образа"
	@echo "  docker-run   - Запуск в Docker контейнере"
	@echo ""
	@echo "🚀 Развертывание:"
	@echo "  deploy       - Развертывание на Heroku"
	@echo ""

# Установка зависимостей
install:
	@echo "📦 Установка зависимостей..."
	pip install -r requirements.txt

# Запуск приложения
run:
	@echo "🚀 Запуск приложения..."
	python run.py

# Запуск тестов
test:
	@echo "🧪 Запуск тестов..."
	python -m pytest tests/ -v

# Проверка кода
lint:
	@echo "🔍 Проверка кода линтерами..."
	flake8 app_new.py controllers/ models/ services/ --max-line-length=100
	mypy app_new.py controllers/ models/ services/ --ignore-missing-imports
	bandit -r app_new.py controllers/ models/ services/ -f txt

# Форматирование кода
format:
	@echo "🎨 Форматирование кода..."
	black app_new.py controllers/ models/ services/ tests/ --line-length=100
	isort app_new.py controllers/ models/ services/ tests/

# Очистка
clean:
	@echo "🧹 Очистка временных файлов..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.log" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "htmlcov" -exec rm -rf {} +
	rm -rf instance/supply_tracker.db

# Сборка Docker образа
docker-build:
	@echo "🐳 Сборка Docker образа..."
	docker build -t building-supply-manager .

# Запуск в Docker
docker-run:
	@echo "🐳 Запуск в Docker контейнере..."
	docker run -p 5000:5000 building-supply-manager

# Развертывание на Heroku
deploy:
	@echo "🚀 Развертывание на Heroku..."
	@if [ -z "$(HEROKU_APP)" ]; then \
		echo "❌ Укажите HEROKU_APP=name в переменных окружения"; \
		exit 1; \
	fi
	heroku create $(HEROKU_APP) || echo "Приложение уже существует"
	git push heroku master
	heroku open

# Полная установка и запуск
setup: install
	@echo "✅ Проект настроен! Запустите 'make run' для запуска приложения"

# CI/CD пайплайн
ci: lint test
	@echo "✅ CI/CD проверки пройдены!"

# Разработка
dev: format lint test
	@echo "✅ Код готов к коммиту!"
