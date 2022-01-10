from dataclasses import dataclass
import email
from enum import Enum
from pathlib import Path
from typing import Union, Optional, Dict, List, Tuple

from pdfreader import SimplePDFViewer  # type: ignore

from invoice import InventoryReader, JamecoInventoryReader, TaydaInventoryReader
from pipeline import Pipeline
from datasheet import JamecoDatasheetLookup
from product import TaydaProductLookup
from scrape import TaydaScraper, JamecoScraper


class SUPPLIER(Enum):
    JAMECO = "Jameco Electronics"
    TAYDA = "Tayda Electronics"


SUPPLIER_FILE_TYPES: Dict[SUPPLIER, List[str]] = {
    SUPPLIER.TAYDA: [".eml"],
    SUPPLIER.JAMECO: [".pdf"],
}

READERS: Dict[Tuple[SUPPLIER, str], InventoryReader] = {
    (SUPPLIER.TAYDA, ".eml"): TaydaInventoryReader(),
    (SUPPLIER.JAMECO, ".pdf"): JamecoInventoryReader(),
}

PIPELINES: Dict[Tuple[SUPPLIER, str], Pipeline] = {
    (SUPPLIER.TAYDA, ".eml"): Pipeline(
        TaydaInventoryReader(),
        TaydaProductLookup(),
        TaydaScraper(),
    ),
    (SUPPLIER.JAMECO, ".pdf"): Pipeline(
        JamecoInventoryReader(), JamecoDatasheetLookup(), JamecoScraper()
    ),
}


def detect_supplier_from_pdf(pdf_file: Union[str, Path]) -> Optional[SUPPLIER]:
    with open(pdf_file, "rb") as f:
        viewer = SimplePDFViewer(f)
        for canvas in viewer:
            for supplier, file_types in SUPPLIER_FILE_TYPES.items():
                if ".pdf" not in file_types:
                    continue
                if supplier.value in canvas.strings:
                    return supplier
    return None


def detect_supplier_from_email(email_file: Union[str, Path]) -> Optional[SUPPLIER]:
    with open(email_file, "r") as f:
        message = email.message_from_file(f)
    payload = message.get_payload(decode=True).decode("utf-8")
    for supplier, file_types in SUPPLIER_FILE_TYPES.items():
        if ".eml" not in file_types:
            continue
        if supplier.value in payload:
            return supplier
    return None


def detect_supplier_from_file(file: Path) -> Optional[SUPPLIER]:
    PARSERS = {".pdf": detect_supplier_from_pdf, ".eml": detect_supplier_from_email}
    file_type = file.suffix
    if file_type not in set(ft for v in SUPPLIER_FILE_TYPES.values() for ft in v):
        raise ValueError(f"Cannot parse from file of type {file_type}")
    parser = PARSERS[file_type]
    return parser(file)


def get_reader_from_file(file: Path) -> InventoryReader:
    supplier = detect_supplier_from_file(file)
    if supplier is None:
        raise ValueError(f"Unable to detect supplier from {file}.")
    return READERS[(supplier, file.suffix)]


def get_pipeline_from_file(file: Path) -> Pipeline:
    supplier = detect_supplier_from_file(file)
    if supplier is None:
        raise ValueError(f"Unable to detect supplier from {file}.")
    return PIPELINES[(supplier, file.suffix)]
