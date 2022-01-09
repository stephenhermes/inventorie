from typing import Protocol

import pandas as pd  # type: ignore
import requests  # type: ignore


class ProductLookup(Protocol):
    """Class for finding a product webpage."""

    supplier: str

    def lookup(self, product_id: str) -> str:
        """Get webpage for product.

        Parameters
        ----------
        product_id : str
            The product id for the product to look up. This is supplier specific.

        Returns
        -------
        url : str
            The url for the product.
        """
        ...

    def update_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Finds urls for each product in a dataframe.

        If there is no column for 'product_url' then one will be appended.

        Parameters
        ----------
        df : DataFrame
            A dataframe with a column for 'product_id'

        Returns
        -------
        updated_df : DataFrame
            Dataframe with column for 'product_url'.

        """
        ...


class TaydaProductLookup:

    supplier = "Tayda Electronics"

    SEARCH_URL = "https://www.taydaelectronics.com/catalogsearch/result/?q={}"

    def lookup(self, product_id: str) -> str:
        query_url = self.SEARCH_URL.format(product_id)
        resp = requests.get(query_url)
        if resp.status_code != 200:
            raise ValueError(f"Unable to find webpage for {product_id}")
        # Should redirect if single product found.
        if not resp.history:
            raise ValueError(f"Found multiple results for {product_id}.")
        return resp.url

    def update_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        if "product_url" not in df.columns:
            df["product_url"] = None
        for idx, row in df.iterrows():
            if row["product_url"] is not None:
                continue
            product_url = self.lookup(row["product_id"])
            df.at[idx, "product_url"] = product_url
        return df
