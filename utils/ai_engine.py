"""Local AI engine for warehouse inventory analysis."""
from __future__ import annotations

import numpy as np


class WarehouseAI:
    """AI engine for calculating safety stock, reorder points, and demand forecasting."""

    def __init__(self, lead_time_days: int = 7, z_score: float = 1.65):
        """Initialize the WarehouseAI engine.

        Args:
            lead_time_days: Lead time for orders in days (default: 7)
            z_score: Z-score for service level (default: 1.65 = 95% service level)
        """
        self.lead_time_days = max(1, int(lead_time_days))
        self.z_score = float(z_score)

    def analyze_product(
        self,
        sku: str,
        name: str,
        current_stock: float,
        daily_sales: list[float],
        unit_price: float,
    ) -> dict:
        """Analyze a product and return inventory insights.

        Args:
            sku: Product SKU
            name: Product name
            current_stock: Current stock quantity
            daily_sales: List of daily sales quantities
            unit_price: Unit price in EUR

        Returns:
            Dictionary containing analysis results
        """
        # Convert sales to numpy array
        sales_arr = np.asarray(daily_sales, dtype=float)
        if sales_arr.size == 0:
            sales_arr = np.array([0.0], dtype=float)

        # Calculate statistics
        avg_demand = float(np.mean(sales_arr))
        std_demand = float(np.std(sales_arr))

        # Calculate safety stock and reorder point
        safety_stock = int(np.ceil(self.z_score * np.sqrt(self.lead_time_days) * std_demand))
        reorder_point = int(np.ceil((avg_demand * self.lead_time_days) + safety_stock))
        days_autonomy = round(current_stock / avg_demand, 1) if avg_demand > 0 else 999.0

        # Determine status and insight
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
            "sku": sku,
            "name": name,
            "current_stock": float(current_stock),
            "avg_daily_demand": round(avg_demand, 2),
            "safety_stock": safety_stock,
            "reorder_point_ai": reorder_point,
            "days_autonomy": days_autonomy,
            "status": status,
            "insight": insight,
            "unit_price": float(unit_price),
        }
