import streamlit as st
import pandas as pd
from utils.sharepoint_db import get_sharepoint_data, update_stock_in_sharepoint
from utils.ai_engine import WarehouseAI
from utils.pdf_generator import generate_pdf_thermal

st.set_page_config(page_title="Warehouse AI System", page_icon="📦", layout="wide")
st.title("📦 Warehouse AI & Inventory System")

try:
    df_products = get_sharepoint_data()
except Exception as e:
    st.error(f"Errore di connessione a SharePoint: {e}")
    st.stop()

if df_products.empty:
    st.info("💡 Nessun prodotto trovato nella lista SharePoint.")
else:
    col1, col2, col3 = st.columns(3)
    val_tot = (df_products['stock'] * df_products['unit_price']).sum()
    items_tot = df_products['stock'].sum()
    critical_cnt = df_products[df_products['stock'] < df_products['reorder_point']].shape[0]

    col1.metric("Valore Totale", f"€ {val_tot:,.2f}")
    col2.metric("Giacenza Complessiva", f"{items_tot:,.0f} pz")
    col3.metric("Prodotti Sotto Scorta", f"{critical_cnt}", delta_color="inverse", delta=f"{critical_cnt} critici")

    st.divider()

    st.subheader("📋 Gestione Giacenze & Stampa Etichette")
    selected_product_name = st.selectbox("Seleziona Prodotto", df_products['name'].tolist())
    product_row = df_products[df_products['name'] == selected_product_name].iloc[0]
    
    new_stock = st.number_input("Nuova Giacenza", value=float(product_row['stock']))
    if st.button("Aggiorna Giacenza su SharePoint"):
        update_stock_in_sharepoint(int(product_row['ID']), new_stock)
        st.success("Giacenza aggiornata con successo! Ricarica la pagina per vedere le modifiche.")

    st.divider()

    st.subheader("📊 Analisi AI & Dettagli Prodotti")
    ai = WarehouseAI()
    insights = []
    
    for _, row in df_products.iterrows():
        insight = ai.analyze_product(row['sku'], row['name'], row['stock'], [float(row['stock'])], row['unit_price'])
        insights.append(insight)
        
    df_insights = pd.DataFrame(insights)
    st.dataframe(df_insights, use_container_width=True)

    if st.button("🖨️ Genera PDF Etichette Termiche"):
        pdf_bytes = generate_pdf_thermal(df_products.to_dict(orient="records"))
        st.download_button(
            label="💾 Scarica PDF",
            data=pdf_bytes,
            file_name="etichette_zebra_50x30.pdf",
            mime="application/pdf"
        )