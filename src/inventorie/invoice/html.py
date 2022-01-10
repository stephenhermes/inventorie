import email
from pathlib import Path
import re
from typing import Union, Optional, Tuple

from bs4 import BeautifulSoup  # type: ignore
from bs4.element import Tag  # type: ignore
import pandas as pd  # type: ignore

from .reader import InventoryReader


class TaydaInventoryReader(InventoryReader):

    supplier = "Tayda Electronics"

    def read(self, file: Union[Path, str]) -> pd.DataFrame:
        body = self._read_email_body(file)
        table = self._get_inventory_table(body)
        if table is None:
            raise ValueError(f"Unable to extract table from {file}")
        df = self._parse_inventory_table(table)
        df["quantity"] = df["quantity"].astype(int)
        df["unit_price"] = df["unit_price"].astype(float)
        df["amount"] = df["unit_price"] * df["quantity"]
        return df

    def _read_email_body(self, email_file: Union[Path, str]) -> bytes:
        """Get the email text from `.eml` file."""
        with open(email_file, "r") as f:
            message = email.message_from_file(f)
        return message.get_payload(decode=True)

    def _get_inventory_table(self, body: bytes) -> Optional[Tag]:
        """Extract the inventory table from the email text."""
        soup = BeautifulSoup(body, "html.parser")
        tables = soup.find_all("table")
        for table in tables:
            if table.attrs.get("class") and "email-items" in table.attrs.get("class"):
                return table
        else:
            return None

    def _parse_inventory_row(self, row: Tag) -> Tuple[str, str, int, float]:
        """Extract information from single row in inventory table."""
        item, quantity, price = row.find_all("td")
        quantity = int(quantity.text.strip())
        price = price.text.strip().replace("$", "")
        description, sku = item.find_all("p")
        description = description.text.strip()
        sku_match = re.match("SKU: (.*)", sku.text.strip())
        sku = None
        if sku_match:
            sku = sku_match.groups()[0]
        return sku, description, quantity, price

    def _parse_inventory_table(self, table: Tag) -> pd.DataFrame:
        """Extract relevant information from inventory table."""
        rows = []
        for tb in table.find_all("tbody"):
            rows += tb.find_all("tr")
        rows = [self._parse_inventory_row(row) for row in rows]
        return pd.DataFrame(
            rows, columns=["product_id", "description", "quantity", "unit_price"]
        )
