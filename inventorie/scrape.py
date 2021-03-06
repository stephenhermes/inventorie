from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
import json
from typing import Protocol, Optional

from bs4 import BeautifulSoup  # type: ignore
from bs4.element import Tag  # type: ignore
import pandas as pd  # type: ignore
import requests  # type: ignore


@dataclass
class ScrapeResult:
    manufacturer: Optional[str] = None
    manufacturer_product_id: Optional[str] = None
    product_category: Optional[str] = None
    supplier: Optional[str] = None
    datasheet_url: Optional[str] = None
    description: Optional[str] = None


class Scraper(Protocol):
    """Represents a supplier-specific web scraper."""

    def scrape(self, url: str) -> ScrapeResult:
        """Scrapes product information from provided url.

        Parameters
        ----------
        url : string
            The url for the particular product.

        Returns
        -------
        result : ScrapeResult
            The scraped data.

        """
        ...

    def update_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Updates a data frame of products to include scraped data for each product.

        Parameters
        ----------
        df : DataFrame
            A dataframe with a 'product_url' column.

        Returns
        -------
        df : DataFrame
            The original dataframe with missing fields (and columns) updated
            by scraped results for each product.

        """
        for new_col in ScrapeResult.__dataclass_fields__.keys():
            if new_col not in df.columns:
                df[new_col] = None

        with ThreadPoolExecutor() as executor:
            futures = {
                idx: executor.submit(self.scrape, row["product_url"])
                for idx, row in df.iterrows()
            }
            scrape_results = {idx: t.result() for idx, t in futures.items()}

        for idx, result in scrape_results.items():
            for col, val in result.__dict__.items():
                if df.at[idx, col] is not None:
                    continue
                df.at[idx, col] = val

        return df


class TaydaScraper(Scraper):
    """A `Scraper` for Tayda Electronics."""

    def scrape(self, url: str) -> ScrapeResult:
        resp = requests.get(url)
        if resp.status_code != 200:
            raise ValueError(f"Unable to find webpage {url}")
        soup = BeautifulSoup(resp.content, features="html.parser")
        specs = self._find_specs_table(soup)
        if specs is None:
            raise ValueError(f"Unable to find additional information from {url}")
        result = self._scrape_specs_table(specs)
        category_url = self._find_product_category_url(soup)
        result.product_category = self._scrape_product_category(category_url)
        result.datasheet_url = self._scrape_datasheet(soup)
        return result

    def _find_specs_table(self, soup: BeautifulSoup) -> Optional[Tag]:
        """Find the product specifications table."""
        tables = soup.find_all("table")
        for table in tables:
            if (
                table.attrs.get("id")
                and table.attrs["id"] == "product-attribute-specs-table"
            ):
                return table
        return None

    def _scrape_specs_table(self, table: Tag) -> ScrapeResult:
        """Scrape relevant data from product specification."""
        rows = table.find_all("tr")
        result = ScrapeResult(supplier="Tayda Electronics")
        for row in rows:
            field = row.td.attrs.get("data-th")
            if field == "Manufacturer":
                result.manufacturer = row.td.text.strip()
            if field == "MPN":
                result.manufacturer_product_id = row.td.text.strip()
        return result

    def _find_product_category_url(self, soup: BeautifulSoup) -> str:
        # The data is in the first "script" tag after the "bradcrumbs" div
        script = soup.find("div", {"class", "breadcrumbs"})
        while script.name != "script":
            script = script.next_sibling
        script_data = json.loads(script.text)
        return script_data[".breadcrumbs"]["breadcrumbs"]["categoryOverride"]

    def _scrape_product_category(self, url: str) -> str:
        resp = requests.get(url)
        if resp.status_code != 200:
            raise ValueError
        soup = BeautifulSoup(resp.content, features="html.parser")
        title = soup.find("span", {"data-ui-id": "page-title-wrapper"})
        return title.text.strip()

    def _scrape_datasheet(self, soup: BeautifulSoup) -> Optional[str]:
        info = soup.find("div", {"class": "product attribute description"})
        links = info.find_all("a")
        for l in links:
            if l.attrs.get("href"):
                link = l.attrs.get("href")
                if "taydaelectronics.com/datasheets/" in link:
                    return link
        return None


class JamecoScraper(Scraper):
    """A `Scraper` for Jameco Electronics."""

    def scrape(self, url: str) -> ScrapeResult:
        resp = requests.get(url)
        if resp.status_code != 200:
            raise ValueError(f"Unable to find webpage {url}")
        soup = BeautifulSoup(resp.content, features="html.parser")
        result = self._scrape_specs_table(soup)
        result.product_category = self._scrape_product_category(soup)
        result.description = self._scrape_product_description(soup)
        return result

    def _scrape_specs_table(self, soup: BeautifulSoup) -> ScrapeResult:
        result = ScrapeResult(supplier="Jameco Electronics")
        items = soup.find_all("li")
        for item in items:
            if item.strong and item.strong.text == "Manufacturer:":
                result.manufacturer = item.span.text.strip()
            if item.strong and item.strong.text == "Manufacturer no.:":
                result.manufacturer_product_id = item.span.text.strip()
        return result

    def _scrape_product_category(self, soup: BeautifulSoup) -> str:
        breadcrumb = soup.find("ol", {"class": "breadcrumb"})
        categories = breadcrumb.find_all("li")
        # Home, Category, Subcategory, Specific
        _, parent, *_ = [c.text.strip() for c in categories]
        return parent

    def _scrape_product_description(self, soup: BeautifulSoup) -> str:
        header = soup.find("h1")
        return header.text.strip()
