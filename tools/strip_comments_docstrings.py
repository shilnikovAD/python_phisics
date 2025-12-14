"""Strip comments and docstrings from Python files safely.

Usage:
    python tools/strip_comments_docstrings.py --files <file1> <file2> ...
    python tools/strip_comments_docstrings.py --dir puthon_2hw/endpoints --backup

This script creates .bak copies before modifying files.
"""

import argparse
import ast
import os
from typing import List


def remove_docstrings(source: str) -> str:
    try:
        parsed = ast.parse(source)
    except Exception:
        return source

    class DocstringRemover(ast.NodeTransformer):
        def visit_FunctionDef(self, node):
            self.generic_visit(node)
            if (
                node.body
                and isinstance(node.body[0], ast.Expr)
                and isinstance(node.body[0].value, ast.Constant)
                and isinstance(node.body[0].value.value, str)
            ):
                node.body.pop(0)
            return node

        def visit_AsyncFunctionDef(self, node):
            self.generic_visit(node)
            if (
                node.body
                and isinstance(node.body[0], ast.Expr)
                and isinstance(node.body[0].value, ast.Constant)
                and isinstance(node.body[0].value.value, str)
            ):
                node.body.pop(0)
            return node

        def visit_ClassDef(self, node):
            self.generic_visit(node)
            if (
                node.body
                and isinstance(node.body[0], ast.Expr)
                and isinstance(node.body[0].value, ast.Constant)
                and isinstance(node.body[0].value.value, str)
            ):
                node.body.pop(0)
            return node

        def visit_Module(self, node):
            self.generic_visit(node)
            if (
                node.body
                and isinstance(node.body[0], ast.Expr)
                and isinstance(node.body[0].value, ast.Constant)
                and isinstance(node.body[0].value.value, str)
            ):
                node.body.pop(0)
            return node

    try:
        new_tree = DocstringRemover().visit(parsed)
        ast.fix_missing_locations(new_tree)
        new_source = ast.unparse(new_tree)
    except Exception:
        return source
    return new_source


def remove_full_line_comments(source: str) -> str:
    lines = source.splitlines()
    out_lines = []
    for line in lines:
        stripped = line.lstrip()
        if stripped.startswith("#"):
            # skip full-line comment
            continue
        out_lines.append(line)
    return "\n".join(out_lines) + ("\n" if source.endswith("\n") else "")


def process_file(path: str, backup: bool = True) -> None:
    with open(path, "r", encoding="utf-8") as f:
        src = f.read()

    if backup:
        bak = path + ".bak"
        with open(bak, "w", encoding="utf-8") as bf:
            bf.write(src)

    no_doc = remove_docstrings(src)
    no_comments = remove_full_line_comments(no_doc)

    with open(path, "w", encoding="utf-8") as f:
        f.write(no_comments)


def gather_files_from_dir(directory: str) -> List[str]:
    result = []
    for root, dirs, files in os.walk(directory):
        if "archive" in root.split(os.sep):
            continue
        for file in files:
            if file.endswith(".py"):
                result.append(os.path.join(root, file))
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--files", nargs="*", help="Specific files to process")
    parser.add_argument("--dir", help="Directory to process recursively")
    parser.add_argument("--backup", action="store_true", help="Create .bak backups")
    args = parser.parse_args()

    files = []
    if args.files:
        files.extend(args.files)
    if args.dir:
        files.extend(gather_files_from_dir(args.dir))

    if not files:
        print("No files to process. Specify --files or --dir")
        return

    for f in files:
        if os.path.exists(f) and f.endswith(".py"):
            print(f"Processing: {f}")
            process_file(f, backup=args.backup)
        else:
            print(f"Skipping (not found or not .py): {f}")


if __name__ == "__main__":
    main()
