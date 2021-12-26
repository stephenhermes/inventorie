from pathlib import Path
import re
from typing import Union, Optional

import pandas as pd                                 # type: ignore
from pdfreader import SimplePDFViewer               # type: ignore
from pdfreader.types.objects import Annot           # type: ignore
import tabula                                       # type: ignore

from .reader import InventoryReader


class JamecoInventoryReader(InventoryReader):

    def read(self, file: Union[Path, str]) -> pd.DataFrame:
        df = self.read_pdf_table(file)
        if df is None:
            raise ValueError(
                f"Unable to read table from {file}"
            )
        links = self.read_product_links(file)
        df['link'] = df['item_number'].map(links)
        return df


    def read_pdf_table(self, pdf_file: Union[Path, str]) -> Optional[pd.DataFrame]:
        dfs = tabula.read_pdf(pdf_file, pages='all')
        for df in dfs:
            if 'Description' in df:
                df.dropna(inplace=True)
                df.reset_index(inplace=True, drop=True)
                df.columns = ['item_number', 'manufacturer_part_number', 'description', 
                    'quantity', 'unit', 'unit_price', 'amount']
                df['item_number'] = df['item_number'].astype(int).astype(str)
                return df
        else:
            return None


    def parse_link_annotation(self, annot: Annot) -> str:
        link = annot['A']['URI'].decode('utf-8')
        return link


    def extract_product_id(self, link):
        match = re.match('.*\&productId=(\d+)', link)
        if match:
            return match.groups()[0]
        return None


    def read_product_links(self, pdf_file: Union[Path, str]) -> dict:

        with open(pdf_file,'rb') as f:
            viewer = SimplePDFViewer(f)
            link_annotations = [
                annot for annot in viewer.annotations 
                if annot.get('Subtype') == 'Link'
            ]

        links = [self.parse_link_annotation(a) for a in link_annotations]
        return {self.extract_product_id(l): l for l in links}
