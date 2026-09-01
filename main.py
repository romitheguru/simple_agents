"""Entry point for the simple-agents learning framework."""

import argparse

from examples.research_team import run_demo


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run a simple multi-agent workflow demo (mock or OpenAI completions)."
    )
    parser.add_argument(
        "--task",
        default="Explain quantum computing for beginners",
        help="Task for the agent team to work on",
    )
    parser.add_argument(
        "--provider",
        choices=["auto", "mock", "openai"],
        default="auto",
        help="LLM backend: auto (mock without API key), mock, or openai",
    )
    args = parser.parse_args()
    run_demo(task=args.task, provider=args.provider)


if __name__ == "__main__":
    main()
