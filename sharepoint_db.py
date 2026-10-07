import os
import pandas as pd
from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.user_credential import UserCredential

SITE_URL = "https://tuodominio.sharepoint.com/sites/NomeSito"
USERNAME = os.getenv("SP_USER", "utente@aziendadominio.com")
PASSWORD = os.getenv("SP_PASS", "tua_password")
LIST_NAME = "Prodotti Magazzino"

def get_sharepoint_data() -> pd.DataFrame:
    ctx = ClientContext(SITE_URL).with_credentials(UserCredential(USERNAME, PASSWORD))
    sp_list = ctx.web.lists.get_by_title(LIST_NAME)
    items = sp_list.items.get().execute_query()
    
    data = []
    for item in items:
        data.append({
            'ID': item.properties['Id'],
            'sku': item.properties.get('SKU', ''),
            'name': item.properties.get('Title', ''),
            'category': item.properties.get('Category', ''),
            'stock': float(item.properties.get('Stock', 0)),
            'reorder_point': float(item.properties.get('ReorderPoint', 0)),
            'unit_price': float(item.properties.get('UnitPrice', 0))
        })
    return pd.DataFrame(data)

def update_stock_in_sharepoint(item_id: int, new_stock: float):
    ctx = ClientContext(SITE_URL).with_credentials(UserCredential(USERNAME, PASSWORD))
    sp_list = ctx.web.lists.get_by_title(LIST_NAME)
    item = sp_list.items.get_by_id(item_id)
    item.set_property("Stock", new_stock)
    item.update()
    ctx.execute_query()