from typing import Protocol, Union
from pathlib import Path

import pandas as pd  # type: ignore

from .invoice.reader import InventoryReader


class Chainable(Protocol):
    def update_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        ...


class Pipeline:
    def __init__(self, reader: InventoryReader, *steps: Chainable):
        """Represents a sequence of scraping and file parsing steps.

        Parameters
        ----------
        reader : InventoryReader
            A reader for reading in raw data from an invoice.

        steps : Chainable
            The steps for postprocessing the raw invoice.
            Each `step` in `steps` should follow the `Chainable` protocol.

        """
        self.reader = reader
        self.steps = steps

    def process(self, file: Union[Path, str]) -> pd.DataFrame:
        """Read and process an invoice.

        The pipeline reads in an invoice file as a dataframe and sequentially
        updates and adds fields, as per the provided `steps`.

        Parameters
        ----------
        file : string or Path
            The invoice to run the pipeline on.

        Returns
        -------
        df : DataFrame
            The dataframe obtained by applying the various transformations.

        """
        df = self.reader.read(file)
        for step in self.steps:
            df = step.update_dataframe(df)
        return df
