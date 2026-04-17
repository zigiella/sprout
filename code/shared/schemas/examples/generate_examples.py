"""Generate canonical JSON examples from the Pydantic models."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from schemas import (
    ContradictionAlert,
    DecisionReceipt,
    PolicyDelta,
    PolicyPacket,
    RhizomeSnapshot,
    WeatherPacket,
)
from schemas.examples.builders import (
    contradiction_alert_example,
    decision_receipt_blocked_example,
    decision_receipt_example,
    policy_delta_example,
    policy_packet_example,
    rhizome_snapshot_example,
    weather_packet_example,
)

EXAMPLES_DIR = Path(__file__).resolve().parent


@dataclass(frozen=True)
class ExampleSpec:
    filename: str
    model_cls: type
    payload_factory: Callable[[], dict]


CORE_EXAMPLE_SPECS = (
    ExampleSpec("rhizome_snapshot.json", RhizomeSnapshot, rhizome_snapshot_example),
    ExampleSpec("policy_packet.json", PolicyPacket, policy_packet_example),
    ExampleSpec("policy_delta.json", PolicyDelta, policy_delta_example),
    ExampleSpec("weather_packet.json", WeatherPacket, weather_packet_example),
    ExampleSpec("contradiction_alert.json", ContradictionAlert, contradiction_alert_example),
    ExampleSpec("decision_receipt.json", DecisionReceipt, decision_receipt_example),
)

SUPPLEMENTAL_EXAMPLE_SPECS = (
    ExampleSpec("decision_receipt_blocked.json", DecisionReceipt, decision_receipt_blocked_example),
)

ALL_EXAMPLE_SPECS = CORE_EXAMPLE_SPECS + SUPPLEMENTAL_EXAMPLE_SPECS


def render_example(spec: ExampleSpec) -> str:
    payload = spec.payload_factory()
    parsed = spec.model_cls.model_validate(payload)
    canonical_payload = parsed.model_dump(mode="json")
    return json.dumps(canonical_payload, indent=2, ensure_ascii=True) + "\n"


def write_examples() -> list[Path]:
    written_paths: list[Path] = []
    for spec in ALL_EXAMPLE_SPECS:
        output_path = EXAMPLES_DIR / spec.filename
        output_path.write_text(render_example(spec), encoding="utf-8")
        written_paths.append(output_path)
    return written_paths


def stale_examples() -> list[str]:
    stale: list[str] = []
    for spec in ALL_EXAMPLE_SPECS:
        output_path = EXAMPLES_DIR / spec.filename
        expected = render_example(spec)
        if not output_path.exists() or output_path.read_text(encoding="utf-8") != expected:
            stale.append(spec.filename)
    return stale


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check that the committed JSON files match the generated canonical output.",
    )
    args = parser.parse_args()

    if args.check:
        stale = stale_examples()
        if stale:
            for filename in stale:
                print(filename)
            return 1
        print("All canonical examples are up to date.")
        return 0

    written_paths = write_examples()
    for path in written_paths:
        print(path.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
