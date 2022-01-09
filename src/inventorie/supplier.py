from dataclasses import dataclass
import email
from enum import Enum
from pathlib import Path
from typing import Union, Optional

from pdfreader import SimplePDFViewer  # type: ignore

from invoice import InventoryReader, JamecoInventoryReader, TaydaInventoryReader
from pipeline import Pipeline
from datasheet import TaydaDatasheetLookup, JamecoDatasheetLookup
from product import TaydaProductLookup
from scrape import TaydaScraper, JamecoScraper


@dataclass
class Supplier:
    name: str
    file_type: str


class SUPPLIER(Enum):
    JAMECO = Supplier("Jameco Electronics", ".pdf")
    TAYDA = Supplier("Tayda Electronics", ".eml")


READERS = {
    SUPPLIER.TAYDA: TaydaInventoryReader(),
    SUPPLIER.JAMECO: JamecoInventoryReader(),
}

PIPELINES = {
    SUPPLIER.TAYDA: Pipeline(
        TaydaInventoryReader(),
        TaydaProductLookup(),
        TaydaDatasheetLookup(),
        TaydaScraper(),
    ),
    SUPPLIER.JAMECO: Pipeline(
        JamecoInventoryReader(), JamecoDatasheetLookup(), JamecoScraper()
    ),
}


def detect_supplier_from_pdf(pdf_file: Union[str, Path]) -> Optional[SUPPLIER]:
    with open(pdf_file, "rb") as f:
        viewer = SimplePDFViewer(f)
        for canvas in viewer:
            for supplier in SUPPLIER:
                if supplier.value.file_type != ".pdf":
                    continue
                if supplier.value.name in canvas.strings:
                    return supplier
    return None


def detect_supplier_from_email(email_file: Union[str, Path]) -> Optional[SUPPLIER]:
    with open(email_file, "r") as f:
        message = email.message_from_file(f)
    payload = message.get_payload(decode=True).decode("utf-8")
    for supplier in SUPPLIER:
        if supplier.value.file_type != ".eml":
            continue
        if supplier.value.name in payload:
            return supplier
    return None


def detect_supplier_from_file(file: Union[str, Path]) -> Optional[SUPPLIER]:
    PARSERS = {".pdf": detect_supplier_from_pdf, ".eml": detect_supplier_from_email}
    if not hasattr(file, "suffix"):
        file = Path(file)
    file_type = file.suffix
    if file_type not in [s.value.file_type for s in SUPPLIER]:
        raise ValueError(f"Cannot parse from file of type {file_type}")
    parser = PARSERS[file_type]
    return parser(file)


def get_reader_from_file(file: Union[str, Path]) -> InventoryReader:
    supplier = detect_supplier_from_file(file)
    if supplier is None:
        raise ValueError(f"Unable to detect supplier from {file}.")

    return READERS[supplier]


def get_pipeline_from_file(file: Union[str, Path]) -> Pipeline:
    supplier = detect_supplier_from_file(file)
    if supplier is None:
        raise ValueError(f"Unable to detect supplier from {file}.")

    return PIPELINES[supplier]
