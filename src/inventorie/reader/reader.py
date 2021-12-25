from pathlib import Path
from typing import Union, Protocol 

from pandas import pd   # type: ignore


class InventoryReader(Protocol):

    def read(self, file: Union[Path, str]) -> pd.DataFrame:
        ...
