"""Example: Using observability features.

This example demonstrates the observability tools:
- AgentLogger: Structured logging with different levels
- Tracer: Execution tracing and span tracking
- MetricsCollector: Performance metrics collection
"""

import time

from agentflow.observability import (
    AgentLogger,
    LogLevel,
    Tracer,
    MetricsCollector,
)


def demo_logger() -> None:
    """Demonstrate structured logging."""
    print("\n" + "=" * 60)
    print("Structured Logging Demo")
    print("=" * 60)

    # Create logger with different output formats
    logger = AgentLogger("demo_agent", level=LogLevel.DEBUG)

    logger.info("agent_start", "Agent starting up", {"version": "1.0.0"})
    logger.debug("config_load", "Loading configuration", {"config_file": "config.json"})
    logger.warning("deprecated_api", "Using deprecated API", {"api": "old_endpoint"})
    logger.error("connection_failed", "Failed to connect to service", {"service": "api.example.com", "retry": 1})

    print("\nJSON output format:")
    json_logger = AgentLogger("demo_agent", level=LogLevel.INFO, output_json=True)
    json_logger.info("task_complete", "Task completed successfully", {"duration_ms": 1234})


def demo_tracer() -> None:
    """Demonstrate execution tracing."""
    print("\n" + "=" * 60)
    print("Execution Tracing Demo")
    print("=" * 60)

    tracer = Tracer("demo_agent", enabled=True)

    # Start a trace
    trace_id = tracer.start_trace("Process customer order", {"customer_id": "12345"})
    print(f"\nStarted trace: {trace_id}")

    # Add events
    tracer.add_event("order_received", {"order_id": "ORD-001", "items": 3})

    # Use span for timed operations
    with tracer.span("validate_order", {"order_id": "ORD-001"}):
        time.sleep(0.1)  # Simulate work
        tracer.add_event("validation_check", {"status": "passed"})

    with tracer.span("process_payment", {"amount": 99.99}):
        time.sleep(0.2)  # Simulate work
        tracer.add_event("payment_processed", {"transaction_id": "TXN-123"})

    with tracer.span("ship_order", {"warehouse": "US-WEST"}):
        time.sleep(0.15)  # Simulate work
        tracer.add_event("shipment_created", {"tracking": "TRACK-789"})

    # End trace
    tracer.end_trace()

    # Get trace details
    trace = tracer.get_trace(trace_id)
    if trace:
        print(f"\nTrace completed in {trace.duration_ms():.2f}ms")
        print(f"Total events: {len(trace.events)}")

        # Show events
        print("\nTrace events:")
        for event in trace.events:
            print(f"  - {event.event_type}: {event.data}")
            if event.duration_ms:
                print(f"    Duration: {event.duration_ms:.2f}ms")

    # Save trace to file
    tracer.save_trace(trace_id, f"./traces/trace_{trace_id}.json")
    print(f"\nTrace saved to: ./traces/trace_{trace_id}.json")


def demo_metrics() -> None:
    """Demonstrate metrics collection."""
    print("\n" + "=" * 60)
    print("Metrics Collection Demo")
    print("=" * 60)

    metrics = MetricsCollector("demo_agent", enabled=True)

    # Counter metrics
    print("\n📊 Recording counter metrics...")
    metrics.counter("requests.total", description="Total requests processed")
    metrics.counter("requests.total")
    metrics.counter("requests.total")
    metrics.counter("errors.total", description="Total errors")

    # Gauge metrics
    print("📈 Recording gauge metrics...")
    metrics.gauge("queue.size", 10.0, description="Current queue size")
    metrics.gauge("queue.size", 15.0)
    metrics.gauge("queue.size", 8.0)

    metrics.gauge("memory.usage_mb", 256.5, description="Memory usage in MB")
    metrics.gauge("memory.usage_mb", 312.7)

    # Histogram metrics (for durations, sizes, etc.)
    print("📏 Recording histogram metrics...")
    metrics.histogram("response.time_ms", 123.45, description="Response time in ms")
    metrics.histogram("response.time_ms", 98.32)
    metrics.histogram("response.time_ms", 156.78)
    metrics.histogram("response.time_ms", 87.91)

    # Timer usage
    print("⏱️  Using timers...")
    metrics.start_timer("operation")
    time.sleep(0.1)
    duration = metrics.stop_timer("operation")
    print(f"Operation took: {duration:.2f}ms")

    # Get metrics summary
    print("\n📋 Metrics Summary:")
    summary = metrics.get_summary()
    for name, data in summary.items():
        print(f"\n  {name}:")
        for key, value in data.items():
            print(f"    {key}: {value}")

    # Save metrics
    metrics.save_metrics("./metrics/demo_metrics.json")
    print("\n💾 Metrics saved to: ./metrics/demo_metrics.json")


def demo_combined() -> None:
    """Demonstrate using all observability tools together."""
    print("\n" + "=" * 60)
    print("Combined Observability Demo")
    print("=" * 60)

    logger = AgentLogger("combined_agent", level=LogLevel.INFO)
    tracer = Tracer("combined_agent", enabled=True)
    metrics = MetricsCollector("combined_agent", enabled=True)

    # Start trace
    trace_id = tracer.start_trace("Complex task execution")
    logger.info("task_start", "Starting complex task", {"trace_id": trace_id})

    # Do work with observability
    with tracer.span("phase_1", {"description": "Data processing"}):
        logger.debug("processing", "Processing data")
        metrics.counter("items.processed")
        metrics.start_timer("processing")
        time.sleep(0.1)
        duration = metrics.stop_timer("processing")
        logger.info("phase_complete", f"Phase 1 completed in {duration:.2f}ms")

    with tracer.span("phase_2", {"description": "Validation"}):
        logger.debug("validation", "Validating results")
        metrics.counter("validation.checks", 5)
        time.sleep(0.05)
        logger.info("validation_complete", "All checks passed")

    # End trace
    tracer.end_trace()
    trace = tracer.get_trace(trace_id)

    logger.info(
        "task_complete",
        "Task completed successfully",
        {
            "trace_id": trace_id,
            "duration_ms": trace.duration_ms() if trace else 0,
            "total_items": 1,
        },
    )

    print(f"\n✅ Task traced, logged, and metrics collected!")
    print(f"   Trace duration: {trace.duration_ms():.2f}ms")
    print(f"   Events logged: {len(trace.events)}")
    print(f"   Metrics collected: {len(metrics.get_all_metrics())}")


def main() -> None:
    """Run all observability demos."""
    print("\n🔍 AgentFlow Observability Demos\n")

    demo_logger()
    demo_tracer()
    demo_metrics()
    demo_combined()

    print("\n" + "=" * 60)
    print("All demos completed!")
    print("Check the ./traces and ./metrics directories for output files.")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
