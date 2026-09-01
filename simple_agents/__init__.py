"""A minimal multi-agent framework for learning how orchestration works."""

from simple_agents.agent import Agent, AgentResult
from simple_agents.eval import EvalResult, Evaluator
from simple_agents.memory import Memory
from simple_agents.model import Message, ModelProvider, create_provider
from simple_agents.orchestrator import Orchestrator, WorkflowResult, WorkflowStep

__all__ = [
    "Agent",
    "AgentResult",
    "EvalResult",
    "Evaluator",
    "Memory",
    "Message",
    "ModelProvider",
    "Orchestrator",
    "WorkflowResult",
    "WorkflowStep",
    "create_provider",
]
