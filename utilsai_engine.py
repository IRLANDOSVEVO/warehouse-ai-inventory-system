import numpy as np

class WarehouseAI:
    def __init__(self, lead_time_days: int = 7, z_score: float = 1.65):
        self.lead_time_days = lead_time_days
        self.z_score = z_score

    def analyze_product(self, sku: str, name: str, current_stock: float, daily_sales: list[float], unit_price: float) -> dict:
        sales_arr = np.array(daily_sales) if len(daily_sales) > 0 else np.array([0.0])
        avg_demand = float(np.mean(sales_arr))
        std_demand = float(np.std(sales_arr))

        safety_stock = int(np.ceil(self.z_score * np.sqrt(self.lead_time_days) * std_demand))
        reorder_point = int(np.ceil((avg_demand * self.lead_time_days) + safety_stock))
        days_autonomy = round(current_stock / avg_demand, 1) if avg_demand > 0 else 999.0

        if current_stock <= 0:
            status = "🚨 Esaurito"
            insight = "Effettuare un ordine d'emergenza."
        elif current_stock < reorder_point:
            status = "⚠️ Sotto punto di riordino"
            insight = f"Ordinare entro {max(1, int(days_autonomy - self.lead_time_days))} giorni."
        elif days_autonomy > 90:
            status = "📦 Overstock"
            insight = "Pianificare sconti per sbloccare capitale."
        else:
            status = "✅ Giacenza ottimale"
            insight = "Nessuna azione richiesta."

        return {
            'sku': sku,
            'name': name,
            'current_stock': current_stock,
            'avg_daily_demand': round(avg_demand, 2),
            'safety_stock': safety_stock,
            'reorder_point_ai': reorder_point,
            'days_autonomy': days_autonomy,
            'status': status,
            'insight': insight
        }