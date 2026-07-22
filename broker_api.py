import requests
from config import BROKER_API_KEY, BROKER_API_URL, BROKER_LOGIN, BROKER_PASSWORD

# Глобальное хранилище сессии
active_session = {"cst": None, "x_security_token": None, "last_deal_id": None}


def capital_login():
  url = f"{BROKER_API_URL}/session"
  headers = {"X-CAP-API-KEY": BROKER_API_KEY, "Content-Type": "application/json"}
  payload = {
      "identifier": BROKER_LOGIN,
      "password": BROKER_PASSWORD,
      "encryptedPassword": False,
  }
  try:
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
      active_session["cst"] = response.headers.get("CST")
      active_session["x_security_token"] = response.headers.get(
          "X-SECURITY-TOKEN"
      )
      print("✅ Успешная авторизация в API Capital.com!")
      return True
    else:
      print(f"❌ Ошибка авторизации Capital.com: {response.text}")
      return False
  except Exception as e:
    print(f"❌ Ошибка соединения при логине Capital.com: {e}")
    return False


def execute_broker_order(direction, volume, stop_loss, take_profit):
  print(
      f"🔄 Отправка ордера брокеру: {direction} | Объем: {volume} | SL:"
      f" {stop_loss} | TP: {take_profit}"
  )

  if not active_session["cst"] and not capital_login():
    print("❌ Нет активной сессии брокера. Ордер отклонен.")
    return False

  url = f"{BROKER_API_URL}/positions"
  headers = {
      "X-CAP-API-KEY": BROKER_API_KEY,
      "CST": active_session["cst"],
      "X-SECURITY-TOKEN": active_session["x_security_token"],
      "Content-Type": "application/json",
  }

  payload = {
      "epic": "US500",
      "direction": direction,
      "size": volume,
      "guaranteedStopLoss": False,
      "stopLossLevel": stop_loss if stop_loss > 0 else None,
      "profitLevel": take_profit if take_profit > 0 else None,
      "trailingStop": True,
  }

  try:
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code in [200, 201]:
      data = response.json()
      deal_reference = data.get("dealReference")
      print(f"✅ Ордер принят брокером! Ссылка: {deal_reference}")
      active_session["last_deal_id"] = deal_reference
      return True
    else:
      print(f"❌ Ошибка открытия позиции: {response.text}")
      return False
  except Exception as e:
    print(f"❌ Исключение при отправке ордера: {e}")
    return False
