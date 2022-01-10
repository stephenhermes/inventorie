from argparse import ArgumentParser
from pathlib import Path
from typing import Union, Optional

import pandas as pd  # type: ignore

from supplier import get_pipeline_from_file


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


def main(workdir: Path, output: Optional[Path]):

    print(f"Working in {workdir.resolve()}")
    dfs = []
    for file in workdir.glob("*"):
        if file.suffix not in (".pdf", ".eml"):
            continue
        print(f"Processing {file.name}")
        pipeline = get_pipeline_from_file(file)
        df = pipeline.process(file)
        dfs.append(df)

    df = pd.concat(dfs)
    df.reset_index(inplace=True, drop=True)
    print("Done")

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


if __name__ == "__main__":
    args = get_args()
    flags = args.parse_args()
    main(flags.workdir, flags.output)
