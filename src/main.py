import pymupdf as pf
import argparse
from pathlib import Path


def crop_page(p: pf.Page) -> pf.Page:
    blocks = p.get_text("dict")["blocks"]
    shapes = p.get_drawings()
    coordinates = []

    for b in blocks:
        coordinates.append(b["bbox"])

    for s in shapes:
        coordinates.append((s["rect"].x0, s["rect"].y0, s["rect"].x1, s["rect"].y1))

    x0 = min([p[0] for p in coordinates])
    y0 = min([p[1] for p in coordinates])
    x1 = max([p[2] for p in coordinates])
    y1 = max([p[3] for p in coordinates])

    p.set_cropbox(pf.Rect(x0, y0, x1, y1))

    return p


def main():
    parser = argparse.ArgumentParser(
        description="An experimental alternative of TeX/pdfcrop tool"
    )
    parser.add_argument("--input", "-i", required=True)
    parser.add_argument("--output", "-o")
    args = parser.parse_args()

    doc = pf.open(args.input)
    for p in doc.pages():
        crop_page(p)

    input_path = Path(args.input)
    if args.output is None:
        output_path = input_path.with_name(input_path.stem + "_cropped.pdf")
    else:
        output_path = args.output

    doc.save(output_path, deflate=True, garbage=4, clean=True)


if __name__ == "__main__":
    main()
