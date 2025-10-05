"""Performance metrics collection for agents."""

import json
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class MetricValue(BaseModel):
    """A single metric value."""

    timestamp: datetime
    value: float
    labels: Dict[str, str] = Field(default_factory=dict)


class Metric(BaseModel):
    """A metric with its history."""

    name: str
    metric_type: str  # "counter", "gauge", "histogram"
    description: str = ""
    values: List[MetricValue] = Field(default_factory=list)

    def add_value(self, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        """Add a value to the metric."""
        self.values.append(
            MetricValue(
                timestamp=datetime.now(),
                value=value,
                labels=labels or {},
            )
        )

    def get_latest(self) -> Optional[float]:
        """Get the latest value."""
        if self.values:
            return self.values[-1].value
        return None

    def get_average(self) -> Optional[float]:
        """Calculate average value."""
        if not self.values:
            return None
        return sum(v.value for v in self.values) / len(self.values)

    def get_sum(self) -> float:
        """Calculate sum of all values."""
        return sum(v.value for v in self.values)

    def get_min(self) -> Optional[float]:
        """Get minimum value."""
        if not self.values:
            return None
        return min(v.value for v in self.values)

    def get_max(self) -> Optional[float]:
        """Get maximum value."""
        if not self.values:
            return None
        return max(v.value for v in self.values)


class MetricsCollector:
    """Metrics collector for agents."""

    def __init__(self, agent_name: str, enabled: bool = True) -> None:
        """Initialize metrics collector.

        Args:
            agent_name: Name of the agent
            enabled: Whether metrics collection is enabled
        """
        self.agent_name = agent_name
        self.enabled = enabled
        self.metrics: Dict[str, Metric] = {}
        self.timers: Dict[str, float] = {}

    def counter(
        self,
        name: str,
        value: float = 1.0,
        description: str = "",
        labels: Optional[Dict[str, str]] = None,
    ) -> None:
        """Increment a counter metric.

        Args:
            name: Metric name
            value: Value to add
            description: Metric description
            labels: Optional labels
        """
        if not self.enabled:
            return

        metric_name = f"{self.agent_name}.{name}"

        if metric_name not in self.metrics:
            self.metrics[metric_name] = Metric(
                name=metric_name,
                metric_type="counter",
                description=description,
            )

        # For counters, add to the current total
        current = self.metrics[metric_name].get_latest() or 0.0
        self.metrics[metric_name].add_value(current + value, labels)

    def gauge(
        self,
        name: str,
        value: float,
        description: str = "",
        labels: Optional[Dict[str, str]] = None,
    ) -> None:
        """Set a gauge metric.

        Args:
            name: Metric name
            value: Current value
            description: Metric description
            labels: Optional labels
        """
        if not self.enabled:
            return

        metric_name = f"{self.agent_name}.{name}"

        if metric_name not in self.metrics:
            self.metrics[metric_name] = Metric(
                name=metric_name,
                metric_type="gauge",
                description=description,
            )

        self.metrics[metric_name].add_value(value, labels)

    def histogram(
        self,
        name: str,
        value: float,
        description: str = "",
        labels: Optional[Dict[str, str]] = None,
    ) -> None:
        """Record a histogram value.

        Args:
            name: Metric name
            value: Value to record
            description: Metric description
            labels: Optional labels
        """
        if not self.enabled:
            return

        metric_name = f"{self.agent_name}.{name}"

        if metric_name not in self.metrics:
            self.metrics[metric_name] = Metric(
                name=metric_name,
                metric_type="histogram",
                description=description,
            )

        self.metrics[metric_name].add_value(value, labels)

    def start_timer(self, name: str) -> None:
        """Start a timer for duration tracking.

        Args:
            name: Timer name
        """
        if not self.enabled:
            return

        self.timers[name] = time.time()

    def stop_timer(
        self,
        name: str,
        labels: Optional[Dict[str, str]] = None,
    ) -> Optional[float]:
        """Stop a timer and record the duration.

        Args:
            name: Timer name
            labels: Optional labels

        Returns:
            Duration in milliseconds or None
        """
        if not self.enabled or name not in self.timers:
            return None

        start_time = self.timers.pop(name)
        duration_ms = (time.time() - start_time) * 1000

        self.histogram(
            f"{name}.duration_ms",
            duration_ms,
            description=f"Duration of {name} in milliseconds",
            labels=labels,
        )

        return duration_ms

    def get_metric(self, name: str) -> Optional[Metric]:
        """Get a metric by name.

        Args:
            name: Metric name (with or without agent prefix)

        Returns:
            Metric or None
        """
        # Try with agent prefix first
        metric_name = f"{self.agent_name}.{name}"
        if metric_name in self.metrics:
            return self.metrics[metric_name]

        # Try without prefix
        if name in self.metrics:
            return self.metrics[name]

        return None

    def get_all_metrics(self) -> Dict[str, Metric]:
        """Get all metrics.

        Returns:
            Dictionary of all metrics
        """
        return self.metrics.copy()

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of all metrics.

        Returns:
            Summary dictionary
        """
        summary = {}

        for name, metric in self.metrics.items():
            metric_summary = {
                "type": metric.metric_type,
                "description": metric.description,
                "count": len(metric.values),
            }

            if metric.metric_type == "counter":
                metric_summary["total"] = metric.get_sum()
                metric_summary["latest"] = metric.get_latest()

            elif metric.metric_type == "gauge":
                metric_summary["latest"] = metric.get_latest()
                metric_summary["min"] = metric.get_min()
                metric_summary["max"] = metric.get_max()
                metric_summary["avg"] = metric.get_average()

            elif metric.metric_type == "histogram":
                metric_summary["min"] = metric.get_min()
                metric_summary["max"] = metric.get_max()
                metric_summary["avg"] = metric.get_average()
                metric_summary["count"] = len(metric.values)

            summary[name] = metric_summary

        return summary

    def save_metrics(self, file_path: str) -> None:
        """Save metrics to a JSON file.

        Args:
            file_path: Path to save file
        """
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "agent_name": self.agent_name,
            "timestamp": datetime.now().isoformat(),
            "metrics": {
                name: metric.model_dump()
                for name, metric in self.metrics.items()
            },
            "summary": self.get_summary(),
        }

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)

    def clear(self) -> None:
        """Clear all metrics."""
        self.metrics.clear()
        self.timers.clear()
