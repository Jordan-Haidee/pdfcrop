from dataclasses import dataclass
from pathlib import Path

import pymupdf as pf
import tyro
from typing_extensions import Annotated


@dataclass
class Config:
    input: Annotated[
        Path,
        tyro.conf.arg(aliases=["-i"], help="The input pdf file."),
    ]
    output: Annotated[
        Path | None, tyro.conf.arg(aliases=["-o"], help="The output path.")
    ] = None
    pages: Annotated[
        list[int] | None,
        tyro.conf.arg(help="The page numbers to crop. None denotes all pages."),
    ] = None
    margins: Annotated[
        list[int] | None,
        tyro.conf.arg(
            help="The margins to reserve. None denotes all 0. If one number is given, it will be applied to four borders."
        ),
    ] = None


def crop_page(p: pf.Page, margins: list[int]) -> pf.Page:
    blocks = p.get_text("dict")["blocks"]
    shapes = p.get_drawings()
    coordinates = []

    for b in blocks:
        coordinates.append(b["bbox"])

    for s in shapes:
        coordinates.append((s["rect"].x0, s["rect"].y0, s["rect"].x1, s["rect"].y1))

    x0 = min([p[0] for p in coordinates]) - margins[0]
    y0 = min([p[1] for p in coordinates]) - margins[2]
    x1 = max([p[2] for p in coordinates]) + margins[1]
    y1 = max([p[3] for p in coordinates]) + margins[3]

    p.set_cropbox(pf.Rect(x0, y0, x1, y1))

    return p


def main(config: Config):
    assert config.margins is None or len(config.margins) in (
        1,
        4,
    ), "margins number must be 1 or 4"
    if config.margins is None:
        margins = [0] * 4
    if len(margins) == 1:
        margins = margins * 4

    # breakpoint()
    doc = pf.open(str(config.input))
    for i, p in enumerate(doc.pages()):
        if config.pages is None or i in config.pages:
            crop_page(p, margins)

    if config.output is None:
        output_path = config.input.with_name(config.input.stem + "_cropped.pdf")
    else:
        output_path = config.output

    doc.save(output_path, deflate=True, garbage=4, clean=True)


def _main():
    config = tyro.cli(Config)
    main(config)


if __name__ == "__main__":
    _main()
