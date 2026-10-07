"""SharePoint integration module for warehouse inventory data."""
import os

import pandas as pd
from dotenv import load_dotenv
from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext

# Load environment variables from .env file
load_dotenv()

# SharePoint configuration from environment
SITE_URL = os.getenv("SP_URL", "").strip()
USERNAME = os.getenv("SP_USER", "").strip()
PASSWORD = os.getenv("SP_PASS", "").strip()
LIST_NAME = os.getenv("SP_LIST_NAME", "Prodotti Magazzino").strip()


def _get_context() -> ClientContext:
    """Create and return a SharePoint ClientContext.

    Raises:
        ValueError: If required environment variables are not configured.

    Returns:
        ClientContext: Authenticated SharePoint context.
    """
    if not SITE_URL:
        raise ValueError(
            "SP_URL non configurato. Aggiungi la variabile d'ambiente SP_URL nel file .env."
        )
    if not USERNAME or not PASSWORD:
        raise ValueError(
            "SP_USER e SP_PASS non configurati. Controlla il file .env."
        )

    return ClientContext(SITE_URL).with_credentials(UserCredential(USERNAME, PASSWORD))


def get_sharepoint_data() -> pd.DataFrame:
    """Fetch inventory data from SharePoint List.

    Returns:
        pd.DataFrame: DataFrame with columns:
            - ID: Item ID
            - sku: Product SKU
            - name: Product name
            - category: Product category
            - stock: Current stock
            - reorder_point: Reorder threshold
            - unit_price: Unit price in EUR

    Raises:
        ValueError: If SharePoint connection fails.
    """
    ctx = _get_context()
    sp_list = ctx.web.lists.get_by_title(LIST_NAME)
    items = sp_list.items.get().execute_query()

    rows = []
    for item in items:
        props = item.properties
        rows.append(
            {
                "ID": int(props.get("Id", 0) or 0),
                "sku": str(props.get("SKU", "") or ""),
                "name": str(props.get("Title", "") or ""),
                "category": str(props.get("Category", "") or ""),
                "stock": float(props.get("Stock", 0) or 0),
                "reorder_point": float(props.get("ReorderPoint", 0) or 0),
                "unit_price": float(props.get("UnitPrice", 0) or 0),
            }
        )

    return pd.DataFrame(rows)


def update_stock_in_sharepoint(item_id: int, new_stock: float) -> None:
    """Update stock quantity for a product in SharePoint.

    Args:
        item_id: SharePoint item ID
        new_stock: New stock quantity

    Raises:
        ValueError: If SharePoint connection fails.
    """
    ctx = _get_context()
    sp_list = ctx.web.lists.get_by_title(LIST_NAME)
    item = sp_list.items.get_by_id(item_id)
    item.set_property("Stock", float(new_stock))
    item.update()
    ctx.execute_query()
