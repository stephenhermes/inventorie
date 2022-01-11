from pathlib import Path
from typing import Union, Protocol

import pandas as pd  # type: ignore


class InventoryReader(Protocol):
    """Protocol for reading in invoices."""

    supplier: str

    def read(self, file: Union[Path, str]) -> pd.DataFrame:
        """Read data from raw invoice file into a dataframe.

        Parameters
        file : string or Path
            The file of the invoice to read.

        Returns
        -------
        df : DataFrame
            Invoice data as a dataframe.

        """
        ...
