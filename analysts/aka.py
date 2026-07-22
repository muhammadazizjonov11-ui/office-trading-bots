import pandas as pd
import yfinance as yf


class AssetAnalyst:
  """АКА - Аналитик мульти-активов (Золото и Нефть)"""

  def analyze_gold_and_oil(self):
    try:
      gold = yf.download("GC=F", period="1mo", interval="1d", progress=False)
      oil = yf.download("BZ=F", period="1mo", interval="1d", progress=False)

      for df in [gold, oil]:
        if isinstance(df.columns, pd.MultiIndex):
          df.columns = df.columns.get_level_values(0)

      gold_price = (
          float(gold["Close"].iloc[-1]) if not gold.empty else 2400.0
      )
      gold_atr = (
          float((gold["High"] - gold["Low"]).rolling(14).mean().iloc[-1])
          if not gold.empty
          else 15.0
      )
      gold_dir = (
          "BUY" if gold_price > float(gold["Close"].iloc[-5]) else "SELL"
      )

      oil_price = float(oil["Close"].iloc[-1]) if not oil.empty else 80.0
      oil_atr = (
          float((oil["High"] - oil["Low"]).rolling(14).mean().iloc[-1])
          if not oil.empty
          else 1.5
      )
      oil_dir = "BUY" if oil_price > float(oil["Close"].iloc[-5]) else "SELL"

      return {
          "gold": {
              "price": gold_price,
              "dir": gold_dir,
              "sl": round(
                  gold_price - (gold_atr * 1.5)
                  if gold_dir == "BUY"
                  else gold_price + (gold_atr * 1.5),
                  2,
              ),
              "tp": round(
                  gold_price + (gold_atr * 3.0)
                  if gold_dir == "BUY"
                  else gold_price - (gold_atr * 3.0),
                  2,
              ),
          },
          "oil": {
              "price": oil_price,
              "dir": oil_dir,
              "sl": round(
                  oil_price - (oil_atr * 1.5)
                  if oil_dir == "BUY"
                  else oil_price + (oil_atr * 1.5),
                  2,
              ),
              "tp": round(
                  oil_price + (oil_atr * 3.0)
                  if oil_dir == "BUY"
                  else oil_price - (oil_atr * 3.0),
                  2,
              ),
          },
      }
    except Exception as e:
      print(f"❌ [АКА] Ошибка анализа активов: {e}")
      return None
