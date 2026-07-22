import pandas as pd
import yfinance as yf


class TimeframeAnalyst:
  """РАТ - Робот-аналитик таймфреймов (1H, 1W)"""

  def check_trends(self):
    try:
      df_1h = yf.download(
          "^GSPC", period="1mo", interval="60m", progress=False
      )
      df_1w = yf.download(
          "^GSPC", period="1y", interval="1wk", progress=False
      )

      for df in [df_1h, df_1w]:
        if isinstance(df.columns, pd.MultiIndex):
          df.columns = df.columns.get_level_values(0)

      df_1h["SMA_9"] = df_1h["Close"].rolling(9).mean()
      df_1h["SMA_21"] = df_1h["Close"].rolling(21).mean()
      df_1w["SMA_20"] = df_1w["Close"].rolling(20).mean()

      h1_fast = float(df_1h["SMA_9"].iloc[-1])
      h1_slow = float(df_1h["SMA_21"].iloc[-1])

      weekly_close = float(df_1w["Close"].iloc[-1])
      weekly_sma20 = float(df_1w["SMA_20"].iloc[-1])

      return {
          "h1_bullish": h1_fast > h1_slow,
          "h1_bearish": h1_fast < h1_slow,
          "weekly_bullish": weekly_close > weekly_sma20,
          "weekly_bearish": weekly_close < weekly_sma20,
      }
    except Exception as e:
      print(f"❌ [РАТ] Ошибка анализа таймфреймов: {e}")
      return None
