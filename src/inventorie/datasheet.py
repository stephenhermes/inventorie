from typing import Protocol

import pandas as pd  # type: ignore
import requests  # type: ignore


class DatasheetLookup(Protocol):
    """Protocol for generating links to datasheets for product."""

    supplier: str

    def lookup(self, product_id: str, validate: bool = False) -> str:
        """Get datasheet for product.

        Parameters
        ----------
        product_id : str
            The product ID for the product to look up datasheet.

        validate : bool, optional, default=False
            Whether or not to query the found website to verify that
            it is an active link. If `False` will raise a `ValueError`.

        Returns
        -------
        url : str
            A url to the product datasheet.
        """
        ...

    def update_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        if "datasheet_url" not in df.columns:
            df["datasheet_url"] = None
        for idx, row in df.iterrows():
            if row["datasheet_url"] is not None:
                continue
            datasheet_url = self.lookup(row["product_id"])
            df.at[idx, "datasheet_url"] = datasheet_url
        return df

    def _validate(self, url: str):
        resp = requests.get(url)
        if resp.status_code != 200:
            raise ValueError(f"No datasheet available at {url}.")


class TaydaDatasheetLookup(DatasheetLookup):

    supplier = "Tayda Electronics"

    # TODO: This has changed. Should be scraped from product webpage
    DATASHEET_URL = "https://www.taydaelectronics.com/datasheets/{}.pdf"

    def lookup(self, product_id: str, validate: bool = False) -> str:
        datasheet_url = self.DATASHEET_URL.format(product_id)
        if validate:
            self._validate(datasheet_url)
        return datasheet_url


class JamecoDatasheetLookup(DatasheetLookup):

    supplier = "Jameco Electronics"

    DATASHEET_URL = "https://www.jameco.com/Jameco/Products/ProdDS/{}.pdf"

    def lookup(self, product_id: str, validate: bool = False) -> str:
        datasheet_url = self.DATASHEET_URL.format(product_id)
        if validate:
            self._validate(datasheet_url)
        return datasheet_url
