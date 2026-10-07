import os

import pandas as pd
import streamlit as st

from utils.ai_engine import WarehouseAI
from utils.pdf_generator import generate_pdf_thermal


st.set_page_config(
    page_title="Warehouse AI System",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("📦 Warehouse AI & Inventory System")
st.markdown("Sistema intelligente di gestione magazzino con dati condivisi in CSV.")


def load_inventory_data() -> pd.DataFrame:
    """Load inventory data from repository-local CSV file if available."""
    csv_path = os.path.join("data", "inventory.csv")
    if os.path.exists(csv_path):
        try:
            df = pd.read_csv(csv_path)
            return df
        except Exception as exc:
            st.warning(f"Impossibile leggere il CSV: {exc}")
    return pd.DataFrame()


def prepare_product_data(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    normalized = df.copy()
    normalized["stock"] = pd.to_numeric(normalized.get("stock", 0), errors="coerce").fillna(0.0)
    normalized["reorder_point"] = pd.to_numeric(normalized.get("reorder_point", 0), errors="coerce").fillna(0.0)
    normalized["unit_price"] = pd.to_numeric(normalized.get("unit_price", 0), errors="coerce").fillna(0.0)
    normalized["name"] = normalized.get("name", "").fillna("")
    normalized["sku"] = normalized.get("sku", "").fillna("")
    normalized["category"] = normalized.get("category", "").fillna("")
    return normalized


try:
    df_products = prepare_product_data(load_inventory_data())
except Exception as exc:
    st.error(f"Errore nel caricamento dei dati: {exc}")
    st.stop()


if df_products.empty:
    st.info("💡 Nessun dato trovato. Verifica che esista il file data/inventory.csv.")
else:
    col1, col2, col3 = st.columns(3)
    val_tot = (df_products["stock"] * df_products["unit_price"]).sum()
    items_tot = df_products["stock"].sum()
    critical_cnt = df_products[df_products["stock"] < df_products["reorder_point"]].shape[0]

    col1.metric("💰 Valore Totale Giacenza", f"€ {val_tot:,.2f}")
    col2.metric("📦 Giacenza Complessiva", f"{items_tot:,.0f} pz")
    col3.metric(
        "⚠️ Prodotti Sotto Scorta",
        f"{critical_cnt}",
        delta=f"{critical_cnt} critici" if critical_cnt > 0 else "Nessuno",
        delta_color="inverse" if critical_cnt > 0 else "off",
    )

    st.divider()

    st.subheader("📋 Gestione Giacenze & Stampa Etichette")
    selected_product_name = st.selectbox("Seleziona Prodotto", df_products["name"].tolist())
    product_row = df_products[df_products["name"] == selected_product_name].iloc[0]

    new_stock = st.number_input("Nuova Giacenza", value=float(product_row["stock"]), min_value=0.0, step=1.0)
    if st.button("✅ Aggiorna giacenza ", use_container_width=True):
        df_products.loc[df_products["name"] == selected_product_name, "stock"] = new_stock
        st.success("✓ Giacenza aggiornata in memoria. Per salvarla permanentemente, salva il CSV.")

    st.divider()

    st.subheader("📊 Analisi AI & Dettagli Prodotti")
    ai = WarehouseAI()
    insights = []
    for _, row in df_products.iterrows():
        daily_sales = [float(row["stock"]) / 30.0] if row["stock"] > 0 else [0.0]
        insight = ai.analyze_product(
            row["sku"],
            row["name"],
            float(row["stock"]),
            daily_sales,
            float(row["unit_price"]),
        )
        insights.append(insight)

    df_insights = pd.DataFrame(insights)
    st.dataframe(
        df_insights[
            [
                "name",
                "sku",
                "current_stock",
                "avg_daily_demand",
                "reorder_point_ai",
                "days_autonomy",
                "status",
                "insight",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    st.subheader("🖨️ Esporta Etichette Termiche")
    if st.button("📥 Scarica PDF", use_container_width=True):
        try:
            pdf_bytes = generate_pdf_thermal(df_products.to_dict(orient="records"))
            st.download_button(
                label="💾 Scarica Etichette",
                data=pdf_bytes,
                file_name="etichette_warehouse_ai.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        except Exception as e:
            st.error(f"Errore nella generazione PDF: {e}")
