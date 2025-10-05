"""Execution tracing for agents."""

import json
import uuid
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional

from pydantic import BaseModel, Field


class TraceEvent(BaseModel):
    """A single trace event."""

    event_id: str
    trace_id: str
    timestamp: datetime
    event_type: str  # "task_start", "task_end", "tool_call", "llm_call", etc.
    agent_name: str
    data: Dict[str, Any] = Field(default_factory=dict)
    parent_id: Optional[str] = None
    duration_ms: Optional[float] = None


class Trace(BaseModel):
    """A complete execution trace."""

    trace_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    agent_name: str
    task: str
    events: List[TraceEvent] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def duration_ms(self) -> Optional[float]:
        """Calculate total duration in milliseconds."""
        if self.end_time:
            delta = self.end_time - self.start_time
            return delta.total_seconds() * 1000
        return None


class Tracer:
    """Execution tracer for agents."""

    def __init__(self, agent_name: str, enabled: bool = True) -> None:
        """Initialize tracer.

        Args:
            agent_name: Name of the agent
            enabled: Whether tracing is enabled
        """
        self.agent_name = agent_name
        self.enabled = enabled
        self.current_trace: Optional[Trace] = None
        self.traces: List[Trace] = []
        self.event_stack: List[str] = []  # For nested events

    def start_trace(self, task: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Start a new trace.

        Args:
            task: Task being executed
            metadata: Optional metadata

        Returns:
            Trace ID
        """
        if not self.enabled:
            return ""

        trace_id = str(uuid.uuid4())
        self.current_trace = Trace(
            trace_id=trace_id,
            start_time=datetime.now(),
            agent_name=self.agent_name,
            task=task,
            metadata=metadata or {},
        )
        return trace_id

    def end_trace(self) -> None:
        """End the current trace."""
        if not self.enabled or not self.current_trace:
            return

        self.current_trace.end_time = datetime.now()
        self.traces.append(self.current_trace)
        self.current_trace = None
        self.event_stack.clear()

    def add_event(
        self,
        event_type: str,
        data: Optional[Dict[str, Any]] = None,
        parent_id: Optional[str] = None,
    ) -> str:
        """Add an event to the current trace.

        Args:
            event_type: Type of event
            data: Event data
            parent_id: Parent event ID for nested events

        Returns:
            Event ID
        """
        if not self.enabled or not self.current_trace:
            return ""

        event_id = str(uuid.uuid4())
        event = TraceEvent(
            event_id=event_id,
            trace_id=self.current_trace.trace_id,
            timestamp=datetime.now(),
            event_type=event_type,
            agent_name=self.agent_name,
            data=data or {},
            parent_id=parent_id or (self.event_stack[-1] if self.event_stack else None),
        )

        self.current_trace.events.append(event)
        return event_id

    @contextmanager
    def span(
        self, event_type: str, data: Optional[Dict[str, Any]] = None
    ) -> Generator[str, None, None]:
        """Create a traced span (context manager).

        Args:
            event_type: Type of event
            data: Event data

        Yields:
            Event ID
        """
        if not self.enabled:
            yield ""
            return

        start_time = datetime.now()
        event_id = self.add_event(f"{event_type}_start", data)
        self.event_stack.append(event_id)

        try:
            yield event_id
        finally:
            end_time = datetime.now()
            duration_ms = (end_time - start_time).total_seconds() * 1000

            # Update start event with duration
            if self.current_trace:
                for event in self.current_trace.events:
                    if event.event_id == event_id:
                        event.duration_ms = duration_ms
                        break

            self.add_event(
                f"{event_type}_end",
                {**(data or {}), "duration_ms": duration_ms},
            )

            if self.event_stack and self.event_stack[-1] == event_id:
                self.event_stack.pop()

    def get_trace(self, trace_id: str) -> Optional[Trace]:
        """Get a trace by ID.

        Args:
            trace_id: Trace ID

        Returns:
            Trace or None
        """
        for trace in self.traces:
            if trace.trace_id == trace_id:
                return trace
        return None

    def get_all_traces(self) -> List[Trace]:
        """Get all traces.

        Returns:
            List of traces
        """
        return self.traces.copy()

    def save_trace(self, trace_id: str, file_path: str) -> None:
        """Save a trace to a JSON file.

        Args:
            trace_id: Trace ID
            file_path: Path to save file
        """
        trace = self.get_trace(trace_id)
        if not trace:
            return

        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(trace.model_dump(), f, indent=2, default=str)

    def load_trace(self, file_path: str) -> Optional[Trace]:
        """Load a trace from a JSON file.

        Args:
            file_path: Path to trace file

        Returns:
            Loaded trace or None
        """
        path = Path(file_path)
        if not path.exists():
            return None

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return Trace(**data)

    def clear(self) -> None:
        """Clear all traces."""
        self.traces.clear()
        self.current_trace = None
        self.event_stack.clear()
