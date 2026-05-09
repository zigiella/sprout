<!-- Contributing guide · English first · Spanish version: CONTRIBUTING.es.md -->

🇬🇧 **English** · 🇪🇸 **[Español](CONTRIBUTING.es.md)**

---

# Contributing to Sprout

Thanks for your interest in Sprout. This document covers **two paths** to contribute, depending on whether you are part of the internal **zigiella** team or an external contributor.

---

## Two paths to contribute

### Path A — External contributors

If you are not part of the zigiella team and you want to propose a change to the public Sprout repository:

1. **Open an issue first** to discuss the change before you write code, especially for non-trivial features. Sprout has tight architectural invariants (see *Architectural invariants* below) that we don't want to break by accident.
2. **Fork the repository** and create a branch from `main` (`fix/<short-topic>` or `feat/<short-topic>`).
3. **Follow the code conventions** documented in [Code conventions](#code-conventions) below.
4. **Run tests locally** before pushing (see *Reproducing locally* in the [README](README.md#reproduce-locally)).
5. **Open a pull request** against `main` with a clear description of:
   - What problem your change solves
   - How it preserves the architectural invariants
   - How you tested it
6. **Be patient** — this is a small project; reviews may take a few days.

External pull requests are welcome but reviewed against the project's **architectural invariants** (below). We may decline contributions that introduce cloud dependencies, weaken the safety hierarchy, or break the determinism guarantees, even if they are otherwise high quality. Sprout is opinionated about *where* and *how* AI is used.

### Path B — Internal zigiella team

The internal team has a much more detailed operating manual (machine-shared workflow, identity-inline commits, three-point git verification, `Interrelaciones` template for cross-frente messages, repo-first rule, hot-file convention, etc.) that lives in [`CONTRIBUTING.es.md`](CONTRIBUTING.es.md). It's in Spanish because the team works in Spanish.

If you are reading this and you are part of the team, **please read `CONTRIBUTING.es.md` end to end**. The rules in there are the cumulative learning of 24+ days of operating in a shared machine — they exist because each one was learned the hard way.

---

## Architectural invariants

Sprout is built around five non-negotiables. Any contribution should preserve them:

1. **Local-first by design.** No node depends on the cloud to function. Internet is optional, never required for the core control loop.
2. **Physical safety prevails.** The ESP32-S3 firmware can veto or modulate any action. No `PolicyPacket` from upper layers can reduce its hard limits — only recommend more conservative behavior.
3. **Deterministic logic decides; the LLM only writes the rationale.** Critical decisions are auditable down to a concrete rule. Gemma 4 explains; the system decides.
4. **Every intelligence has jurisdiction and expiry.** Every JSON contract carries explicit authority and TTL. Nothing is silently accepted forever.
5. **Honesty over polish.** Refusal is a feature, not a failure. If the system isn't sure, it says so and asks the human to rephrase or step in.

A pull request that violates any of these will be discussed openly in the issue thread before being merged.

---

## Code conventions

### Python (Rhizome, Meristem, Simulator)

- Python 3.11+
- `ruff` for linting, `black` for formatting
- Type hints required on public functions
- Brief docstrings (Spanish in code, English-friendly in API docs)
- Minimal tests in `tests/` of each subproject

### Kotlin (Pollen Android)

- Jetpack Compose
- Gemma 4 via Google AI Edge / LiteRT (with `llama.cpp` as fallback)

### JSON schemas

- All schemas live in `code/shared/schemas/`
- Validated via `pydantic` in Python, `kotlinx.serialization` in Kotlin

### Naming Gemma 4 models

Follow Google's [official naming guidelines](https://ai.google/documents/32/External_Gemma_Model_Variant_Guidelines.pdf):

- Pattern: `sprout/sprout-<component>-<model_base>-v<N>`
- Example: `sprout/sprout-rhizome-e2b-v1`
- Never use "Gemma" as the prefix of a derived model name (license requirement)

### Branches

- `main` = production / latest stable
- `feat/<topic>` = features in development
- `fix/<topic>` = bugfixes
- `docs/<topic>` = docs-only changes

### Commit messages

- `[zone] short summary` (e.g., `[rhizome] add humidity reading via ADS1115`)
- For commits that close an issue, include `Closes #N` in the body

---

## Code of conduct

Be kind, be precise, and be patient. The project is built by a small team under a tight deadline; we appreciate thoughtful contributions and we'll respond as quickly as we can.

---

## License

Apache 2.0 (see [`LICENSE`](LICENSE)). Same as Gemma 4.

## Attribution

Sprout uses Gemma 4 models by Google. **Gemma is a trademark of Google LLC.** This project is not affiliated with or endorsed by Google.

## Questions

Open an issue, or — if you are part of the zigiella team — write a `bitacora/` entry following the convention in [`CONTRIBUTING.es.md §4`](CONTRIBUTING.es.md).
