from __future__ import annotations
from dataclasses import dataclass
from agent_forge.models import ContextMessage


@dataclass
class SegmentConfig:
    max_context_messages: int = 20
    max_context_tokens: int = 8000
    min_context_messages: int = 3


class ContextBuilder:
    def __init__(self, config: SegmentConfig | None = None):
        self.config = config or SegmentConfig()

    def build(self, trigger: dict, history: list[dict]) -> list[ContextMessage]:
        by_ref = {m["ref_id"]: m for m in history}

        if trigger.get("thread_id"):
            thread_id = trigger["thread_id"]
            thread_msgs = [
                m for m in history
                if m["ref_id"] == thread_id or m.get("thread_id") == thread_id
            ]
            return self._to_context(thread_msgs)

        segment_refs: list[dict] = []
        self._trace_reply_chain(trigger, by_ref, segment_refs)

        if len(segment_refs) < self.config.min_context_messages:
            channels = trigger.get("channels", [])
            channel = channels[0] if channels else None
            for m in reversed(history):
                if m["ref_id"] in {s["ref_id"] for s in segment_refs}:
                    continue
                if channel is None or channel in m.get("channels", []):
                    segment_refs.insert(0, m)
                if len(segment_refs) >= self.config.max_context_messages:
                    break

        seen = set()
        deduped = []
        for m in segment_refs:
            if m["ref_id"] not in seen:
                seen.add(m["ref_id"])
                deduped.append(m)

        return self._to_context(deduped[:self.config.max_context_messages])

    def _trace_reply_chain(self, msg: dict, by_ref: dict[str, dict], result: list[dict]) -> None:
        chain = []
        current = by_ref.get(msg["ref_id"])
        if current is None:
            return
        while current:
            chain.append(current)
            reply_to = current.get("reply_to")
            current = by_ref.get(reply_to) if reply_to else None
        result.extend(reversed(chain))

    def _to_context(self, messages: list[dict]) -> list[ContextMessage]:
        return [
            ContextMessage(
                content=m["content"], author=m["author"],
                ref_id=m["ref_id"], timestamp=m.get("timestamp", ""),
            )
            for m in messages
        ]
