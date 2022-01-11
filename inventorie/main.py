from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Dict, Optional

import pandas as pd  # type: ignore

from .supplier import get_pipeline_from_file
from .pipeline import Pipeline


COLUMNS = [
    "manufacturer_product_id",
    "manufacturer",
    "product_id",
    "supplier",
    "product_category",
    "description",
    "product_url",
    "datasheet_url",
    "quantity",
    "unit",
    "unit_price",
    "amount",
]


def get_args() -> ArgumentParser:
    parser = ArgumentParser()
    parser.add_argument(
        "workdir", help="directory containing files to process", type=Path
    )
    parser.add_argument(
        "--output",
        "-o",
        help="where to output the parsed data",
        type=Path,
        required=False,
    )
    return parser


def get_file_pipelines(workdir: Path) -> Dict[Path, Pipeline]:
    pipelines = {}
    for file in workdir.glob("*"):
        if file.suffix not in (".pdf", ".eml"):
            continue
        try:
            pipelines[file] = get_pipeline_from_file(file)
        except ValueError:
            print(f"No parser found for {file.name}")
            continue
    return pipelines


def main(workdir: Path, output: Optional[Path]):
    def _process_file(pipeline: Pipeline, file: Path) -> pd.DataFrame:
        print(f"Processing {file.name}")
        return pipeline.process(file)

    print(f"Working in {workdir.resolve()}")

    pipelines = get_file_pipelines(workdir)
    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(_process_file, pipeline, file)
            for file, pipeline in pipelines.items()
        ]
        df = pd.concat([future.result() for future in futures])
    df.reset_index(inplace=True, drop=True)
    print("Done")

    df = df[COLUMNS]

    if output:
        df.to_csv(output, index=False)
        return

    pd.set_option(
        "display.max_rows",
        None,
        "display.max_columns",
        None,
        "display.max_colwidth",
        None,
    )
    print(df)


def run_script():
    args = get_args()
    flags = args.parse_args()
    main(flags.workdir, flags.output)


if __name__ == "__main__":
    run_script()
