"""
Research team demo — a three-agent workflow orchestrated sequentially.

Flow:
  1. Researcher gathers facts about the topic
  2. Writer summarizes for a general audience
  3. Critic reviews the summary

Each agent is one completion call. The orchestrator passes context forward.
"""

from __future__ import annotations

from simple_agents import Agent, Evaluator, Orchestrator, WorkflowStep, create_provider


def build_research_team(provider_name: str = "auto") -> Orchestrator:
    provider = create_provider(provider=provider_name)

    # Sub-agents share the same provider but have different roles/prompts.
    # Swap `create_provider(model="gpt-4o")` or another backend to use any model.
    researcher = Agent("Researcher", "researcher who collects factual bullet points", provider)
    writer = Agent("Writer", "writer who explains topics clearly for beginners", provider)
    critic = Agent("Critic", "critic who reviews drafts for accuracy and clarity", provider)

    return Orchestrator(
        name="Orchestrator",
        provider=provider,
        agents={
            "researcher": researcher,
            "writer": writer,
            "critic": critic,
        },
        evaluator=Evaluator(),
    )


def run_demo(task: str = "Explain quantum computing for beginners", provider: str = "auto") -> None:
    orchestrator = build_research_team(provider_name=provider)

    print("=" * 60)
    print("SIMPLE AGENTS — Multi-Agent Workflow Demo")
    print("=" * 60)
    print(f"\nTask: {task}\n")

    print("--- Orchestrator plans the workflow ---")
    plan = orchestrator.plan(task)
    print(plan)
    print()

    steps = [
        WorkflowStep(
            agent_name="researcher",
            task="Research this topic and list the most important facts: {task}",
        ),
        WorkflowStep(
            agent_name="writer",
            task="Write a short, clear summary for beginners based on the research: {task}",
        ),
        WorkflowStep(
            agent_name="critic",
            task="Review the summary for accuracy and clarity. Give a score out of 10.",
        ),
    ]

    result = orchestrator.run_workflow(
        task=task,
        steps=steps,
        eval_checks=[
            Evaluator().check_nonempty,
            lambda t: Evaluator().check_contains(t, "accurate"),
        ],
    )

    writer_output = next(s.content for s in result.steps if s.agent_name == "Writer")
    content_eval = Evaluator().check_contains(writer_output, "quantum")

    for step in result.steps:
        print(f"--- {step.agent_name} ---")
        print(step.content)
        print()

    print("--- Final output (from last agent) ---")
    print(result.final_output)
    print()

    print("--- Evaluations (final output) ---")
    for ev in result.evaluations:
        status = "PASS" if ev.passed else "FAIL"
        print(f"  [{status}] {ev.message} (score={ev.score:.2f})")

    status = "PASS" if content_eval.passed else "FAIL"
    print(f"  [{status}] writer {content_eval.message} (score={content_eval.score:.2f})")

    print("\n--- Memory snapshot ---")
    for entry in orchestrator.memory.history:
        print(f"  {entry['agent']}: {entry['event'][:70]}...")


if __name__ == "__main__":
    run_demo()
