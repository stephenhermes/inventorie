from pathlib import Path
import re
from typing import Union, Optional

import pandas as pd  # type: ignore
from pdfreader import SimplePDFViewer  # type: ignore
from pdfreader.types.objects import Annot  # type: ignore
import tabula  # type: ignore

from .reader import InventoryReader


class JamecoInventoryReader(InventoryReader):

    supplier = "Jameco Electronics"

    def read(self, file: Union[Path, str]) -> pd.DataFrame:
        df = self._read_pdf_table(file)
        if df is None:
            raise ValueError(f"Unable to read table from {file}")
        links = self._read_product_links(file)
        df["product_url"] = df["product_id"].map(links)
        return df

    def _read_pdf_table(self, pdf_file: Union[Path, str]) -> Optional[pd.DataFrame]:
        # TODO: Tabula misses portions of descriptions on new lines...
        dfs = tabula.read_pdf(pdf_file, pages="all")
        for df in dfs:
            if "Description" in df:
                df.dropna(inplace=True)
                df.reset_index(inplace=True, drop=True)
                df.columns = [
                    "product_id",
                    "manufacturer_product_id",
                    "description",
                    "quantity",
                    "unit",
                    "unit_price",
                    "amount",
                ]
                df["product_id"] = df["product_id"].astype(int).astype(str)
                return df
        else:
            return None

    def _parse_link_annotation(self, annot: Annot) -> str:
        link = annot["A"]["URI"].decode("utf-8")
        return link

    def _extract_product_id(self, link):
        match = re.match(".*\&productId=(\d+)", link)
        if match:
            return match.groups()[0]
        return None

    def _read_product_links(self, pdf_file: Union[Path, str]) -> dict:

        with open(pdf_file, "rb") as f:
            viewer = SimplePDFViewer(f)
            link_annotations = [
                a for a in viewer.annotations if a.get("Subtype") == "Link"
            ]

        links = [self._parse_link_annotation(a) for a in link_annotations]
        return {self._extract_product_id(l): l for l in links}
