# AGENTS.md — Codex Working Rules

This file defines how Codex or any AI coding agent must work in this repository.

## 1. Follow the user's instruction exactly

Codex must only change what the user explicitly asks to change.

Codex must not:

- modify code outside the requested scope;
- rewrite unrelated files;
- redesign unrelated modules;
- rename files, functions, classes, variables, or folders unless the user asks for it;
- change public APIs, command-line interfaces, or file formats unless the task requires it;
- perform broad cleanup, formatting, dependency changes, or refactoring without permission.

If the requested change requires touching additional files, Codex must keep the change as small as possible and explain why those files needed to change in `Creating_log.md`.

## 2. Do not delete code carelessly

Codex must not delete code casually or speculatively.

Before deleting any code, Codex must check whether the code is still needed by existing functionality, current scripts, tests, configuration, or the overall application flow.

If code looks unnecessary but the need is not fully clear, Codex should prefer one of these safer options:

- leave it unchanged;
- add a short TODO comment;
- ask the user before deleting it.

Codex must never remove code only because it looks old, messy, duplicated, or unused at first glance.

## 3. Preserve existing required functionality

Every added or changed code block must preserve the functionality that already needs to work.

Before finishing a task, Codex must check that:

- existing required features still work;
- existing data flow is not broken;
- existing scripts still make sense;
- existing configuration is not silently invalidated;
- new code does not create disconnected or unreachable logic;
- the whole codebase still has a clear end-to-end logical flow.

A new feature is acceptable only when it connects cleanly with the existing project logic and does not break the current working path.

## 4. Keep the codebase globally coherent

Codex must think about the whole project, not only the edited file.

When adding code, Codex must ensure that:

- inputs and outputs are clear;
- new functions are actually called or intentionally prepared for later use;
- file paths and dependencies are consistent;
- error handling does not hide important failures;
- the change fits the existing architecture;
- the final code path is logically closed from start to finish.

Do not add isolated code blocks that are not connected to the rest of the project unless the user explicitly asks for a standalone draft or experiment.

## 5. Keep changes small and safe

Codex should prefer incremental, easy-to-review changes.

For each task, Codex should:

1. understand the exact request;
2. identify the smallest necessary edit;
3. preserve existing structure and naming where possible;
4. avoid new dependencies unless necessary;
5. avoid large abstractions unless they directly solve the requested problem;
6. leave clear TODOs for uncertain follow-up work instead of guessing.

## 6. Update `Creating_log.md` after every meaningful change

After every meaningful code or documentation change, Codex must append a new entry to `Creating_log.md` in the same folder as this file.

The log must be written in both English and Chinese.

New entries must be added in chronological order after previous entries.

Each entry must include:

- time or date of the change;
- files changed;
- what changed;
- code changes;
- thought process;
- why the new code or change was added;
- why the previous code needed to change;
- problems encountered during the change;
- how those problems were solved;
- what better result, functionality, or user experience the change brings;
- remaining risks or TODOs.

## 7. Required `Creating_log.md` entry template

Use this template for every meaningful change:

```markdown
## YYYY-MM-DD HH:MM — Short Change Title

### English

**Files changed:**
- `path/to/file`

**What changed:**
- ...

**Code changes:**
- ...

**Thought process:**
- ...

**Why this code/change was added:**
- ...

**Why the previous code needed to change:**
- ...

**Problems encountered:**
- ...

**Solution:**
- ...

**Better result / user experience:**
- ...

**Remaining risks / TODOs:**
- ...

### 中文

**修改文件：**
- `path/to/file`

**修改内容：**
- ...

**代码变化：**
- ...

**思考流程：**
- ...

**为什么添加这个代码/修改：**
- ...

**为什么之前的代码需要修改：**
- ...

**遇到的问题：**
- ...

**解决方式：**
- ...

**带来的更好效果 / 用户体验：**
- ...

**剩余风险 / TODO：**
- ...
```

## 8. Final checklist before finishing

Before considering a task complete, Codex must check:

- Did I follow the user's exact instruction?
- Did I avoid modifying unrelated code?
- Did I avoid deleting code without a clear reason?
- Did I preserve all existing required functionality?
- Did I keep the codebase globally coherent?
- Did I avoid unnecessary dependencies or broad refactoring?
- Did I update `Creating_log.md` for meaningful changes?
- Did I document remaining risks or TODOs?

If any answer is no, Codex must fix the issue before finishing.