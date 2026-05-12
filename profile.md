---
allowed-tools: Bash(python3:*), Bash(ls:*), Bash(diff:*), Bash(test:*), Bash(grep:*), Bash(rm:*), Read, Edit, Write
argument-hint: [bootstrap|regenerate|audit|merge <path>|show]
description: Maintain personal behavioral playbook from Claude Code memories
---

Personal AI behavioral profile. Extracts cross-project preferences from Claude Code's auto-memory and synthesizes them into a `playbook.rules.md` file that's auto-loaded into every session via `~/.claude/CLAUDE.md`.

**Profile directory:** `${AI_PROFILE_DIR:-$HOME/.ai-profile}` — set the env var in your shell rc to override, or symlink `~/.ai-profile` to your preferred location.

**Files inside profile dir:**
- `playbook.rules.md` — LLM-loaded rule format (R1, R2, ...) — auto-loaded
- `playbook.md` — human-readable companion
- `scripts/extract_memories.py` — memory extraction tool (comes with the cloned repo)

Decide flow based on `$ARGUMENTS`:

---

## If `bootstrap` — first-time setup

Goal: clean slate to working profile in one command.

**Step 1. Resolve and validate profile dir.**
- Run: `PROFILE_DIR="${AI_PROFILE_DIR:-$HOME/.ai-profile}"; ls -la "$PROFILE_DIR/scripts/extract_memories.py" 2>&1`
- If extract script missing → tell user: "Profile dir `$PROFILE_DIR` is not set up. Clone the reference repo: `git clone https://github.com/deadchack123/ai-profile.git \"$PROFILE_DIR\"` (or set `AI_PROFILE_DIR` to where you cloned it) and re-run `/profile bootstrap`." STOP.

**Step 2. Check for existing playbook.**
- Run: `test -f "$PROFILE_DIR/playbook.rules.md" && echo EXISTS || echo MISSING`
- If `EXISTS`: warn user "playbook.rules.md already exists in `$PROFILE_DIR`. Bootstrap will REGENERATE it from your memories. Existing reference content (if cloned from the public repo) will be replaced. Continue? [y/n]". Wait for confirmation. On `n` — STOP.

**Step 3. Extract memories.**
- Run: `python3 "$PROFILE_DIR/scripts/extract_memories.py" --out /tmp/profile_extract.md`
- Read `/tmp/profile_extract.md`.
- Count user/feedback entries (look for `### user (N)` and `### feedback (N)` headers in the extract).

**Step 4. Sanity check on data volume.**
- If `user + feedback < 10` → tell user: "You have only N memories across M projects. Profile will be thin and not very useful. Recommended path: work with Claude Code for a few more weeks, give explicit 'do this / don't do this' feedback during sessions (these become memories), then re-run `/profile bootstrap`. Synthesize anyway with current data? [y/n]". On `n` — cleanup `/tmp/profile_extract.md` and STOP.

**Step 5. Synthesize the playbook.**

Structure: rules grouped under thematic `##` headers, each rule is `### R<N>`. Sequential numbering R1..RN across all themes (numbers don't reset per theme).

Themes to use (`##` headers, in this order, omit any with zero rules):
- `## Communication` — how the agent talks to the user, output format
- `## Workflow` — how to approach tasks, planning, escalation
- `## Git` — commits, branches, push policy
- `## Cost / tokens` — LLM resource management
- `## Tooling` — env, installs, infra commands
- `## Code principles` — writing/reviewing code
- `## Verification` — checking that work is real
- `## Documentation` — knowledge maps, handoffs

Format for every rule:

```
### R<N> — <short title>

**WHEN:** <observable trigger>
**DO:**
- <imperative action>
- <imperative action>

**DON'T:**
- <concrete anti-pattern>

**EXCEPT:** <when rule does not apply> (optional, omit if none)

**WHY:** <one-line rationale>
```

Synthesis principles:

- **Imperative voice.** "Do X. Don't do Y." Not "user prefers X".

- **Observable triggers — required.** Each rule's WHEN must be a concrete action by user / observable state of code / specific situation in the session. "When user types `план`" ✅. "When user gives negative feedback" ❌ (too broad — happens every session). "When working with anything" → drop the rule, it's philosophy not a behavioral trigger.

- **Concrete DON'T examples** — list specific anti-patterns the user has actually corrected, not abstract anti-principles.

- **Numeric thresholds where extractable.** "≥$0.10 OR ≥2 minutes" beats "expensive operations".

- **Don't merge rules with different WHEN.** Each distinct trigger gets its own rule, even if topics are related. "When introducing a new key name" ≠ "When introducing a new architectural pattern" ≠ "When seeing existing code that looks wrong" — three different triggers, three separate rules. Same for "sketch before code" vs "decompose to ≤1-2 days" vs "cost announce" vs "iterative bench" — separate.

- **Test for project-specific — DROP if any apply.** A memory is project-specific when it encodes:
  - A specific product / domain workflow (the thing the user is *building*, not how they build it).
  - A specific type of system being built where the rule only applies in that build context.
  - A specific team's convention (file layout choice, ticket-ID format, naming scheme).
  - A specific library/framework/runtime quirk (a particular API gotcha, version compat fix).
  - A specific tool path or service name unique to one repo.

  These go in project CLAUDE.md, NOT in this profile. Strong feedback signal does NOT make a memory cross-project — check trigger generality first.

- **CRITICAL: Two-step analysis for every memory — behavior + trigger.** Before deciding keep/drop, ALWAYS separate:
  1. **The behavior** the memory describes (the DO / DON'T action — output format, procedure, habit, communication pattern).
  2. **The trigger** that activates it (what situation in the session causes this behavior to apply).

  **Source project ≠ application context.** A memory's framing reflects where the user noticed the issue (the past), not where the rule applies (the future). Always re-derive the trigger in domain-neutral terms before judging project-specificity.

  This is the most common failure mode: rule gets dropped because the source memory talks about a specific product (e.g., a teaching app), but the underlying behavior is portable. Or rule gets kept because the source memory has strong feedback signal, but the trigger only exists in that one product.

- **Tricky-case examples to calibrate judgment:**

  **Case A — looks specific, actually KEEP:**
  Memory says: "In the daily-reading block of a lesson, send URLs as raw text in code block, not as markdown links — student copies them on mobile."
  Wrong move: drop because "daily-reading lesson" sounds teaching-specific.
  Right move: behavior = "output URLs as raw code-block, no markdown wrapper". Trigger = "when sending URLs the user will copy". That trigger fires in any session displaying URLs. KEEP.

  **Case B — looks similar, but DROP:**
  Memory says: "Don't put hint in parentheses after Russian phrase during translation drill — student translates from the hint."
  Behavior = "no answer-hint in parens during exercise". Trigger = "during a drill / recall exercise". That trigger only exists in teaching/coaching products. DROP.

  **Case C — KEEP after generalization:**
  Memory says: "Always run `ruff check + mypy` before commit because pre-commit hook is configured."
  Wrong move: drop because "ruff/mypy" = Python-specific.
  Right move: behavior = "run configured lint/format/typecheck locally before commit". Trigger = "about to commit when project has lint configs". Both portable. KEEP, drop specific tool names.

  **Case D — DROP, no salvage:**
  Memory says: "Specific library X's class Y has readonly attribute Z; use private `_Z` to override."
  Behavior = library-specific quirk. Trigger only fires when using that exact library. DROP — no generalization rescues this.

  **Case E — looks general, but DROP:**
  Memory says: "When designing prompt for autonomous background agent on cheap LLM, default action = inaction with numeric thresholds."
  Behavior pattern looks portable (prompt design). But trigger ("when designing prompts for autonomous LLM agents") only fires in build-an-agent-system projects. If user doesn't build agent systems regularly, DROP.

- **KEEP rule when EITHER condition holds:**
  - Behavior + generalized trigger both fire in projects across multiple unrelated domains (web / CLI / data pipeline / mobile / scientific / game).
  - Memory expresses a *preference about how to interact with the user* (communication style, output format, when to ask vs act) — those are user-personal, not project-personal.

- **DROP rule when:**
  - Generalized trigger only fires in the specific domain of the source project.
  - Behavior depends on a specific library/framework/tool that user doesn't use everywhere.
  - Rule encodes a one-time research conclusion ("X is not viable as Y") — not a behavior.

- **Group thematically using `##` headers from the list above.** Within each theme, order rules by trigger frequency (most common first). If a theme has 0 rules — omit its header entirely.

- **Number rules R1, R2, ... sequentially across themes** in display order. Numbers do NOT reset per theme — R1..R5 might be communication, R6..R12 workflow, etc.

- **Target volume:** roughly one rule per 1.5-2 source memories after dropping project-specific. If you started with 50 memories and ended with 8 rules — you over-merged or over-dropped, re-check. If you ended with 60 rules — you split too granularly, look for true duplicates. Concrete checkpoint: count memories that pass the WHEN-generality test, then rules should be ~50-70% of that count (some merge into single rules with the same trigger).

**Step 6. Write `playbook.rules.md`** to `$PROFILE_DIR/playbook.rules.md`. File header:

```
# Playbook (LLM rules)

LLM-ориентированная версия. Каждое правило: WHEN / DO / DON'T / EXCEPT / WHY. Императив, без прозы. Группировка по темам через `##`, правила нумерованы R1..RN сквозно.

---
```

Then thematic sections with rules per the format in Step 5.

**Step 7. Wire up auto-loading.**
- Read `~/.claude/CLAUDE.md`.
- If it doesn't already contain a reference to `playbook.rules.md`, append the line: `@$PROFILE_DIR/playbook.rules.md` (with `$PROFILE_DIR` resolved to absolute path).
- `AI_PROFILE_DIR` env var doesn't expand in CLAUDE.md — always resolve to absolute path.

**Step 8. Cleanup.**
- `rm /tmp/profile_extract.md`.

**Step 9. Report to user.**
- Number of rules generated.
- Path to `playbook.rules.md`.
- Confirmation auto-load is wired in `~/.claude/CLAUDE.md`.
- Note: "open a new Claude Code session to see the loaded profile — current session's context was set before the change".

---

## If `regenerate` — update existing playbook

Use when memories accumulated since last bootstrap. Same as bootstrap but with diff-and-confirm:

1. Resolve `PROFILE_DIR` (Step 1 from bootstrap). Require existing `playbook.rules.md` — if missing, tell user "no existing playbook — run `/profile bootstrap` first".
2. Run extract (Step 3 from bootstrap).
3. Read current `playbook.rules.md`.
4. Synthesize new playbook (Step 5).
5. **Show diff** to user: NEW rules / REMOVED rules (with reason for removal) / MODIFIED rules (before/after).
6. Ask: "Apply this regeneration? [y/n]".
7. On `y`: Write new playbook + companion `playbook.md`. On `n`: discard, report what stayed the same.
8. Cleanup.

**Important:** preserve manually-edited rules. If a rule has hand-tuned phrasing/thresholds not derivable from memories, keep it unless user explicitly says "wipe everything".

---

## If `audit` — check staleness, no rewrite

1. Resolve `PROFILE_DIR`, run extract.
2. Read current playbook.
3. Report only:
   - **Rules with no supporting memory** (likely obsolete or invented).
   - **Recurring patterns in memories not yet in playbook** (candidates for new rules).
   - **Rules whose trigger contradicts a recent memory** (drift).
4. Don't write anything. End with: "run `/profile regenerate` to apply changes".

---

## If `merge <path>` — combine two playbooks

Goal: merge a colleague's playbook into yours.

1. Read `<path>` (the other playbook).
2. Read your current `playbook.rules.md`.
3. Output 4 buckets:
   - **Identical rules** (same trigger + same action) — no action.
   - **Compatible additions** (rules in other but not yours, no conflict) — propose adding.
   - **Conflicts** (same trigger, different action) — show side-by-side, ask user to choose.
   - **Style differences** (e.g., your R5 covers same ground as their R12) — propose unification.
4. For each conflict/addition, ask: keep mine / take theirs / write hybrid / skip.
5. Apply approved changes via Edit.

Human-in-the-loop. Don't auto-merge.

---

## If `show` or no args

Run: `PROFILE_DIR="${AI_PROFILE_DIR:-$HOME/.ai-profile}"; ls -la "$PROFILE_DIR" 2>/dev/null; grep -c '^## R' "$PROFILE_DIR/playbook.rules.md" 2>/dev/null; grep -F "playbook.rules.md" ~/.claude/CLAUDE.md 2>/dev/null`

Report:
- Profile dir resolved path + whether `AI_PROFILE_DIR` env var is set vs default.
- Files present.
- Number of rules (count of `## R` headers).
- Last-modified time.
- Whether `~/.claude/CLAUDE.md` auto-loads the playbook.
- One-line summary of each subcommand.

---

## Universal notes

- Never auto-commit changes to playbook files. User reviews and approves.
- Don't add filler text or marketing-speak to the playbook. Rules only.
- If memories conflict (e.g., "always X" in one project, "never X" in another), surface the conflict to user and ask which is current — don't pick silently.
- Project-specific quirks (lib APIs, framework conventions) belong in project's `CLAUDE.md`, not in this profile.
