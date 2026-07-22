import pandas as pd
import yfinance as yf


class MarketAnalyst:
  """РАР - Робот-аналитик рынка (PRO Версия с расширенными фильтрами)"""

  def analyze_us500(self):
    try:
      df_1d = yf.download(
          "^GSPC", period="6mo", interval="1d", progress=False
      )
      if isinstance(df_1d.columns, pd.MultiIndex):
        df_1d.columns = df_1d.columns.get_level_values(0)

      df_1d["SMA_20"] = df_1d["Close"].rolling(20).mean()
      df_1d["SMA_50"] = df_1d["Close"].rolling(50).mean()
      df_1d["SMA_200"] = df_1d["Close"].rolling(200).mean()

      # Расчет ATR для фильтрации волатильности
      df_1d["ATR"] = (
          df_1d[["High", "Low", "Close"]]
          .apply(lambda x: x["High"] - x["Low"], axis=1)
          .rolling(14)
          .mean()
      )
      df_1d["ATR_MA"] = df_1d["ATR"].rolling(14).mean()  # Средняя волатильность

      df_1d["BB_Mid"] = df_1d["Close"].rolling(20).mean()
      df_1d["BB_Std"] = df_1d["Close"].rolling(20).std()
      df_1d["BB_Upper"] = df_1d["BB_Mid"] + (df_1d["BB_Std"] * 2)
      df_1d["BB_Lower"] = df_1d["BB_Mid"] - (df_1d["BB_Std"] * 2)

      delta = df_1d["Close"].diff()
      gain = delta.where(delta > 0, 0).rolling(14).mean()
      loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
      df_1d["RSI"] = 100 - (100 / (1 + (gain / (loss + 1e-10))))

      latest = df_1d.iloc[-1]

      # PRO-фильтр волатильности: ATR должен быть выше своей средней линии (рынок активен)
      is_volatility_normal = float(latest["ATR"]) >= float(
          latest["ATR_MA"] * 0.8
      )

      return {
          "close": float(latest["Close"]),
          "sma_20": float(latest["SMA_20"]),
          "sma_50": float(latest["SMA_50"]),
          "sma_200": (
              float(latest["SMA_200"])
              if not pd.isna(latest["SMA_200"])
              else float(latest["SMA_50"])
          ),
          "atr": float(latest["ATR"]),
          "rsi": float(latest["RSI"]),
          "bb_upper": float(latest["BB_Upper"]),
          "bb_lower": float(latest["BB_Lower"]),
          "is_volatility_normal": is_volatility_normal,
      }
    except Exception as e:
      print(f"❌ [РАР-PRO] Ошибка анализа рынка: {e}")
      return None
