from typing import Protocol, List, Union
from pathlib import Path

import pandas as pd  # type: ignore

from invoice.reader import InventoryReader


class Chainable(Protocol):
    def update_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        ...


class Pipeline:
    def __init__(self, reader: InventoryReader, *steps: Chainable):
        self.reader = reader
        self.steps = steps

    def process(self, file: Union[Path, str]) -> pd.DataFrame:
        df = self.reader.read(file)
        for step in self.steps:
            df = step.update_dataframe(df)
        return df
