# simple-agents

A **minimal multi-agent framework** for learning how orchestration works. No heavy abstractions — just completion API calls, clear roles, and a sequential workflow you can read in one sitting.

## What you'll learn

- How an **orchestrator** delegates work to **sub-agents**
- How each agent is a single **completion/response** call with a role-specific system prompt
- How **context** flows from one agent to the next
- How to swap **any model** via a small provider interface
- A tiny **memory** layer and **eval** checks on outputs

## Architecture

```
User task
    │
    ▼
Orchestrator (plans + delegates)
    │
    ├── Researcher agent  → completion API → facts
    │         │
    │         ▼ (context passed forward)
    ├── Writer agent      → completion API → summary
    │         │
    │         ▼
    └── Critic agent      → completion API → review
                │
                ▼
         Eval + shared memory
```

Each box labeled "agent" is one `provider.complete(messages)` call — the same pattern as Chat Completions or Responses APIs.

## Quick start

```bash
# Install dependencies
uv sync --frozen

# Run demo with mock completions (no API key needed)
uv run python main.py --provider mock

# Run with OpenAI when OPENAI_API_KEY is set
export OPENAI_API_KEY=sk-...
uv run python main.py --provider openai
```

## Core concepts

### 1. Model provider (`simple_agents/model.py`)

Any backend implements `complete(messages) -> str`:

- `MockProvider` — deterministic responses for learning without API keys
- `OpenAIProvider` — real Chat Completions API
- `create_provider("auto")` — picks OpenAI if `OPENAI_API_KEY` is set, otherwise mock

### 2. Agent (`simple_agents/agent.py`)

An agent has a **name**, **role** (system prompt), and **provider**. One `run()` = one API call:

```python
from simple_agents import Agent, create_provider

provider = create_provider()
researcher = Agent("Researcher", "researcher who lists facts", provider)
result = researcher.run("Research quantum computing")
print(result.content)
```

### 3. Orchestrator (`simple_agents/orchestrator.py`)

The orchestrator owns shared memory and runs agents in sequence:

```python
from simple_agents import Orchestrator, WorkflowStep

orchestrator = Orchestrator("Orchestrator", provider, agents={"researcher": researcher, ...})

result = orchestrator.run_workflow(
    task="Explain quantum computing",
    steps=[
        WorkflowStep("researcher", "Research: {task}"),
        WorkflowStep("writer", "Summarize: {task}"),
        WorkflowStep("critic", "Review the summary"),
    ],
)
```

### 4. Memory (`simple_agents/memory.py`)

Shared key-value store + event log for one workflow run.

### 5. Eval (`simple_agents/eval.py`)

Simple checks: non-empty, contains keyword, minimum length.

## Project layout

```
simple_agents/
  model.py        # Provider abstraction (mock + OpenAI)
  agent.py        # Single agent = one completion call
  orchestrator.py # Multi-agent workflow coordinator
  memory.py       # Tiny shared memory
  eval.py         # Output checks
examples/
  research_team.py  # Researcher → Writer → Critic demo
main.py             # CLI entry point
```

## Using a different model

Pass a different model name or base URL when creating the provider:

```python
from simple_agents.model import OpenAIProvider

provider = OpenAIProvider(model="gpt-4o", base_url="https://your-compatible-endpoint/v1")
```

Or use `create_provider(provider="openai", model="gpt-4o")`.

## Roadmap ideas (from original goals)

- [x] Orchestrator
- [x] Sub-agents
- [x] Any model via provider interface
- [x] Multi-agent orchestration
- [x] Eval layer
- [x] Small memory layer
- [ ] Parallel agent execution
- [ ] Tool / function calling
- [ ] Persistent memory across runs

## License

MIT (add your license as needed)
