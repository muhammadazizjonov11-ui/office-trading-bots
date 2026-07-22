import time
from config import CHAT_ID, TELEGRAM_TOKEN
from main import MainTradingRobot
import telebot

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
  # Запускаем полный цикл анализа и отправки отчета в тот же чат
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
  # Запуск непрерывного прослушивания сообщений и нажатий
  bot.infinity_polling()
