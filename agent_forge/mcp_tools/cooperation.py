from __future__ import annotations
from typing import Any
from agent_forge.core import AgentForge
from agent_forge.cooperation import PipelineStep


def _run_pipeline(
    forge: AgentForge,
    steps: list[dict[str, str]],
    input_text: str,
) -> dict[str, Any]:
    try:
        pipeline_steps = []
        for s in steps:
            forge.templates.get(s["template"])
            pipeline_steps.append(
                PipelineStep(role=s["role"], template=s["template"], trigger=s["trigger"])
            )
        pipeline = forge.cooperation.pipeline(
            name=f"pipeline-{len(steps)}steps", steps=pipeline_steps
        )
        return {
            "pipeline_name": pipeline.name,
            "steps": [
                {"role": s.role, "template": s.template, "trigger": s.trigger}
                for s in pipeline.steps
            ],
            "input": input_text[:200],
            "status": "created",
        }
    except (KeyError, ValueError) as e:
        return {"error": str(e)}


def _run_ensemble(
    forge: AgentForge,
    agents: list[dict[str, str]],
    input_text: str,
    strategy: str = "majority",
) -> dict[str, Any]:
    try:
        agent_names = []
        for a in agents:
            forge.templates.get(a["template"])
            agent_names.append(a["name"])
        ensemble = forge.cooperation.ensemble(
            name=f"ensemble-{len(agents)}agents",
            agents=agent_names,
            strategy=strategy,
        )
        return {
            "ensemble_name": ensemble.name,
            "agents": [{"template": a["template"], "name": a["name"]} for a in agents],
            "strategy": ensemble.strategy,
            "input": input_text[:200],
            "status": "created",
        }
    except (KeyError, ValueError) as e:
        return {"error": str(e)}


def register_cooperation_tools(server, forge: AgentForge):
    """Register pipeline and ensemble tools on the MCP server."""

    @server.tool()
    async def run_pipeline(steps: list[dict[str, str]], input_text: str) -> str:
        """Run a serial pipeline of agents. Each step triggers the next.

        Args:
            steps: List of pipeline steps, each with "role", "template", "trigger" keys
            input_text: Initial input for the pipeline
        """
        import json
        return json.dumps(
            _run_pipeline(forge, steps, input_text), ensure_ascii=False
        )

    @server.tool()
    async def run_ensemble(
        agents: list[dict[str, str]],
        input_text: str,
        strategy: str = "majority",
    ) -> str:
        """Run multiple agents in parallel and aggregate results.

        Args:
            agents: List of agents, each with "template" and "name" keys
            input_text: Input for all agents
            strategy: Aggregation strategy (default: "majority")
        """
        import json
        return json.dumps(
            _run_ensemble(forge, agents, input_text, strategy),
            ensure_ascii=False,
        )
