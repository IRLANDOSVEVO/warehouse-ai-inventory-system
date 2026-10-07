# 📦 Warehouse AI Inventory System

Sistema intelligente di gestione magazzino costruito con Python + Streamlit, integrato con Microsoft SharePoint, dotato di analisi AI locale e generazione di etichette PDF termiche con codice a barre.

## ✨ Funzionalità

- **Dashboard KPI** con valore totale giacenza, quantità totale e conteggio prodotti critici
- **Integrazione SharePoint** per lettura e aggiornamento dati in tempo reale
- **Motore AI locale** per calcolo di:
  - Safety Stock (scorta di sicurezza)
  - Reorder Point (punto di riordino)
  - Giorni di autonomia
  - Status e insight automatici (Esaurito, Sotto scorta, Overstock, Ottimale)
- **Generazione PDF** con etichette termiche 50×30 mm contenenti:
  - Nome prodotto
  - Codice a barre Code128
  - SKU e prezzo unitario
- **Download immediato** dal browser senza installazioni esterne

## 📁 Struttura del Progetto

```
warehouse-ai-inventory-system/
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
├── app.py
├── .streamlit/
│   └── config.toml
└── utils/
    ├── __init__.py
    ├── ai_engine.py
    ├── pdf_generator.py
    └── sharepoint_db.py
```

## 🔧 Requisiti

- **Python** 3.10 o superiore
- **Git** per il controllo versione
- **Accesso SharePoint** con permessi di lettura/scrittura
- **Lista SharePoint** con campi standard (vedi sotto)
- **Streamlit Community Cloud account** (opzionale per il deploy)

## 🚀 Setup Locale

### 1. Clona il repository

```bash
git clone https://github.com/IRLANDOSVEVO/warehouse-ai-inventory-system.git
cd warehouse-ai-inventory-system
```

### 2. Crea ambiente virtuale

```bash
python -m venv .venv

# Linux / macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

### 3. Installa dipendenze

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configura variabili d'ambiente

Copia il file di esempio:

```bash
cp .env.example .env
```

Modifica `.env` con i tuoi dati SharePoint:

```env
SP_URL=https://yourtenant.sharepoint.com/sites/YourSite
SP_USER=your.user@yourdomain.com
SP_PASS=your_password_here
SP_LIST_NAME=Prodotti Magazzino
```

### 5. Avvia l'app

```bash
streamlit run app.py
```

L'app sarà disponibile su `http://localhost:8501`

## 📋 Struttura Lista SharePoint

La lista SharePoint deve contenere i seguenti campi:

| Campo | Tipo | Descrizione |
|-------|------|-------------|
| `Title` | Testo | Nome del prodotto |
| `SKU` | Testo | Codice SKU univoco |
| `Category` | Testo | Categoria prodotto |
| `Stock` | Numero | Quantità attuale |
| `ReorderPoint` | Numero | Soglia minima di riordino |
| `UnitPrice` | Valuta | Prezzo unitario in EUR |
| `Id` | (automatico) | ID elemento SharePoint |

## 🤖 Logica AI

L'engine WarehouseAI calcola:

- **Media domanda giornaliera** (μ) dalle quantità di stock
- **Deviazione standard** (σ) per la variabilità
- **Safety Stock** = z-score × √(lead_time) × σ
- **Reorder Point** = (μ × lead_time) + safety_stock
- **Giorni di autonomia** = stock attuale / μ
- **Status** automatico:
  - 🚨 **Esaurito** (stock ≤ 0)
  - ⚠️ **Sotto punto di riordino** (stock < reorder_point)
  - 📦 **Overstock** (autonomia > 90 giorni)
  - ✅ **Giacenza ottimale** (tutto ok)

## 🖨️ Generazione PDF

L'app genera PDF con etichette termiche 50×30 mm standardizzate per stampanti termiche Zebra.

Ciascuna etichetta contiene:
- Nome prodotto (massimo 22 caratteri)
- Codice a barre Code128 leggibile
- SKU e prezzo unitario

## 🌐 Deploy su Streamlit Community Cloud

### Prerequisiti

- Account Streamlit Community Cloud gratuito
- Repository pubblico su GitHub
- Variabili d'ambiente configurate

### Procedura

1. **Carica il codice su GitHub**

```bash
git add .
git commit -m "Initial commit: Warehouse AI System"
git push origin main
```

2. **Accedi a Streamlit Cloud**

Vai su https://streamlit.io/cloud

3. **Crea una nuova app**

- Clicca "New app"
- Seleziona il tuo repository GitHub
- Scegli il branch `main`
- File principale: `app.py`

4. **Configura variabili d'ambiente**

Nella schermata di deploy, clicca su "Advanced settings" e aggiungi:

```
SP_URL=https://yourtenant.sharepoint.com/sites/YourSite
SP_USER=your.user@yourdomain.com
SP_PASS=your_password_here
SP_LIST_NAME=Prodotti Magazzino
```

5. **Deploy**

Clicca "Deploy". Streamlit creerà un URL pubblico per la tua app.

## 🔒 Sicurezza

### ⚠️ Importanti avvertimenti

- **Non committare il file `.env`** → È già nel `.gitignore`
- **Non inserire credenziali nel codice** → Usa solo variabili d'ambiente
- **Usa account SharePoint con privilegi minimi** → Non usare admin account
- **Cambia regolarmente la password** → Soprattutto su Streamlit Cloud
- **Monitora l'accesso** → Controlla i log di SharePoint

## 🔧 Troubleshooting

### Errore: "Errore di connessione a SharePoint"

**Causa:** Credenziali non configurate o errate

**Soluzione:**

1. Verifica che `.env` sia nel root del progetto
2. Controlla che le credenziali siano corrette
3. Verifica che l'URL del sito SharePoint sia corretto
4. Testa l'accesso direttamente a SharePoint nel browser

### Errore: "Lista 'Prodotti Magazzino' non trovata"

**Causa:** Nome lista sbagliato o lista inesistente

**Soluzione:**

1. Vai al tuo sito SharePoint
2. Copia il nome esatto della lista
3. Aggiungi in `.env`: `SP_LIST_NAME=Nome Esatto`
4. Riavvia l'app

### Errore nella generazione PDF

**Causa:** Dipendenze mancanti

**Soluzione:**

```bash
pip install --upgrade reportlab pillow python-barcode
streamlit run app.py
```

## 📊 Esempio dati di test

Puoi aggiungere questi prodotti nella lista SharePoint per test:

| Title | SKU | Category | Stock | ReorderPoint | UnitPrice |
|-------|-----|----------|-------|--------------|-----------|
| Vite M8x50 | SKU-001 | Ferramenta | 150 | 50 | 2.50 |
| Bullone M10 | SKU-002 | Ferramenta | 25 | 100 | 3.75 |
| Dado M8 | SKU-003 | Ferramenta | 0 | 200 | 1.50 |
| Rondella | SKU-004 | Ferramenta | 3000 | 500 | 0.25 |

## 📝 Licenza

Questo progetto è distribuito sotto la licenza MIT.

## 🙏 Ringraziamenti

- [Streamlit](https://streamlit.io) per il framework web
- [Office365-REST-Python-Client](https://github.com/vgrem/Office365-REST-Python-Client) per l'integrazione SharePoint
- [ReportLab](https://www.reportlab.com/) per la generazione PDF
- [python-barcode](https://github.com/WhyNotHugo/python-barcode) per i codici a barre

---

**Warehouse AI Inventory System** v1.0.0 • Sviluppato con ❤️
