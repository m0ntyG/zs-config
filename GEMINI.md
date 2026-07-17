# General

Be extremely concise. sacrifice grammer for the sake of concision.

# Planning

## Plan Expansion & Execution Rules

When generating, reviewing, or expanding any plan — whether from Plan Mode or
a user request — you MUST follow these rules without exception.

Plans are executed exclusively by an AI agent. The user is not a developer.
Therefore, zero ambiguity is acceptable. Every step must be so precise that
there is only one possible way to interpret and execute it.

---

### Rules

#### 1. Atomic Steps Only
Every task must be broken down until it cannot be split further without
losing context. One step = one file, one function, or one logical change.
If a step touches more than one concern, split it.

#### 2. No Vague Language
Words like "update", "improve", "refactor", "handle", or "adjust" are
forbidden without explicit qualification. Always specify WHAT, WHERE, and HOW.

#### 3. Pseudo Code is Mandatory
Every step that involves writing or modifying logic MUST include pseudo code.
The pseudo code must reflect the actual project logic and existing code style.
It documents intent — not syntax — but must be precise enough that only one
implementation is possible.

#### 4. Blast Radius Assessment
Every step MUST include an assessment of what could break or be affected,
covering: files, modules, functions, APIs, databases, external services,
other teams or systems, and deployment environments (dev/staging/prod).

#### 5. Impact & Negative Consequences
Every step MUST explicitly state potential negative side effects, regressions,
performance impacts, or unintended behavioral changes that could result from
the change.

#### 6. File Placement & Removal
Every step MUST explicitly state:
- WHERE new code goes (exact file path and location within the file)
- WHAT must be deleted or removed and from WHERE

#### 7. Spaghetti Code Risk Check
Before finalising any step, evaluate it against the following checklist.
Any violation MUST be flagged as a risk with a suggested resolution:

- **S — Single Responsibility (SOLID)**
  Does each function/class do exactly one thing?
  No function should have more than one reason to change.

- **C — Separation of Concerns**
  Is business logic strictly separated from data access, configuration,
  and presentation? Nothing mixed.

- **D — Size Limits**
  Functions: max 50 lines. Files: max 200 lines.
  If a new function/file exceeds this, the design must be reconsidered.

- **E — God Class / God Function Detection**
  Does any existing or new class/function "know too much" or "do too much"?
  Flag immediately if a class has more than one domain of responsibility.

- **G — Naming Clarity**
  Can every new function, class, variable, and file name be explained in
  one sentence without using the word "and"?
  If not, the naming — and likely the design — is wrong.

#### 8. Project Goal Alignment
Every step MUST include a brief statement confirming that the change still
serves the original project goal as defined in the project documentation.
Reference files: `docs/SC Hackathon - Account Discovery PRD.md` and `.plan/MVP0_Implementation_Plan.md`.
If a step risks diverging from the project goal, it MUST be flagged
explicitly before execution.

#### 9. Test Coverage Gate
Every step that adds or modifies logic MUST be accompanied by a description
of how it can be tested. If a step cannot be tested in isolation, it is
designed incorrectly and must be redesigned.

---

### Mandatory Step Template

Every plan step MUST use exactly this structure. No exceptions.

---

##### Step [N]: [Precise, unambiguous title — no vague verbs]

**What & Why**
[One short paragraph. What exactly is being done and why is this step
necessary. No assumptions, no interpretation space.]

**File Placement**
- New code → `path/to/file.py` → [exact location: after function X / before class Y / new file]
- Remove → `path/to/file.py` → [exact function/class/block to delete, or "nothing to remove"]

**Pseudo Code**

```python
# Describe the logic precisely — not syntax, but intent + structure
# Must reflect existing project patterns and naming conventions
#
# Example:
# function do_specific_thing(input):
#     validate input is not empty
#     call existing_helper(input)
#     if result is valid:
#         write result to database
#     else:
#         raise specific error with message
```

**Blast Radius**
- Files affected: [list every file that is read, written, or imported]
- Functions affected: [list every function that changes or is called differently]
- APIs / Services / DBs affected: [list or "none"]
- Deployment risk: [none / low / medium / high] — [one sentence reason]

**Impact & Negative Consequences**
- [Explicit list of potential regressions, side effects, or risks]
- [If none identified: state "No negative consequences identified" — do not leave blank]

**Spaghetti Code Risk Check**
- [ ] Single Responsibility: [pass / RISK: describe the violation and resolution]
- [ ] Separation of Concerns: [pass / RISK: describe the violation and resolution]
- [ ] Size Limits: [pass / RISK: describe the violation and resolution]
- [ ] God Class/Function: [pass / RISK: describe the violation and resolution]
- [ ] Naming Clarity: [pass / RISK: describe the violation and resolution]

**Project Goal Alignment**
[One sentence confirming this step serves the goal in docs/MVP0.md,
or explicitly flagging divergence with a recommended action.]

**Test Coverage**
[Describe exactly how this step can be verified or tested in isolation.
Name the test file, the test case, and the expected outcome.]

---


# Commit

- Commit at least after every code change, use a meaningful comment

# Code Intelligence Rules

## MANDATORY: Use better-code-review-graph MCP Tools

You have access to the `better-code-review-graph` MCP server. ALWAYS use this MCP server when interacting with the code.

### FORBIDDEN:
- ReadFile for dependency or impact analyses
- ReadFolder to explore the project structure
- Grep/Glob for semantic search

### INSTEAD, always use MCP-Tools:

| Question | MCP-Tool |
|---|---|
| Who calls function X? | `query` with `callers_of` + target = "function_name" |
| What does file X import? | `query` with `imports_of` + target = "file_name" |
| Blast radius of a change? | `query` with `callers_of` + `importers_of` combined |
| File summary | `query` with `file_summary` |
| Semantic search | `search` tool with natural search query |


### Workflow for Code Changes:
1. Call `graph` build/update
2. Call `query` with the appropriate pattern
3. ONLY if MCP returns no result → ReadFile as fallback

## Agent skills

### Issue tracker

Issues and PRDs for this repo live as GitHub issues. External PRs are triaged. See `docs/agents/issue-tracker.md`.

### Triage labels

Using standard triage labels (needs-triage, needs-info, ready-for-agent, ready-for-human, wontfix). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context layout with a global `CONTEXT.md` at root. See `docs/agents/domain.md`.

