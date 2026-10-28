@echo off
echo ========================================
echo   Магазин спортивного питания
echo   Запуск бэкенда и фронтенда...
echo ========================================

echo [1/2] Запуск Flask бэкенда (порт 5000)...
start cmd /k "cd /d C:\Users\ASUS\Downloads\Emir_new\sports-shop-frontend\backend && venv\Scripts\activate && python app.py"

timeout /t 2 /nobreak >nul

echo [2/2] Запуск Vue фронтенда (порт 5173)...
start cmd /k "cd /d C:\Users\ASUS\Downloads\Emir_new\sports-shop-frontend && npm run dev"

echo Готово! Оба сервера запущены.
echo Бэкенд: http://localhost:5000
echo Фронтенд: http://localhost:5173
echo Закройте окна командной строки для остановки.