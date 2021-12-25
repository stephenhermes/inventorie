import email
from pathlib import Path
import re
from typing import Union, Optional, Tuple

from bs4 import BeautifulSoup   # type: ignore                 
from bs4.element import Tag     # type: ignore
import pandas as pd             # type: ignore

EMAIL_SUPPLIERS = ['Tayda Electronics']


def detect_supplier_from_email(email_file):
    with open(email_file, 'r') as f:
        message = email.message_from_file(f)
    payload = message.get_payload(decode=True)
    for supplier in EMAIL_SUPPLIERS:
        if supplier in payload:
            return supplier
    return None


class TaydaInventoryReader:
    
    def read(self, file: Union[Path, str]) -> pd.DataFrame:
        body = self.read_email_body(file)
        table = self.get_inventory_table(body)
        if table is None:
            raise ValueError(
                f"Unable to extract table from {file}"
            )
        return self.parse_inventory_table(table)


    def read_email_body(self, email_file: Union[Path, str]) -> bytes:
        with open(email_file, 'r') as f:
            message = email.message_from_file(f)
        return message.get_payload(decode=True)


    def get_inventory_table(self, body: bytes) -> Optional[Tag]:
        soup = BeautifulSoup(body, 'html.parser')
        tables = soup.find_all('table')
        for table in tables:
            if (table.attrs.get('class') and 
                'email-items' in table.attrs.get('class')):
                return table
        else:
            return None


    def parse_inventory_row(self, row: Tag) -> Tuple[str, str, int, float]:
        item, quantity, price = row.find_all('td')
        quantity = int(quantity.text.strip())
        price = price.text.strip().replace('$', '')
        description, sku = item.find_all('p')
        description = description.text.strip()
        sku_match = re.match('SKU: (.*)', sku.text.strip())
        sku = None
        if sku_match:
            sku = sku_match.groups()[0]
        return sku, description, quantity, price


    def parse_inventory_table(self, table: Tag) -> pd.DataFrame:
        rows = []
        for tb in table.find_all('tbody'):
            rows += tb.find_all('tr')
        rows = [self.parse_inventory_row(row) for row in rows]
        return pd.DataFrame(rows, 
            columns=['item_number', 'description', 'quantity', 'unit_price'])
