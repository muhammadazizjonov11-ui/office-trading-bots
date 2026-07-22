import xml.etree.ElementTree as ET
import requests


class NewsAnalyst:
  """РАН - Робот-аналитик новостей и макро-календаря"""

  def check_economic_calendar(self):
    try:
      response = requests.get(
          "https://finance.yahoo.com/rss/headline?s=FED,CPI,FOMC,NFP",
          timeout=5,
      )
      if response.status_code == 200:
        root = ET.fromstring(response.content)
        events = [
            item.find("title").text.lower()
            for item in root.findall(".//item")
            if item.find("title") is not None and item.find("title").text
        ]
        for ev in events:
          for kw in [
              "fomc",
              "fed rate",
              "cpi inflation",
              "non-farm payrolls",
              "powell speech",
          ]:
            if kw in ev:
              return f"⚠️ Риск волатильности ({kw.upper()})", True
      return "✅ Календарь чист", False
    except Exception:
      return "✅ Календарь стабилен", False

  def get_news_sentiment(self):
    try:
      rss_url = "https://finance.yahoo.com/rss/headline?s=%5EGSPC"
      response = requests.get(rss_url, timeout=5)
      if response.status_code != 200:
        return "Нейтрально", 0
      root = ET.fromstring(response.content)
      headlines = [
          item.find("title").text.lower()
          for item in root.findall(".//item")
          if item.find("title") is not None and item.find("title").text
      ]
      bullish = sum(
          1
          for h in headlines
          for w in [
              "rally",
              "gain",
              "high",
              "surge",
              "jump",
              "record",
              "growth",
              "bull",
          ]
          if w in h
      )
      bearish = sum(
          1
          for h in headlines
          for w in [
              "drop",
              "fall",
              "crash",
              "slump",
              "inflation",
              "risk",
              "bear",
              "loss",
          ]
          if w in h
      )
      if bearish > bullish + 2:
        return "Медвежий 🔴", -1
      elif bullish > bearish + 2:
        return "Бычий 🟢", 1
      else:
        return "Нейтральный ⚖️", 0
    except Exception:
      return "Недоступно", 0
