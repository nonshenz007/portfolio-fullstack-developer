# INTERVIEW BRIEF — Clara (Offline Academic Assistant)

## 1) Snapshot
- Purpose: Privacy‑first academic assistant orchestrating local LLMs (via llama.cpp) for tasks like study planning, Q&A, and document organization.
- Users: Students and researchers needing offline workflows.
- Problem: Enables AI‑assisted tasks without network dependency; predictable performance on local hardware.

- Tech Stack
  - Runtime: Python 3.
  - Inference: External llama.cpp binary (GGUF models) launched via subprocess.
  - Structure: `Clara/Core/*` for orchestration; `Launchers/` for entry; minimal Python deps.

- Entry Points / Boot
  - Launchers in `Clara/Launchers` (e.g., CLI/desktop wrappers).
  - Core router: `Clara/Core/router.py` — routes tasks to execution backends.
  - LLM runner: `Clara/Core/utils/llama_runner.py` — finds and executes llama.cpp.

## 2) Architecture Map
- Folder Tree (top 2 levels)
  - `Clara/Core/` task router, utils, pipelines
  - `Clara/Models/` model storage (GGUF files expected)
  - `Clara/Memory/` workspace memory/state
  - `Clara/Docs/` documentation
  - `Clara/Launchers/` entry scripts

- Responsibilities
  - `Core/router.py`: Dispatches prompts/commands, would call `llama_runner.invoke(...)` (wired for simulation now).
  - `Core/utils/llama_runner.py`: Binary discovery (`find_llama_cpp_binary`) and invocation (`run_llama_cpp`) with params.

- Data Flow
  Command → Router → llama.cpp process with model + prompts → stdout/stderr captured → response routing → write to Memory/outputs.

- External Services
  - None; model execution is fully local via llama.cpp.

## 3) Interfaces
- CLI Scripts / Launchers
  - `Clara/Launchers/*` (TODO list exact names) wrap router and execution; dry‑run supported for development.

## 4) Data & Config
- Models: `Clara/Models/*.gguf` paths; expected model naming in readme.
- Env: Optional path overrides for llama.cpp binary and model directory.
- Requirements: `Clara/requirements.txt` — minimal (`pyyaml`, `psutil`).

## 5) Core Logic Deep Dives
1) `Core/utils/llama_runner.py:find_llama_cpp_binary()`
   - Searches in known locations (repo‑local and sibling `llama.cpp` folder) and returns path or error.
2) `Core/utils/llama_runner.py:run_llama_cpp(model, system_prompt, user_command, tokens, temperature, top_p, top_k)`
   - Assembles command line, spawns process, captures output/errors; prints diagnostic command for reproducibility.
3) `Core/router.py`
   - Task routing layer; where prompt templates and policy controls (temperature/tokens) plug in; currently simulates call site.

## 6) Reliability, Security, Performance
- Reliability: Validates binary presence; safe fallbacks and explicit error messages when binary or model is missing.
- Security: No network calls; work is local; follow model file and prompt sanitation hygiene.
- Performance: Hardware‑aware selection (future); parameters control throughput/latency; offload to GPU builds if detected.

## 7) Deploy & Ops
- Distribution: Package as CLI; ship instructions to place `llama.cpp` binary and GGUF models in `Models/`.
- Logging: Print command lines for reproducibility; capture stderr/stdout; add rotating logs as a next step.

## 8) Testing & QA
- Dry‑run of runner with tiny model; unit tests for path resolution and command assembly.
- Manual: Confirm binary discovery, test with small GGUF, validate token/temperature flags.

## 9) Interview Q&A Pack
1) How do you run the model completely offline?
   - Spawn llama.cpp with a local GGUF file via `Core/utils/llama_runner.py` using `subprocess.run`.
2) How is the binary located?
   - `find_llama_cpp_binary()` searches common paths; returns explicit error otherwise.
3) Where do you wire templating and policies?
   - `Core/router.py`—central place to set system prompts and sampling params.
4) How do you handle errors?
   - Catch `CalledProcessError`, print stderr, return descriptive error strings to the router.
5) What’s the performance tuning path?
   - Choose quantization (Q4_K_M etc.), adjust tokens/temp/top‑k/p, and select GPU build when present.
6) Where are models stored?
   - `Clara/Models` by convention; path is configurable.
7) How to add a new command?
   - Extend router with new verb → map to prompt template and runner call.
8) How to debug a failing run?
   - Use the printed command line, run in shell, inspect stderr; minimize params then scale up.
9) How do you avoid blocking UI?
   - CLI is synchronous; for desktop use a thread/process pool (future addition).
10) What happens without a model?
   - Runner prints guidance and returns a specific error; router surfaces it to the user.
11) How to add hardware detection?
   - Probe CPU/GPU at boot and select the appropriate binary flags; psutil present already.
12) How do you keep it maintainable?
   - Keep runner minimal and pure; config in one place; templating separated from invocation.

- Debugging stories
  - Missing binary confusion: Added explicit search + friendly message and sample path; mitigated new user setup issues.
  - Parameter overloads: Added conservative defaults and step‑up guidance to avoid OOM.

- Scalability tradeoff
  - Use external binary for speed/compatibility; tight control over invocation and resource use vs. large Python deps.

- Security hardening step
  - Disallow remote URLs, validate model paths, and sanitize prompt inputs for shell safety.

- If I had 1 week
  - Add config file, prompt templates, small test model bundling, and structured logs.

## 10) Flash Cards
- “Router dispatches tasks; runner executes llama.cpp.”
- “Binary discovery prevents opaque failures.”
- “All local; zero network required.”
- “Models live in `Clara/Models/*.gguf`.”
- “Parameters tune speed vs. quality.”
- “Errors surfaced with actionable messages.”
- “Add commands by extending router map.”
- “psutil available for basic HW telemetry.”
- “Keep runner minimal; focus on reliability.”
- “Launchers wrap CLI/desktop entry.”
- “Config file planned for policies.”
- “Prefer deterministic defaults.”
- “Document exact shell command for repro.”
- “Guard against path injection.”
- “Test with tiny model first.”

---

## Universal Hot‑Seat Prep
- Walkthrough: Snapshot → Core (router/runner) → Flow: command → runner → output → Deploy with local models.
- Why this stack: Maximum portability and privacy; minimal deps; easy ops.
- Debug a prod 500: N/A; for CLI errors, use printed command, inspect stderr, adjust params; write postmortem.
- Explain auth: N/A; all local; focus on file system permissions.
- Scale to 10×: GPU builds, parameter autotuning, and caching.

## 60‑Minute Cram Checklist
1) Read this brief; open `Core/utils/llama_runner.py`.
2) Skim `Core/router.py`.
3) Memorize search paths and basic params.
4) Prepare 1 setup improvement + 1 tuning idea.

## Red Flags to Avoid
- Don’t speculate on cloud inference—this is offline.
- If unsure: “I’d verify X, but concept is Y; implemented in `Clara/Core/utils/llama_runner.py`.”
- Keep answers precise and actionable.

