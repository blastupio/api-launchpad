class PointsCalculator:
    @classmethod
    def _get_coef_for_ido_purchase(cls, usd_amount: float) -> float:
        if usd_amount < 10:
            return 0

        if usd_amount < 250:
            return 0.06

        if usd_amount < 500:
            return 0.07

        if usd_amount < 1000:
            return 0.08

        if usd_amount < 2500:
            return 0.09

        if usd_amount < 5000:
            return 0.10

        if usd_amount < 10000:
            return 0.11

        return 0.12

    @classmethod
    def calculate_points_for_ido_purchase(
        cls, usd_amount: float | str, bonus_for_ido: float = 2.0
    ) -> float:
        usd_amount = float(usd_amount)
        coef = cls._get_coef_for_ido_purchase(usd_amount)
        return round(usd_amount * coef * 100 * bonus_for_ido, 2)
