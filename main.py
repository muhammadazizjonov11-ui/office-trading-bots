from datetime import datetime
import threading
import time
from broker_api import capital_login, execute_broker_order
from config import ACCOUNT_BALANCE, CHAT_ID, RISK_PERCENT, TELEGRAM_TOKEN
from managers import ManagementRobot
import requests


class MainTradingRobot:
  """ГТР - Главный торговый/офисный робот (PRO Версия с фильтрацией волатильности)"""

  def __init__(self):
    self.name = "GTR-PRO"
    self.manager = ManagementRobot()

  def send_telegram_signal(
      self, target_chat_id, message, signal_type, volume, sl, tp
  ):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    keyboard = {
        "inline_keyboard": [
            [
                {"text": "📊 Анализ", "callback_data": "action_analysis"},
                {"text": "📈 Терминал", "url": "https://capital.com/trading/"},
            ],
            [
                {
                    "text": "⚡ АВТО-ВХОД (API)",
                    "callback_data": f"auto_trade_{signal_type}_{volume}_{sl}_{tp}",
                },
            ],
            [
                {"text": "🛡 Трейлинг-Стоп ВКЛ", "callback_data": "action_trailing"},
                {"text": "🚨 ЗАКРЫТЬ ВСЁ", "callback_data": "action_close_all"},
            ],
        ]
    }

    payload = {
        "chat_id": target_chat_id,
        "text": message,
        "parse_mode": "Markdown",
        "reply_markup": keyboard,
    }

    try:
      response = requests.post(url, json=payload)
      if response.status_code == 200:
        print("✅ [ГТР-PRO] Сигнал успешно отправлен в Telegram!")
      else:
        print(f"❌ [ГТР-PRO] Ошибка отправки в Telegram: {response.text}")
    except Exception as e:
      print(f"❌ [ГТР-PRO] Ошибка соединения с Telegram: {e}")

  def run_cycle(self, target_chat_id):
    print(f"🚀 [{self.name}] Запуск полного цикла PRO-анализа данных...")

    data = self.manager.gather_all_analytics()

    market = data["market"]
    news_text = data["news_text"]
    news_code = data["news_code"]
    calendar_text = data["calendar_text"]
    is_macro_danger = data["is_macro_danger"]
    trends = data["trends"]
    assets = data["assets"]

    if not market or not trends:
      print(f"⚠️ [{self.name}] Недостаточно данных для принятия решения.")
      return

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    allowed_risk_usd = ACCOUNT_BALANCE * (RISK_PERCENT / 100.0)

    latest_close = market["close"]
    sma_20 = market["sma_20"]
    sma_50 = market["sma_50"]
    atr = market["atr"]
    rsi = market["rsi"]
    bb_upper = market["bb_upper"]
    bb_lower = market["bb_lower"]
    is_volatility_normal = market["is_volatility_normal"]

    is_bullish_trend = (
        sma_20 > sma_50 and trends["h1_bullish"] and trends["weekly_bullish"]
    )
    is_bearish_trend = (
        sma_20 < sma_50 and trends["h1_bearish"] and trends["weekly_bearish"]
    )

    us500_sig = "HOLD"
    us500_sl = 0
    us500_tp = 0
    us500_size = 0

    # 1. Расчет сигнала US500
    if is_macro_danger:
      us500_sig = "HOLD"
      us500_advice = "🚨 *РЫНОК ЗАБЛОКИРОВАН КАЛЕНДАРЕМ*"
    elif not is_volatility_normal:
      us500_sig = "HOLD"
      us500_advice = "💤 *РЫНОК ВО ФЛЭТЕ (Низкая волатильность)*"
    elif (
        is_bullish_trend
        and rsi < 70
        and latest_close < bb_upper
        and news_code != -1
    ):
      us500_sig = "LONG"
      us500_sl = round(latest_close - (atr * 1.5), 2)
      us500_tp = round(latest_close + (atr * 3.0), 2)
      risk_share = abs(latest_close - us500_sl)
      us500_size = (
          round(allowed_risk_usd / risk_share, 2) if risk_share > 0 else 1
      )
    elif (
        is_bearish_trend
        and rsi > 30
        and latest_close > bb_lower
        and news_code != 1
    ):
      us500_sig = "SHORT"
      us500_sl = round(latest_close + (atr * 1.5), 2)
      us500_tp = round(latest_close - (atr * 3.0), 2)
      risk_share = abs(us500_sl - latest_close)
      us500_size = (
          round(allowed_risk_usd / risk_share, 2) if risk_share > 0 else 1
      )
    else:
      us500_sig = "HOLD"
      us500_advice = "⚖️ *US500: HOLD (Фильтры не пройдены)*"

    # 2. Общий флаг высокой уверенности по новостям для всех активов
    is_high_confidence = not is_macro_danger and (news_code != 0)
    signal_prefix = "⚠️ *ВАЖНО!* " if is_high_confidence else ""

    # Оформление совета по US500 с префиксом
    if us500_sig == "LONG":
      us500_advice = (
          f"{signal_prefix}🟢 *US500: PRO-LONG* | Вход: `{latest_close:.2f}` | SL:"
          f" `{us500_sl}` | TP: `{us500_tp}`"
      )
    elif us500_sig == "SHORT":
      us500_advice = (
          f"{signal_prefix}🔴 *US500: PRO-SHORT* | Вход: `{latest_close:.2f}` | SL:"
          f" `{us500_sl}` | TP: `{us500_tp}`"
      )

    # 3. Добавляем префикс ВАЖНО! для Золота и Нефти
    if assets:
      # Проверяем направление золота (например, если это 'LONG' или 'BUY', добавляем префикс)
      gold_dir = assets["gold"].get("dir", "")
      gold_prefix = (
          signal_prefix
          if (is_high_confidence and gold_dir in ["LONG", "BUY", "Bullish"])
          else ""
      )

      gold_info = (
          f"🟡 *Золото (GC=F):* `{assets['gold']['price']:.2f}` | Сигнал:"
          f" `{gold_prefix}{gold_dir}`\n    └ SL: `{assets['gold']['sl']}` | TP:"
          f" `{assets['gold']['tp']}`"
      )

      # Проверяем направление нефти
      oil_dir = assets["oil"].get("dir", "")
      oil_prefix = (
          signal_prefix
          if (is_high_confidence and oil_dir in ["LONG", "BUY", "Bullish"])
          else ""
      )

      oil_info = (
          f"🛢 *Нефть (BZ=F):* `{assets['oil']['price']:.2f}` | Сигнал:"
          f" `{oil_prefix}{oil_dir}`\n    └ SL: `{assets['oil']['sl']}` | TP:"
          f" `{assets['oil']['tp']}`"
      )
    else:
      gold_info = "🟡 Золото: Н/Д"
      oil_info = "🛢 Нефть: Н/Д"

    # 4. Собираем итоговое сообщение
    message_text = (
        f"🤖 *ГТР [HIERARCHY SYSTEM PRO]*\n"
        f"🕒 *Время:* `{current_time}`\n\n"
        f"📰 *Новости:* `{news_text}`\n"
        f"📅 *Календарь:* `{calendar_text}`\n\n"
        f"{gold_info}\n\n"
        f"{oil_info}\n\n"
        f"📈 *US500 PRO-Анализ:*\n{us500_advice}"
    )

    self.send_telegram_signal(
        target_chat_id, message_text, us500_sig, us500_size, us500_sl, us500_tp
    )


if __name__ == "__main__":
  print("⚙️ Инициализация PRO-системы иерархических ботов...")
  capital_login()

  bot = MainTradingRobot()
  bot.run_cycle(CHAT_ID)
