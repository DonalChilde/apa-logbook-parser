#!/usr/bin/env python

import argparse
from pathlib import Path
from xml.dom.minidom import parse

parser = argparse.ArgumentParser(description="format an xml file.")

parser.add_argument("input_path", type=str, help="input path for the xml file.")
parser.add_argument("output_path", type=str, help="output path for the xml file.")


def format_xml(input_path: Path, output_path: Path):
    file_in_str = str(input_path)
    dom = parse(file=file_in_str)
    with open(output_path, mode="w", encoding="utf-8") as output:
        output.write(dom.toprettyxml(indent="  ", newl="\n"))


def remove_blank_lines(input_path: Path, output_path: Path):
    with open(input_path, encoding="utf-8") as file_in, open(
        output_path, "w", encoding="utf-8"
    ) as file_out:
        for line in file_in:
            if line.strip():
                file_out.write(line)


if __name__ == "__main__":
    args = parser.parse_args()
    path_in = Path(args.input_path)
    path_out = Path(args.output_path)
    temp_out = path_out.with_suffix(".temp")
    format_xml(path_in, temp_out)
    remove_blank_lines(temp_out, path_out)
    temp_out.unlink()
