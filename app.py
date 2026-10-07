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


def ensure_data_dir():
    """Ensure data directory exists."""
    if not os.path.exists("data"):
        os.makedirs("data")


def get_available_csv_files() -> list:
    """Get list of available CSV files in data directory."""
    ensure_data_dir()
    files = [f for f in os.listdir("data") if f.endswith(".csv")]
    return sorted(files) if files else []


def load_inventory_data(filename: str = "inventory.csv") -> pd.DataFrame:
    """Load inventory data from CSV file."""
    csv_path = os.path.join("data", filename)
    if os.path.exists(csv_path):
        try:
            df = pd.read_csv(csv_path)
            return df
        except Exception as exc:
            st.warning(f"Impossibile leggere il CSV: {exc}")
    return pd.DataFrame()


def save_inventory_data(df: pd.DataFrame, filename: str = "inventory.csv"):
    """Save inventory data to CSV file."""
    ensure_data_dir()
    csv_path = os.path.join("data", filename)
    try:
        df.to_csv(csv_path, index=False)
        st.success(f"✓ Dati salvati su {filename}")
    except Exception as exc:
        st.error(f"Errore nel salvataggio: {exc}")


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


# ==================== SIDEBAR: Data Management ====================
with st.sidebar:
    st.header("📂 Gestione Dati")
    
    # Available files selector
    available_files = get_available_csv_files()
    if available_files:
        selected_file = st.selectbox("Seleziona dataset", available_files)
    else:
        selected_file = "inventory.csv"
        st.info("Nessun CSV trovato. Carica uno con il form sottostante.")
    
    st.divider()
    
    # Upload new CSV
    st.subheader("📤 Carica nuovo CSV")
    uploaded_file = st.file_uploader("Scegli un file CSV", type="csv")
    if uploaded_file is not None:
        try:
            df_upload = pd.read_csv(uploaded_file)
            # Validate required columns
            required_cols = ["sku", "name", "stock", "unit_price"]
            missing_cols = [col for col in required_cols if col not in df_upload.columns]
            
            if missing_cols:
                st.error(f"Colonne mancanti: {', '.join(missing_cols)}")
            else:
                ensure_data_dir()
                filename = uploaded_file.name
                save_path = os.path.join("data", filename)
                df_upload.to_csv(save_path, index=False)
                st.success(f"✓ File caricato: {filename}")
                st.rerun()
        except Exception as exc:
            st.error(f"Errore nel caricamento: {exc}")
    
    st.divider()
    
    # List all available files
    st.subheader("📋 File disponibili")
    if available_files:
        for f in available_files:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.text(f)
            with col2:
                if st.button("🗑️", key=f"delete_{f}"):
                    try:
                        os.remove(os.path.join("data", f))
                        st.success(f"Eliminato: {f}")
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Errore: {exc}")
    else:
        st.info("Nessun file CSV disponibile")


# ==================== MAIN APP ====================
try:
    df_products = prepare_product_data(load_inventory_data(selected_file))
except Exception as exc:
    st.error(f"Errore nel caricamento dei dati: {exc}")
    st.stop()


if df_products.empty:
    st.info("💡 Nessun dato trovato. Carica un CSV dalla sidebar.")
else:
    # Initialize session state for tracking changes
    if "df_modified" not in st.session_state:
        st.session_state.df_modified = df_products.copy()
    
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
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        selected_product_name = st.selectbox("Seleziona Prodotto", df_products["name"].tolist())
    
    product_row = df_products[df_products["name"] == selected_product_name].iloc[0]
    product_idx = df_products[df_products["name"] == selected_product_name].index[0]
    
    with col2:
        new_stock = st.number_input(
            "Nuova Giacenza",
            value=float(product_row["stock"]),
            min_value=0.0,
            step=1.0,
        )
    
    with col3:
        st.write("")
        if st.button("✅ Aggiorna", use_container_width=True):
            df_products.loc[product_idx, "stock"] = new_stock
            st.session_state.df_modified = df_products.copy()
            st.success("✓ Giacenza aggiornata!")

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

    st.subheader("💾 Salva Modifiche & Esporta")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💾 Salva su CSV", use_container_width=True):
            save_inventory_data(df_products, selected_file)
    
    with col2:
        # Download current data as CSV
        csv_data = df_products.to_csv(index=False).encode()
        st.download_button(
            label="📥 Scarica CSV",
            data=csv_data,
            file_name=f"inventory_export_{selected_file}",
            mime="text/csv",
            use_container_width=True,
        )
    
    with col3:
        if st.button("🖨️ Scarica PDF", use_container_width=True):
            try:
                pdf_bytes = generate_pdf_thermal(df_products.to_dict(orient="records"))
                st.download_button(
                    label="📄 PDF Etichette",
                    data=pdf_bytes,
                    file_name="etichette_warehouse_ai.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
            except Exception as e:
                st.error(f"Errore nella generazione PDF: {e}")
    
    st.divider()
    
    st.subheader("📝 Editor Dati (Tabella)")
    st.info("Modifica direttamente i dati nella tabella sottostante, poi clicca 'Salva su CSV'")
    
    edited_df = st.data_editor(
        df_products,
        use_container_width=True,
        num_rows="dynamic",
        key="data_editor"
    )
    
    if not edited_df.equals(df_products):
        st.session_state.df_modified = edited_df
        st.info("Hai modificato i dati. Clicca 'Salva su CSV' per salvare le modifiche.")
