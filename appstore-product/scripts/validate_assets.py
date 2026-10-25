#!/usr/bin/env python3
"""校验 App Store 静态上传图的尺寸、格式、色彩模式和透明通道。"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError as error:  # pragma: no cover - 依赖缺失时给出可操作提示
    raise SystemExit("缺少 Pillow。请先执行：python3 -m pip install Pillow") from error


SPEC_CHECKED_ON = "2026-10-25"
SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg"}
EXACT_SIZES = {
    "creative-header": {(3840, 1646)},
    "creative-universal": {(5244, 2950)},
    "iphone-required": {
        (1179, 2556),
        (2556, 1179),
        (1206, 2622),
        (2622, 1206),
    },
    "ipad-required": {
        (2064, 2752),
        (2752, 2064),
        (2048, 2732),
        (2732, 2048),
    },
}


def parse_expected(value: str) -> tuple[int, int]:
    normalized = value.lower().replace("×", "x")
    try:
        width_text, height_text = normalized.split("x", 1)
        width, height = int(width_text), int(height_text)
    except (ValueError, TypeError) as error:
        raise argparse.ArgumentTypeError("尺寸应写成 3840x1646") from error
    if width <= 0 or height <= 0:
        raise argparse.ArgumentTypeError("宽高必须大于 0")
    return width, height


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def dimension_error(
    mode: str, size: tuple[int, int], expected: set[tuple[int, int]] | None
) -> str | None:
    width, height = size
    if expected is not None:
        if size not in expected:
            options = ", ".join(f"{w}x{h}" for w, h in sorted(expected))
            return f"尺寸 {width}x{height} 不在允许值中：{options}"
        return None

    if mode == "creative-search":
        if width * 2 != height * 3:
            return f"尺寸 {width}x{height} 不是 3:2"
        if not (1920 <= width <= 3840 and 1280 <= height <= 2560):
            return "搜索结果图应在 1920x1280 至 3840x2560 之间"
        return None

    return f"未知尺寸规则：{mode}"


def inspect_file(
    path: Path, mode: str, expected: set[tuple[int, int]] | None
) -> dict[str, object]:
    errors: list[str] = []
    warnings: list[str] = []

    if not path.is_file():
        return {"file": str(path), "ok": False, "errors": ["文件不存在"]}

    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        errors.append("扩展名必须是 .png、.jpg 或 .jpeg")

    try:
        with Image.open(path) as image:
            image.load()
            width, height = image.size
            image_format = image.format
            color_mode = image.mode
            bands = image.getbands()
            has_alpha = "A" in bands or "transparency" in image.info
    except Exception as error:  # Pillow 会给出具体损坏原因
        return {
            "file": str(path),
            "ok": False,
            "errors": errors + [f"无法读取图片：{error}"],
        }

    size_error = dimension_error(mode, (width, height), expected)
    if size_error:
        errors.append(size_error)
    if has_alpha:
        errors.append("图片包含 alpha 或透明度")
    if color_mode != "RGB":
        errors.append(f"色彩模式为 {color_mode}；上传定稿应导出为 RGB")
    if image_format not in {"PNG", "JPEG"}:
        errors.append(f"实际图片格式为 {image_format}，不在 PNG/JPEG 中")
    if path.name == ".DS_Store":
        errors.append("上传目录不能包含 .DS_Store")

    return {
        "file": str(path),
        "ok": not errors,
        "width": width,
        "height": height,
        "format": image_format,
        "mode": color_mode,
        "hasAlpha": has_alpha,
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
        "errors": errors,
        "warnings": warnings,
    }


def expand_inputs(inputs: list[Path]) -> list[Path]:
    """允许传单个图片或一个扁平的 upload 目录。"""
    expanded: list[Path] = []
    for path in inputs:
        if path.is_dir():
            expanded.extend(sorted(item for item in path.iterdir() if item.is_file()))
        else:
            expanded.append(path)
    return expanded


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode",
        required=True,
        choices=[
            "creative-header",
            "creative-search",
            "creative-universal",
            "iphone-required",
            "ipad-required",
        ],
    )
    parser.add_argument(
        "--expect",
        action="append",
        type=parse_expected,
        help="按实时官方规格覆盖内置尺寸，可重复，例如 --expect 3840x1646",
    )
    parser.add_argument("--json-out", type=Path, help="可选：保存机器可读验收报告")
    parser.add_argument("files", nargs="+", type=Path)
    args = parser.parse_args()

    expected = set(args.expect) if args.expect else EXACT_SIZES.get(args.mode)
    files = expand_inputs(args.files)
    reports = [inspect_file(path, args.mode, expected) for path in files]
    global_errors: list[str] = []
    if not files:
        global_errors.append("没有找到可验收的文件")
    if args.mode in {"iphone-required", "ipad-required"} and not 1 <= len(files) <= 10:
        global_errors.append("同一设备尺寸的普通截图应为 1–10 张")

    result = {
        "ok": all(report["ok"] for report in reports) and not global_errors,
        "mode": args.mode,
        "specBaselineCheckedOn": SPEC_CHECKED_ON,
        "customExpectedSizes": [list(size) for size in sorted(expected)]
        if args.expect
        else None,
        "globalErrors": global_errors,
        "files": reports,
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
