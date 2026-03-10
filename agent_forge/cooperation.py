from __future__ import annotations
from dataclasses import dataclass


@dataclass
class PipelineStep:
    role: str
    template: str
    trigger: str


@dataclass
class Pipeline:
    name: str
    steps: list[PipelineStep]

    def next_step(self, trigger: str) -> PipelineStep | None:
        for step in self.steps:
            if step.trigger == trigger:
                return step
        return None


@dataclass
class Ensemble:
    name: str
    agents: list[str]
    strategy: str


class CooperationEngine:
    @staticmethod
    def pipeline(name: str, steps: list[PipelineStep]) -> Pipeline:
        return Pipeline(name=name, steps=steps)

    @staticmethod
    def ensemble(name: str, agents: list[str], strategy: str = "majority") -> Ensemble:
        return Ensemble(name=name, agents=agents, strategy=strategy)
