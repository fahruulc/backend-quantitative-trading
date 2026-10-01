from app.schemas.macro import MacroData
from app.schemas.sector import SectorData

class SectorSelectorProfessionalService:
    def __init__(self):
        self.sectors = {
            "IDXENERGY": {"drivers": {"oil": 0.8, "usd": 0.5}, "defensive": False},
            "IDXBASIC":  {"drivers": {"gold": 0.4, "copper": 0.8, "usd": 0.3}, "defensive": False},
            "IDXFINANCE":{"drivers": {"eido": 0.9, "yield": 0.2, "usd": -0.4}, "defensive": True},
            "IDXNONCYC": {"drivers": {"usd": -0.8, "oil": -0.3}, "defensive": True},
            "IDXTECH":   {"drivers": {"yield": -0.9, "btc": 0.6}, "defensive": False},
            "IDXINFRA":  {"drivers": {"yield": -0.4}, "defensive": True}
        }

    def calculate_normalization(self, val, min_v, max_v):
        if val < min_v: return 0
        if val > max_v: return 100
        return ((val - min_v) / (max_v - min_v)) * 100

    def score_sectors(self, m: MacroData) -> dict:
        scores = {}
        for sec_name, sec_data in self.sectors.items():
            final_score = 50
            drivers = sec_data['drivers']

            for driver_key, weight in drivers.items():
                impact = 0
                if driver_key == "usd":
                    val = self.calculate_normalization(m.usd, 14500, 16800)
                    impact = (val - 50) * weight * 0.5
                elif driver_key == "oil":
                    val = self.calculate_normalization(m.oil, 60, 90)
                    impact = (val - 50) * weight * 0.5
                elif driver_key == "gold":
                    val = self.calculate_normalization(m.gold, 2000, 2700)
                    impact = (val - 50) * weight * 0.5
                elif driver_key == "copper":
                    val = self.calculate_normalization(m.copper, 3.5, 5.0)
                    impact = (val - 50) * weight * 0.8
                elif driver_key == "yield":
                    val = self.calculate_normalization(m.yield_rate, 3.5, 5.0)
                    impact = (val - 50) * weight * 0.6
                elif driver_key == "eido":
                    impact = m.eido * weight * 10
                elif driver_key == "btc":
                    val = self.calculate_normalization(m.btc, 60000, 100000)
                    impact = (val - 50) * weight * 0.4

                final_score += impact

            if ("FEAR" in m.status or "Cash" in m.status) and sec_data['defensive']:
                final_score += 10

            scores[sec_name] = round(max(0, min(100, final_score)), 1)

        # Mengembalikan dictionary yang sudah di-sort
        return dict(sorted(scores.items(), key=lambda item: item[1], reverse=True))

    def run(self, macro_data: MacroData) -> SectorData:
        """
        Menerima input macro_data secara eksplisit (Stateless) alih-alih mengambil dari _SHARED_MACRO_DATA.
        """
        scores = self.score_sectors(macro_data)
        top_sector = list(scores.keys())[0] if scores else ""
        
        return SectorData(
            sorted_sectors=scores,
            top_sector=top_sector
        )
