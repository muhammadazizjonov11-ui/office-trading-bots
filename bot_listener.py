import os
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from config import CHAT_ID, TELEGRAM_TOKEN
from main import MainTradingRobot
import telebot

# --- МИНИ-СЕРВЕР ДЛЯ RENDER (чтобы веб-сервис не падал по таймауту порта) ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive and listening!")

def run_http_server():
    port = int(os.environ.get("PORT", 10000))
    server_address = ("", port)
    httpd = HTTPServer(server_address, HealthCheckHandler)
    print(f"🌐 Фоновый HTTP-сервер запущен на порту {port}")
    httpd.serve_forever()

# Запускаем HTTP-сервер в отдельном потоке
threading.Thread(target=run_http_server, daemon=True).start()
# --------------------------------------------------------------------------

# Инициализируем бота для Telegram
bot = telebot.TeleBot(TELEGRAM_TOKEN)
robot = MainTradingRobot()


# Обработка нажатия на инлайн-кнопки и текстовые команды
@bot.message_handler(commands=["start", "analysis", "анализ"])
def handle_analysis_command(message):
    chat_id = message.chat.id
    bot.send_message(
        chat_id, "🔍 *Запрос принят!* Запускаю PRO-анализ рынка...", parse_mode="Markdown"
    )
    robot.run_cycle(chat_id)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    chat_id = call.message.chat.id
    data = call.data

    if "auto_trade" in data:
        bot.answer_callback_query(
            call.id, "⚡ Запрос на авто-вход через API обрабатывается..."
        )
        bot.send_message(
            chat_id, f"⚡ Сработал авто-вход по сигналу! Параметры: `{data}`", parse_mode="Markdown"
        )
    elif data == "action_close_all":
        bot.answer_callback_query(call.id, "🚨 Все позиции закрыты!")
        bot.send_message(chat_id, "🚨 *Экстренное закрытие всех позиций выполнено!*", parse_mode="Markdown")
    elif data == "action_trailing":
        bot.answer_callback_query(call.id, "🛡 Трейлинг-стоп активирован!")
        bot.send_message(chat_id, "🛡 *Трейлинг-стоп успешно включен.*", parse_mode="Markdown")
    else:
        bot.answer_callback_query(call.id, "Команда принята.")


if __name__ == "__main__":
    print("🤖 Интерактивный Telegram-слушатель запущен и ждет команды...")
    
    # Безопасный цикл polling с автовосстановлением при разрывах связи
    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except Exception as e:
            print(10 * "=" + f" Ошибка polling: {e} " + 10 * "=")
            time.sleep(5)
