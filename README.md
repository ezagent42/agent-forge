# AgentForge

AI Agent lifecycle management for [EZAgent42](https://github.com/ezagent42) — spawn, destroy, sleep, wake, chat.

## Features

- **Template Registry** — TOML-based Agent templates (code-reviewer, task-worker, security-auditor)
- **Instance Manager** — spawn/destroy/sleep/wake Agent instances
- **Lifecycle State Machine** — CREATED → ACTIVE ⇄ SLEEPING → DESTROYED
- **Resource Guard** — agent limits, concurrent limits, API budget, sandbox checks
- **Context Builder** — three-layer conversation context (thread → reply chain → channel)
- **Cooperation Engine** — Pipeline (serial) and Ensemble (parallel) Agent patterns
- **Role Matcher** — StaffingRule-based role-to-template mapping with auto_spawn
- **Adapter Protocol** — pluggable AI backends (Claude Code adapter included)

## Install

```bash
pip install agent-forge
```

## Quick Start

```python
from agent_forge import AgentForge

forge = AgentForge()
forge.templates.load_from_dir("templates/")
instance = forge.spawn(template_id="code-reviewer", name="reviewer-1")
```

## Templates

Preset templates in `templates/`:

| Template | Purpose | Tools |
|----------|---------|-------|
| `code-reviewer` | PR quality and security review | Read, Search, Bash(read-only) |
| `task-worker` | General task execution | Read, Write, Edit, Bash, Search |
| `security-auditor` | Security vulnerability analysis | Read, Search, Bash(read-only) |

## License

Apache 2.0
