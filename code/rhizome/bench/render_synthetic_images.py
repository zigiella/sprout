"""Render deterministic PNG assets for Rhizome multimodal benchmarks."""

from __future__ import annotations

import argparse
import struct
import zlib
from dataclasses import dataclass
from pathlib import Path

ASSETS_DIR = Path(__file__).resolve().parent / "assets"
WIDTH = 384
HEIGHT = 256


@dataclass(frozen=True)
class Color:
    r: int
    g: int
    b: int

    def triplet(self) -> tuple[int, int, int]:
        return self.r, self.g, self.b


@dataclass(frozen=True)
class Scene:
    filename: str
    parcel_a_color: Color
    parcel_b_color: Color
    tank_fill_ratio: float
    tank_fill_color: Color
    weather_rain: bool = False
    weather_alert: bool = False
    contradiction: bool = False


PALETTE = {
    "bg": Color(245, 241, 232),
    "frame": Color(52, 66, 82),
    "soil": Color(123, 88, 63),
    "leaf": Color(62, 125, 75),
    "healthy": Color(74, 166, 102),
    "warning": Color(232, 169, 74),
    "stress": Color(214, 103, 74),
    "danger": Color(173, 62, 50),
    "water": Color(79, 158, 216),
    "cloud": Color(179, 191, 206),
    "rain": Color(66, 122, 195),
    "sand": Color(232, 209, 168),
    "ink": Color(35, 43, 53),
    "white": Color(255, 255, 255),
    "badge": Color(179, 66, 133),
}

SCENES = [
    Scene(
        filename="parcel_a_dry.png",
        parcel_a_color=PALETTE["stress"],
        parcel_b_color=PALETTE["healthy"],
        tank_fill_ratio=0.78,
        tank_fill_color=PALETTE["water"],
    ),
    Scene(
        filename="parcel_b_dry.png",
        parcel_a_color=PALETTE["healthy"],
        parcel_b_color=PALETTE["stress"],
        tank_fill_ratio=0.81,
        tank_fill_color=PALETTE["water"],
    ),
    Scene(
        filename="tank_low_guardrail.png",
        parcel_a_color=PALETTE["warning"],
        parcel_b_color=PALETTE["healthy"],
        tank_fill_ratio=0.16,
        tank_fill_color=PALETTE["danger"],
        weather_alert=True,
    ),
    Scene(
        filename="sensor_vision_conflict.png",
        parcel_a_color=PALETTE["healthy"],
        parcel_b_color=PALETTE["healthy"],
        tank_fill_ratio=0.74,
        tank_fill_color=PALETTE["water"],
        contradiction=True,
    ),
    Scene(
        filename="incoming_rain_shift.png",
        parcel_a_color=PALETTE["warning"],
        parcel_b_color=PALETTE["healthy"],
        tank_fill_ratio=0.69,
        tank_fill_color=PALETTE["water"],
        weather_rain=True,
    ),
]


class Canvas:
    def __init__(self, width: int, height: int, background: Color) -> None:
        self.width = width
        self.height = height
        self.rows = [bytearray(background.triplet() * width) for _ in range(height)]

    def set_pixel(self, x: int, y: int, color: Color) -> None:
        if not (0 <= x < self.width and 0 <= y < self.height):
            return
        offset = x * 3
        self.rows[y][offset : offset + 3] = bytes(color.triplet())

    def fill_rect(self, left: int, top: int, width: int, height: int, color: Color) -> None:
        left = max(0, left)
        top = max(0, top)
        right = min(self.width, left + width)
        bottom = min(self.height, top + height)
        fill = bytes(color.triplet() * max(0, right - left))
        for y in range(top, bottom):
            start = left * 3
            end = right * 3
            self.rows[y][start:end] = fill

    def stroke_rect(self, left: int, top: int, width: int, height: int, color: Color, stroke: int = 2) -> None:
        self.fill_rect(left, top, width, stroke, color)
        self.fill_rect(left, top + height - stroke, width, stroke, color)
        self.fill_rect(left, top, stroke, height, color)
        self.fill_rect(left + width - stroke, top, stroke, height, color)

    def fill_circle(self, cx: int, cy: int, radius: int, color: Color) -> None:
        radius_sq = radius * radius
        for y in range(cy - radius, cy + radius + 1):
            for x in range(cx - radius, cx + radius + 1):
                dx = x - cx
                dy = y - cy
                if dx * dx + dy * dy <= radius_sq:
                    self.set_pixel(x, y, color)

    def draw_line(self, x0: int, y0: int, x1: int, y1: int, color: Color, thickness: int = 1) -> None:
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy

        while True:
            for offset_x in range(-(thickness // 2), thickness // 2 + 1):
                for offset_y in range(-(thickness // 2), thickness // 2 + 1):
                    self.set_pixel(x0 + offset_x, y0 + offset_y, color)
            if x0 == x1 and y0 == y1:
                break
            double_error = 2 * err
            if double_error >= dy:
                err += dy
                x0 += sx
            if double_error <= dx:
                err += dx
                y0 += sy


def _draw_leaf_cluster(canvas: Canvas, origin_x: int, origin_y: int, accent: Color) -> None:
    canvas.fill_rect(origin_x - 3, origin_y + 6, 6, 34, PALETTE["leaf"])
    canvas.fill_circle(origin_x - 18, origin_y + 6, 14, accent)
    canvas.fill_circle(origin_x + 18, origin_y - 4, 14, accent)
    canvas.fill_circle(origin_x, origin_y - 14, 10, accent)
    canvas.draw_line(origin_x, origin_y + 6, origin_x - 12, origin_y - 2, PALETTE["leaf"], thickness=2)
    canvas.draw_line(origin_x, origin_y + 2, origin_x + 12, origin_y - 10, PALETTE["leaf"], thickness=2)


def _draw_parcel_panel(canvas: Canvas, *, left: int, top: int, width: int, height: int, accent: Color) -> None:
    canvas.fill_rect(left, top, width, height, PALETTE["white"])
    canvas.stroke_rect(left, top, width, height, PALETTE["frame"], stroke=3)
    canvas.fill_rect(left + 10, top + height - 34, width - 20, 22, PALETTE["soil"])
    canvas.fill_rect(left + width - 28, top + 16, 12, height - 54, PALETTE["sand"])
    canvas.fill_rect(left + width - 28, top + 16, 12, height - 54, accent)
    _draw_leaf_cluster(canvas, left + width // 2, top + 72, accent)


def _draw_tank(canvas: Canvas, *, left: int, top: int, width: int, height: int, fill_ratio: float, accent: Color) -> None:
    canvas.fill_rect(left, top, width, height, PALETTE["white"])
    canvas.stroke_rect(left, top, width, height, PALETTE["frame"], stroke=3)
    inner_left = left + 18
    inner_top = top + 18
    inner_width = width - 36
    inner_height = height - 36
    canvas.fill_rect(inner_left, inner_top, inner_width, inner_height, PALETTE["bg"])
    fill_height = max(6, int(inner_height * max(0.0, min(fill_ratio, 1.0))))
    canvas.fill_rect(inner_left, inner_top + inner_height - fill_height, inner_width, fill_height, accent)
    canvas.fill_rect(left + width - 38, top + 18, 12, height - 36, PALETTE["sand"])
    gauge_height = height - 36
    gauge_fill = max(6, int(gauge_height * max(0.0, min(fill_ratio, 1.0))))
    canvas.fill_rect(left + width - 38, top + 18 + gauge_height - gauge_fill, 12, gauge_fill, accent)


def _draw_weather(canvas: Canvas, *, left: int, top: int, width: int, height: int, rain: bool, alert: bool) -> None:
    canvas.fill_rect(left, top, width, height, PALETTE["white"])
    canvas.stroke_rect(left, top, width, height, PALETTE["frame"], stroke=3)
    if rain:
        cloud_color = PALETTE["cloud"]
        canvas.fill_circle(left + 60, top + 52, 22, cloud_color)
        canvas.fill_circle(left + 90, top + 44, 26, cloud_color)
        canvas.fill_circle(left + 122, top + 54, 22, cloud_color)
        canvas.fill_rect(left + 46, top + 56, 92, 26, cloud_color)
        for index in range(5):
            drop_x = left + 58 + index * 18
            canvas.fill_circle(drop_x, top + 108, 5, PALETTE["rain"])
            canvas.draw_line(drop_x, top + 108, drop_x - 4, top + 126, PALETTE["rain"], thickness=2)
    else:
        canvas.fill_circle(left + 90, top + 60, 26, PALETTE["warning"])
        canvas.fill_circle(left + 116, top + 60, 26, PALETTE["warning"])
        canvas.fill_circle(left + 103, top + 42, 28, PALETTE["warning"])

    if alert:
        canvas.fill_circle(left + width - 42, top + 42, 18, PALETTE["badge"])
        canvas.draw_line(left + width - 48, top + 36, left + width - 36, top + 48, PALETTE["white"], thickness=3)
        canvas.draw_line(left + width - 48, top + 48, left + width - 36, top + 36, PALETTE["white"], thickness=3)


def _draw_contradiction_badge(canvas: Canvas) -> None:
    badge_left = 26
    badge_top = 18
    canvas.fill_rect(badge_left, badge_top, 124, 26, PALETTE["badge"])
    canvas.draw_line(badge_left + 10, badge_top + 19, badge_left + 32, badge_top + 7, PALETTE["white"], thickness=3)
    canvas.draw_line(badge_left + 38, badge_top + 7, badge_left + 60, badge_top + 19, PALETTE["white"], thickness=3)
    canvas.draw_line(206, 48, 332, 144, PALETTE["badge"], thickness=8)


def render_scene(scene: Scene) -> bytes:
    canvas = Canvas(WIDTH, HEIGHT, PALETTE["bg"])

    canvas.fill_rect(0, 0, WIDTH, 20, PALETTE["ink"])
    _draw_parcel_panel(canvas, left=24, top=34, width=156, height=118, accent=scene.parcel_a_color)
    _draw_parcel_panel(canvas, left=204, top=34, width=156, height=118, accent=scene.parcel_b_color)
    _draw_tank(
        canvas,
        left=24,
        top=172,
        width=156,
        height=64,
        fill_ratio=scene.tank_fill_ratio,
        accent=scene.tank_fill_color,
    )
    _draw_weather(
        canvas,
        left=204,
        top=172,
        width=156,
        height=64,
        rain=scene.weather_rain,
        alert=scene.weather_alert,
    )

    if scene.contradiction:
        _draw_contradiction_badge(canvas)

    return _encode_png(canvas)


def _png_chunk(kind: bytes, payload: bytes) -> bytes:
    return (
        struct.pack(">I", len(payload))
        + kind
        + payload
        + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
    )


def _encode_png(canvas: Canvas) -> bytes:
    ihdr = struct.pack(">IIBBBBB", canvas.width, canvas.height, 8, 2, 0, 0, 0)
    raw_rows = b"".join(b"\x00" + bytes(row) for row in canvas.rows)
    compressed = zlib.compress(raw_rows, level=9)
    return b"".join(
        [
            b"\x89PNG\r\n\x1a\n",
            _png_chunk(b"IHDR", ihdr),
            _png_chunk(b"IDAT", compressed),
            _png_chunk(b"IEND", b""),
        ]
    )


def render_asset_map() -> dict[str, bytes]:
    return {scene.filename: render_scene(scene) for scene in SCENES}


def stale_assets(asset_dir: Path = ASSETS_DIR) -> bool:
    for filename, payload in render_asset_map().items():
        path = asset_dir / filename
        if not path.exists():
            return True
        if path.read_bytes() != payload:
            return True
    return False


def write_assets(asset_dir: Path = ASSETS_DIR) -> list[Path]:
    asset_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for filename, payload in render_asset_map().items():
        path = asset_dir / filename
        path.write_bytes(payload)
        written.append(path)
    return written


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check whether the committed PNG assets match the generator.")
    parser.add_argument("--output-dir", type=Path, default=ASSETS_DIR, help="Directory where PNG assets are written.")
    args = parser.parse_args()

    if args.check:
        if stale_assets(args.output_dir):
            print(str(args.output_dir))
            return 1
        print("Synthetic benchmark assets are up to date.")
        return 0

    for path in write_assets(args.output_dir):
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
