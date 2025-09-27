#!/usr/bin/env python3
"""
Запуск приложения управления снабжением
"""

from app_new import create_app

if __name__ == '__main__':
    app = create_app('development')
    print("🚀 Запуск системы управления снабжением...")
    print("📱 Откройте браузер: http://localhost:5000")
    print("📚 API документация: http://localhost:5000/api/v1/health")
    print("❌ Для выхода нажмите Ctrl+C")

    app.run(host='0.0.0.0', port=5000, debug=True)
