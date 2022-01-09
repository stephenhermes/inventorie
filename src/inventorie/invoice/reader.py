from pathlib import Path
from typing import Union, Protocol

import pandas as pd  # type: ignore


class InventoryReader(Protocol):

    supplier: str

    def read(self, file: Union[Path, str]) -> pd.DataFrame:
        ...
