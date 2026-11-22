#!/usr/bin/env python3
"""Máy quét tĩnh cho code Python của repo (hiện thực một phần U047/U078).

Luật lỗi (exit 1): except trần, assert ngoài hàm test, shell=True,
os.system, eval/exec, pickle.load/loads, random.* ngoài danh sách cho phép.
Luật cảnh báo (chỉ liệt kê): open() text thiếu encoding, hằng chuỗi gán cho
tên gợi ý secret.

Chạy:
    python tools/lintsec.py                 # quét tools/*.py
    python tools/lintsec.py --self-test     # kiểm tra luật + tự quét
    python tools/lintsec.py --strict        # cảnh báo cũng tính hỏng
Không cần cài thêm thư viện. Cần Python 3.10 trở lên.
"""
from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TEST_FUNCS = {"self_test", "tu_kiem"}
RANDOM_OK = {"cborx.py", "ml_distinguisher.py"}  # fuzz gieo seed + nghiên cứu
SECRET_HINT = ("password", "passwd", "secret", "api_key", "apikey", "token")


class Findings:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []


class Visitor(ast.NodeVisitor):
    def __init__(self, fname: str, out: Findings) -> None:
        self.fname = fname
        self.out = out
        self.func_stack: list[str] = []

    def _loc(self, node: ast.AST) -> str:
        return f"{self.fname}:{getattr(node, 'lineno', '?')}"

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self.func_stack.append(node.name)
        self.generic_visit(node)
        self.func_stack.pop()

    visit_AsyncFunctionDef = visit_FunctionDef

    def _in_test(self) -> bool:
        return any(n in TEST_FUNCS or n.startswith("test_") for n in self.func_stack)

    def visit_Assert(self, node: ast.Assert) -> None:
        if not self._in_test():
            self.out.errors.append(f"{self._loc(node)}: assert ngoài hàm test")
        self.generic_visit(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        if node.type is None:
            self.out.errors.append(f"{self._loc(node)}: except trần")
        self.generic_visit(node)

    @staticmethod
    def _call_name(node: ast.Call) -> str:
        f = node.func
        if isinstance(f, ast.Name):
            return f.id
        if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name):
            return f"{f.value.id}.{f.attr}"
        return ""

    def visit_Call(self, node: ast.Call) -> None:
        name = self._call_name(node)
        if name in ("eval", "exec", "os.system", "pickle.load", "pickle.loads"):
            self.out.errors.append(f"{self._loc(node)}: gọi cấm {name}")
        if name in ("subprocess.call", "subprocess.run", "subprocess.Popen", "os.popen"):
            for kw in node.keywords:
                if kw.arg == "shell" and not (
                        isinstance(kw.value, ast.Constant) and kw.value.value is False):
                    self.out.errors.append(f"{self._loc(node)}: shell=True")
        if name == "open":
            mode = "r"
            has_enc = False
            for arg in node.args[1:]:
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    mode = arg.value
            for kw in node.keywords:
                if kw.arg == "mode" and isinstance(kw.value, ast.Constant):
                    mode = str(kw.value.value)
                if kw.arg == "encoding":
                    has_enc = True
            if "b" not in mode and not has_enc:
                self.out.warnings.append(f"{self._loc(node)}: open() text thiếu encoding")
        if name == "random.Random":
            pass  # gieo seed tường minh cho fuzz/test
        elif name.startswith("random."):
            if Path(self.fname).name not in RANDOM_OK:
                self.out.errors.append(f"{self._loc(node)}: random không-crypto ({name})")
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        self._check_secret_assign(node)
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        self._check_secret_assign(node)
        self.generic_visit(node)

    def _check_secret_assign(self, node: ast.AST) -> None:
        value = getattr(node, "value", None)
        if not (isinstance(value, ast.Constant) and isinstance(value.value, str)
                and len(value.value) >= 8):
            return
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        for target in targets:
            if isinstance(target, ast.Name) and any(h in target.id.lower() for h in SECRET_HINT):
                self.out.warnings.append(
                    f"{self._loc(node)}: hằng chuỗi gán cho tên gợi ý secret ({target.id})")


def scan_source(src: str, fname: str) -> Findings:
    out = Findings()
    try:
        tree = ast.parse(src)
    except SyntaxError as exc:
        out.errors.append(f"{fname}:{exc.lineno}: không phân tích được: {exc.msg}")
        return out
    Visitor(fname, out).visit(tree)
    return out


def scan_file(path: Path) -> Findings:
    try:
        return scan_source(path.read_text(encoding="utf-8"), path.name)
    except (OSError, UnicodeDecodeError) as exc:
        out = Findings()
        out.errors.append(f"{path.name}: không đọc được: {exc}")
        return out


def scan_dir(root: Path) -> Findings:
    total = Findings()
    for path in sorted(root.glob("*.py")):
        found = scan_file(path)
        total.errors.extend(found.errors)
        total.warnings.extend(found.warnings)
    return total


def self_test() -> int:
    # 1. Mỗi luật đều bắt được mẫu vi phạm và bỏ qua mẫu sạch.
    cases: list[tuple[str, str | None]] = [
        ("try:\n x = 1\nexcept:\n pass\n", "errors"),
        ("def f():\n assert x\n", "errors"),
        ("def self_test():\n assert x\n", None),
        ("def tu_kiem():\n assert x\n", None),
        ("def test_vidu():\n assert x\n", None),
        ("eval('1')", "errors"),
        ("import os\nos.system('x')", "errors"),
        ("import pickle\npickle.loads(b'')", "errors"),
        ("import subprocess\nsubprocess.run('x', shell=True)", "errors"),
        ("import subprocess\nsubprocess.run(['x'], shell=False)", None),
        ("open('f')", "warnings"),
        ("open('f', encoding='utf-8')", None),
        ("open('f', 'rb')", None),
        ("import random\nrandom.random()", "errors"),
        ("import random\nrandom.Random(1)", None),
        ("password = 'abcdefgh'", "warnings"),
        ("ten = 'abcdefgh'", None),
    ]
    for src, want in cases:
        found = scan_source(src, "mau.py")
        if want == "errors":
            assert found.errors, f"đáng lẽ báo lỗi: {src[:30]}"
        elif want == "warnings":
            assert found.warnings and not found.errors, f"đáng lẽ cảnh báo: {src[:30]}"
        else:
            assert not found.errors and not found.warnings, f"đáng lẽ bỏ qua: {src[:30]}"
    # 2. Tự quét tools/ thật: hiện tại phải sạch lỗi.
    found = scan_dir(ROOT)
    assert not found.errors, f"tools/ còn lỗi tĩnh: {found.errors[:5]}"
    print(f"self-test ok: {len(cases)} luật đúng, tools/ sạch lỗi "
          f"({len(found.warnings)} cảnh báo).")
    for w in found.warnings[:10]:
        print(f"  cảnh báo: {w}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Quét tĩnh bảo mật cho tools/*.py.")
    ap.add_argument("-t", "--self-test", action="store_true")
    ap.add_argument("--strict", action="store_true", help="cảnh báo cũng tính hỏng")
    ap.add_argument("--path", default=None, help="quét file/thư mục khác")
    args = ap.parse_args(argv)
    if args.self_test:
        return self_test()
    target = Path(args.path) if args.path else ROOT
    found = scan_file(target) if target.is_file() else scan_dir(target)
    for e in found.errors:
        print(f"LỖI {e}")
    for w in found.warnings:
        print(f"cảnh báo {w}")
    print(f"{len(found.errors)} lỗi, {len(found.warnings)} cảnh báo.")
    if found.errors or (args.strict and found.warnings):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
