"""This script formats FORTRAN namelist in place"""

import pathlib
import argparse
import re


def find_longest_key(content: str) -> int:
    """
    Find the length of the longest key in Fortran-namelist-style variable assignments.

    Parameters
    ----------
    content : str
        The full text content of the namelist file as a single string.

    Returns
    -------
    int
        The length of the longest variable key (the string before '=') found in the input content.
        Returns -1 if no keys are found.

    Notes
    -----
    This function uses `parse_key_val_pair` to identify lines containing key-value pairs.
    It ignores comment lines and lines that do not contain assignments.
    """
    longest_key = -1
    for line in content.splitlines():
        # Parse line
        try:
            key, _, _ = parse_key_val_pair(line)
        except ValueError:
            continue

        # Overwrite longest key
        if len(key) > longest_key:
            longest_key = len(key)

    return longest_key


def parse_key_val_pair(line: str) -> tuple[str, str, str]:
    """
    Parse a Fortran namelist assignment line into (key, value_string, comment_string).

    Parameters
    ----------
    line : str
        A line of text from a Fortran namelist, typically of the form
        "key = value[,] [! comment]"

    Returns
    -------
    tuple[str, str, str]
        key : str
            The name of the variable being assigned (lowercased).
        value : str
            The value(s) assigned to the key; not type-converted, just as string.
        comment : str
            If present, the trailing comment, including the initial '! ' and with leading/trailing
            whitespace stripped. Returns empty string if no comment.

    Raises
    ------
    ValueError
        If the input line does not contain a valid key-value assignment.
    """
    comment = ""
    value_part = line

    # Comment handling
    if "!" in line:
        value_part, comment = line.split("!", 1)
        comment = " ! " + comment.strip()

    # Regex: Split on the first '=' with optional whitespace, allow leading comma
    eq_match = re.match(r"\s*,?\s*([^\s=]+)\s*=+(.*)", value_part)
    if eq_match:
        key = eq_match.group(1)
        value = eq_match.group(2).rstrip(", \t")
        return key, value.strip(), comment
    else:
        raise ValueError(f"No key matched in {line}")


def format_line(
    line: str,
    align_eq_to: int,
    block_indent: int,
    trailing_comma: bool,
    keep_comments: bool,
) -> str:
    """
    Format a Fortran namelist assignment line with proper alignment, indentation,
    comma, and optional comment retention.

    Parameters
    ----------
    line : str
        The original line containing a key-value assignment.
    align_eq_to : int
        The column at which to align the equal sign '='.
    block_indent : int
        The number of spaces to prepend to the formatted line.
    trailing_comma : bool
        Whether to put a comma after the value.
    keep_comments : bool
        Whether to retain comments at the end of the line.

    Returns
    -------
    str
        The line formatted according to the specified options.
    """
    TRUE_REPR = [".t.", ".TRUE."]
    FALSE_REPR = [".f.", ".FALSE."]

    # Parse line into key, value, and comment
    key, value, comment = parse_key_val_pair(line)

    # For value lists, ensure uniform whitespace after commas
    if "," in value:
        value = ", ".join([item.strip() for item in value.split(",")])

    # Convert booleans to same format
    for bool_str in TRUE_REPR:
        value = value.replace(bool_str, ".true.")
    for bool_str in FALSE_REPR:
        value = value.replace(bool_str, ".false.")

    # Standardize quotation marks to single quotes
    value = value.replace('"', "'")

    # Calculate spaces for alignment
    eq_offset = max(align_eq_to - len(key) - 1, 1)

    # Compose output pieces
    out_comment = comment if keep_comments else ""
    out_comma = "," if trailing_comma else ""

    return (
        f"{' ' * block_indent}{key}{' ' * eq_offset} = {value}{out_comma}{out_comment}"
    )


def format_nml(
    path_to_nml: pathlib.Path,
    eq_offset: int,
    block_indent: int,
    trailing_comma: bool,
    keep_comments: bool,
    keep_whitelines: bool,
) -> str:
    """
    Format a Fortran namelist file with custom alignment and style options.

    Parameters
    ----------
    path_to_nml : pathlib.Path
        Path to the Fortran namelist file to be formatted.
    eq_offset : int
        Additional number of spaces to add after the longest key before the equal sign for alignment.
    block_indent : int
        Number of spaces to indent variables inside namelist blocks.
    trailing_comma : bool
        If True, retain a comma at the end of each key-value line.
    keep_comments : bool
        If True, preserve full-line and inline comments.
    keep_whitelines : bool
        If True, preserve blank lines (whitelines) inside namelist blocks.

    Returns
    -------
    str
        The formatted namelist file content as a string.

    Notes
    -----
    - Each assignment line is realigned so that the equal signs in each block line up according to the longest key.
    - Comments and blanklines can be controlled via `keep_comments` and `keep_whitelines`, respectively.
    - Supports preserving block structure, full-line comments, and optionally trailing commas.
    """

    # Read nml
    nml_content = path_to_nml.read_text()

    # Find longest key
    longest_key = find_longest_key(nml_content)
    align_eq_to = longest_key + eq_offset

    # Format the lines accordingly
    in_block = False
    mod_lines = []
    for line in nml_content.splitlines():
        # Remove \n and trailing spaces
        line = line.strip("\n")
        line = line.rstrip()

        # Check whether inside a block (namelist start)
        if line.strip().startswith("&"):
            in_block = True
            mod_lines.append(line.strip().lower())
            continue

        # Check whether outside a block (namelist end)
        if line.strip() == "/":
            in_block = False
            mod_lines.append(line.strip())
            mod_lines.append("")
            continue

        # Keep whitelines in block if wanted
        if line == "":
            if keep_whitelines and in_block:
                mod_lines.append(line)
            else:
                continue

        # Full line comments
        elif line.strip().startswith("!"):
            if keep_comments:
                indent = "" if not in_block else " " * block_indent
                mod_lines.append(indent + "! " + line.strip()[1:].strip())
            else:
                continue

        # Inside block
        else:
            mod_lines.append(
                format_line(
                    line, align_eq_to, block_indent, trailing_comma, keep_comments
                )
            )

    return "\n".join(mod_lines)


if __name__ == "__main__":
    # CLI parser configuration
    parser = argparse.ArgumentParser(
        description=(
            "Format a FORTRAN namelist file. To avoid formatting in place "
            "use --output option."
        ),
    )
    parser.add_argument(
        "namelist",
        type=pathlib.Path,
        help="Path to the FORTRAN namelist file to format",
    )
    parser.add_argument(
        "--output",
        type=pathlib.Path,
        default=None,
        help=(
            "Optional output path. "
            "If not given, the input namelist is overwritten in place."
        ),
    )
    parser.add_argument(
        "--block-indentation",
        type=int,
        default=2,
        help="Number of spaces to indent variables inside a block (default: 2)",
    )
    parser.add_argument(
        "--eq-offset",
        type=int,
        default=5,
        help="Number of spaces after longest key before the '=' sign (default: 5)",
    )
    parser.add_argument(
        "--no-trailing-comma",
        dest="trailing_comma",
        action="store_false",
        default=True,
        help="Remove trailing commas at end of assignments",
    )
    parser.add_argument(
        "--no-keep-comments",
        dest="keep_comments",
        action="store_false",
        default=True,
        help="Remove all comments from output",
    )
    parser.add_argument(
        "--no-keep-whitelines",
        dest="keep_whitelines",
        action="store_false",
        default=True,
        help="Remove whitelines inside blocks",
    )

    # PROGRAM
    # Parse arguments
    args = parser.parse_args()

    # Format namelist
    formatted_lines = format_nml(
        args.namelist,
        eq_offset=args.eq_offset,
        block_indent=args.block_indentation,
        trailing_comma=args.trailing_comma,
        keep_comments=args.keep_comments,
        keep_whitelines=args.keep_whitelines,
    )

    # Safety check
    if args.output is not None and args.output.resolve() == args.namelist.resolve():
        raise ValueError("Output path cannot be identical to namelist path.")

    # Determine output path
    output_path = args.output if args.output is not None else args.namelist

    # Write result
    output_path.write_text(formatted_lines, encoding="utf-8")
