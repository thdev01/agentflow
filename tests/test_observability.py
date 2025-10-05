"""Tests for observability systems."""

import tempfile
import time
from pathlib import Path

import pytest

from agentflow.observability import (
    AgentLogger,
    LogLevel,
    Tracer,
    MetricsCollector,
)


def test_logger_basic() -> None:
    """Test basic logging functionality."""
    logger = AgentLogger("test_agent", level=LogLevel.INFO)

    # Should not raise any exceptions
    logger.info("test_event", "Test message")
    logger.warning("warning_event", "Warning message", {"key": "value"})
    logger.error("error_event", "Error message")


def test_logger_levels() -> None:
    """Test log level filtering."""
    logger = AgentLogger("test_agent", level=LogLevel.WARNING)

    # INFO and DEBUG should not be logged (checked by no exceptions)
    logger.debug("debug", "Debug message")
    logger.info("info", "Info message")

    # WARNING, ERROR, CRITICAL should be logged
    logger.warning("warning", "Warning message")
    logger.error("error", "Error message")
    logger.critical("critical", "Critical message")


def test_logger_json_output() -> None:
    """Test JSON output format."""
    logger = AgentLogger("test_agent", level=LogLevel.INFO, output_json=True)

    # Should not raise exceptions with JSON output
    logger.info("event", "Message", {"data": 123})


def test_tracer_basic() -> None:
    """Test basic tracing functionality."""
    tracer = Tracer("test_agent", enabled=True)

    trace_id = tracer.start_trace("Test task", {"key": "value"})
    assert trace_id != ""

    event_id = tracer.add_event("test_event", {"data": "test"})
    assert event_id != ""

    tracer.end_trace()

    trace = tracer.get_trace(trace_id)
    assert trace is not None
    assert trace.task == "Test task"
    assert len(trace.events) > 0
    assert trace.duration_ms() is not None


def test_tracer_span() -> None:
    """Test tracer span functionality."""
    tracer = Tracer("test_agent", enabled=True)

    tracer.start_trace("Span test")

    with tracer.span("operation", {"op": "test"}):
        time.sleep(0.01)  # Small delay to measure

    tracer.end_trace()

    trace = tracer.get_trace(tracer.traces[0].trace_id)
    assert trace is not None
    assert len(trace.events) >= 2  # start and end events

    # Check that duration was recorded
    assert any(e.duration_ms is not None for e in trace.events)


def test_tracer_disabled() -> None:
    """Test that disabled tracer doesn't record."""
    tracer = Tracer("test_agent", enabled=False)

    trace_id = tracer.start_trace("Test")
    assert trace_id == ""

    event_id = tracer.add_event("event")
    assert event_id == ""


def test_tracer_persistence() -> None:
    """Test saving and loading traces."""
    tracer = Tracer("test_agent", enabled=True)

    with tempfile.TemporaryDirectory() as tmpdir:
        trace_id = tracer.start_trace("Persistent trace")
        tracer.add_event("event_1", {"data": 123})
        tracer.end_trace()

        # Save trace
        trace_file = Path(tmpdir) / "trace.json"
        tracer.save_trace(trace_id, str(trace_file))
        assert trace_file.exists()

        # Load trace
        loaded_trace = tracer.load_trace(str(trace_file))
        assert loaded_trace is not None
        assert loaded_trace.trace_id == trace_id
        assert loaded_trace.task == "Persistent trace"


def test_metrics_counter() -> None:
    """Test counter metrics."""
    metrics = MetricsCollector("test_agent", enabled=True)

    metrics.counter("requests", description="Request count")
    metrics.counter("requests")
    metrics.counter("requests")

    metric = metrics.get_metric("requests")
    assert metric is not None
    assert metric.metric_type == "counter"
    assert metric.get_latest() == 3.0


def test_metrics_gauge() -> None:
    """Test gauge metrics."""
    metrics = MetricsCollector("test_agent", enabled=True)

    metrics.gauge("queue_size", 10.0)
    metrics.gauge("queue_size", 15.0)
    metrics.gauge("queue_size", 8.0)

    metric = metrics.get_metric("queue_size")
    assert metric is not None
    assert metric.metric_type == "gauge"
    assert metric.get_latest() == 8.0
    assert metric.get_min() == 8.0
    assert metric.get_max() == 15.0


def test_metrics_histogram() -> None:
    """Test histogram metrics."""
    metrics = MetricsCollector("test_agent", enabled=True)

    metrics.histogram("latency", 100.0)
    metrics.histogram("latency", 150.0)
    metrics.histogram("latency", 200.0)

    metric = metrics.get_metric("latency")
    assert metric is not None
    assert metric.metric_type == "histogram"
    assert metric.get_min() == 100.0
    assert metric.get_max() == 200.0
    assert metric.get_average() == 150.0


def test_metrics_timer() -> None:
    """Test timer functionality."""
    metrics = MetricsCollector("test_agent", enabled=True)

    metrics.start_timer("operation")
    time.sleep(0.01)
    duration = metrics.stop_timer("operation")

    assert duration is not None
    assert duration > 0

    # Check that histogram was created
    metric = metrics.get_metric("operation.duration_ms")
    assert metric is not None
    assert metric.metric_type == "histogram"


def test_metrics_summary() -> None:
    """Test metrics summary."""
    metrics = MetricsCollector("test_agent", enabled=True)

    metrics.counter("count", 5)
    metrics.gauge("gauge", 10.0)
    metrics.histogram("hist", 100.0)

    summary = metrics.get_summary()
    assert "test_agent.count" in summary or "count" in summary
    assert "test_agent.gauge" in summary or "gauge" in summary
    assert "test_agent.hist" in summary or "hist" in summary


def test_metrics_persistence() -> None:
    """Test saving metrics to file."""
    metrics = MetricsCollector("test_agent", enabled=True)

    metrics.counter("requests")
    metrics.gauge("queue", 10.0)

    with tempfile.TemporaryDirectory() as tmpdir:
        metrics_file = Path(tmpdir) / "metrics.json"
        metrics.save_metrics(str(metrics_file))
        assert metrics_file.exists()

        # File should contain JSON data
        content = metrics_file.read_text()
        assert "test_agent" in content
        assert "requests" in content


def test_metrics_disabled() -> None:
    """Test that disabled metrics don't record."""
    metrics = MetricsCollector("test_agent", enabled=False)

    metrics.counter("test")
    metrics.gauge("test", 10.0)
    metrics.histogram("test", 100.0)

    assert len(metrics.get_all_metrics()) == 0


def test_metrics_clear() -> None:
    """Test clearing metrics."""
    metrics = MetricsCollector("test_agent", enabled=True)

    metrics.counter("test")
    metrics.gauge("test2", 10.0)
    assert len(metrics.get_all_metrics()) > 0

    metrics.clear()
    assert len(metrics.get_all_metrics()) == 0
