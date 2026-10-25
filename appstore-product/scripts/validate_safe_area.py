#!/usr/bin/env python3
"""校验布局清单中的关键元素是否位于 App Store 创意素材安全区。"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

try:
    from PIL import Image
except ImportError as error:  # pragma: no cover - 依赖缺失时给出可操作提示
    raise SystemExit("缺少 Pillow。请先执行：python3 -m pip install Pillow") from error


BASELINE_SAFE_AREAS = {
    "header": {
        "canvas": (3840, 1646),
        "safe": {"x": 1097, "y": 493, "width": 1646, "height": 661},
    },
    "creative-header": {
        "canvas": (3840, 1646),
        "safe": {"x": 1097, "y": 493, "width": 1646, "height": 661},
    },
    "search": {
        "canvas": (3840, 2560),
        "safe": {"x": 836, "y": 765, "width": 2168, "height": 1030},
    },
    "creative-search": {
        "canvas": (3840, 2560),
        "safe": {"x": 836, "y": 765, "width": 2168, "height": 1030},
    },
    "universal": {
        "canvas": (5244, 2950),
        "safe": {"x": 1921, "y": 660, "width": 1402, "height": 962},
    },
    "creative-universal": {
        "canvas": (5244, 2950),
        "safe": {"x": 1921, "y": 660, "width": 1402, "height": 962},
    },
}


def get_value(item: dict[str, Any], snake: str, camel: str) -> Any:
    return item.get(snake, item.get(camel))


def normalize_rect(value: Any, label: str) -> dict[str, float]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} 必须是对象")
    try:
        rect = {
            "x": float(value["x"]),
            "y": float(value["y"]),
            "width": float(value["width"]),
            "height": float(value["height"]),
        }
    except (KeyError, TypeError, ValueError) as error:
        raise ValueError(f"{label} 缺少合法的 x/y/width/height") from error
    if rect["width"] < 0 or rect["height"] < 0:
        raise ValueError(f"{label} 的宽高不能为负数")
    return rect


def contains(outer: dict[str, float], inner: dict[str, float]) -> bool:
    return (
        inner["x"] >= outer["x"]
        and inner["y"] >= outer["y"]
        and inner["x"] + inner["width"] <= outer["x"] + outer["width"]
        and inner["y"] + inner["height"] <= outer["y"] + outer["height"]
    )


def inspect_asset(asset: dict[str, Any], root: Path) -> dict[str, Any]:
    errors: list[str] = []
    placement = str(asset.get("placement", "")).lower()
    baseline = BASELINE_SAFE_AREAS.get(placement)
    file_value = asset.get("file")
    file_path = root / file_value if isinstance(file_value, str) else None

    width = asset.get("width")
    height = asset.get("height")
    canvas_value = asset.get("canvas")
    if isinstance(canvas_value, list) and len(canvas_value) == 2:
        width, height = canvas_value
    if (width is None or height is None) and baseline:
        width, height = baseline["canvas"]
    try:
        canvas = {
            "x": 0.0,
            "y": 0.0,
            "width": float(width),
            "height": float(height),
        }
    except (TypeError, ValueError) as error:
        raise ValueError("资产缺少合法画布宽高") from error

    safe_value = get_value(asset, "safe_area", "safeArea")
    if safe_value is None and baseline:
        safe_value = baseline["safe"]
    safe = normalize_rect(safe_value, "safe_area")
    if not contains(canvas, safe):
        errors.append("安全区超出画布")

    elements_value = get_value(asset, "critical_elements", "criticalElements")
    if not isinstance(elements_value, list) or not elements_value:
        errors.append("缺少 critical_elements/criticalElements")
        elements_value = []

    element_reports: list[dict[str, Any]] = []
    for index, raw_element in enumerate(elements_value):
        if not isinstance(raw_element, dict):
            errors.append(f"关键元素 #{index + 1} 不是对象")
            continue
        name = raw_element.get("name") or raw_element.get("className") or f"#{index + 1}"
        rect = normalize_rect(raw_element, f"关键元素 {name}")
        allow_outside = bool(
            get_value(raw_element, "allow_outside", "allowOutside") or False
        )
        inside = contains(safe, rect)
        if not inside and not allow_outside:
            errors.append(f"关键元素 {name} 超出安全区")
        element_reports.append(
            {"name": name, "insideSafeArea": inside, "allowOutside": allow_outside}
        )

    if file_path:
        if not file_path.is_file():
            errors.append(f"图片不存在：{file_path}")
        else:
            with Image.open(file_path) as image:
                if image.size != (int(canvas["width"]), int(canvas["height"])):
                    errors.append(
                        f"图片尺寸 {image.width}x{image.height} 与清单画布不一致"
                    )

    return {
        "file": file_value,
        "placement": placement,
        "ok": not errors,
        "canvas": [int(canvas["width"]), int(canvas["height"])],
        "safeArea": safe,
        "criticalElements": element_reports,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--json-out", type=Path, help="可选：保存机器可读报告")
    args = parser.parse_args()

    try:
        payload = json.loads(args.manifest.read_text(encoding="utf-8"))
        assets = payload.get("assets") if isinstance(payload, dict) else payload
        if not isinstance(assets, list) or not assets:
            raise ValueError("清单根节点应为非空数组，或包含非空 assets 数组")
        reports = [inspect_asset(asset, args.manifest.parent) for asset in assets]
        result = {
            "ok": all(report["ok"] for report in reports),
            "specBaselineCheckedOn": "2026-10-25",
            "assets": reports,
        }
    except Exception as error:
        result = {"ok": False, "fatalError": str(error)}

    print(json.dumps(result, ensure_ascii=False, indent=2))
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
