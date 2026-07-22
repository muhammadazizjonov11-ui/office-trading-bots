from analysts.aka import AssetAnalyst
from analysts.pap import MarketAnalyst
from analysts.ran import NewsAnalyst
from analysts.rat import TimeframeAnalyst


class ManagementRobot:
  """ГУР - Главный управляющий робот (Координирует аналитиков)"""

  def __init__(self):
    self.pap = MarketAnalyst()
    self.ran = NewsAnalyst()
    self.rat = TimeframeAnalyst()
    self.aka = AssetAnalyst()

  def gather_all_analytics(self):
    print("🔄 [ГУР] Сбор данных от подчиненных роботов (РАР, РАН, РАТ, АКА)...")

    market_data = self.pap.analyze_us500()
    news_text, news_code = self.ran.get_news_sentiment()
    calendar_text, is_macro_danger = self.ran.check_economic_calendar()
    trends = self.rat.check_trends()
    assets_data = self.aka.analyze_gold_and_oil()

    return {
        "market": market_data,
        "news_text": news_text,
        "news_code": news_code,
        "calendar_text": calendar_text,
        "is_macro_danger": is_macro_danger,
        "trends": trends,
        "assets": assets_data,
    }
