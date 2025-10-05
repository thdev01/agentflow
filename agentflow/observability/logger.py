"""Structured logging for agents."""

import json
import logging
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel


class LogLevel(str, Enum):
    """Log levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogEntry(BaseModel):
    """Structured log entry."""

    timestamp: datetime
    level: LogLevel
    agent_name: str
    event_type: str
    message: str
    data: Dict[str, Any] = {}
    trace_id: Optional[str] = None


class AgentLogger:
    """Structured logger for agents."""

    def __init__(
        self,
        agent_name: str,
        level: LogLevel = LogLevel.INFO,
        output_json: bool = False,
    ) -> None:
        """Initialize agent logger.

        Args:
            agent_name: Name of the agent
            level: Minimum log level
            output_json: Whether to output JSON format
        """
        self.agent_name = agent_name
        self.level = level
        self.output_json = output_json
        self.logger = logging.getLogger(f"agentflow.{agent_name}")
        self.logger.setLevel(getattr(logging, level.value))

        # Add console handler if not already added
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            if output_json:
                handler.setFormatter(
                    logging.Formatter("%(message)s")
                )
            else:
                handler.setFormatter(
                    logging.Formatter(
                        "[%(levelname)s] [%(name)s] %(message)s"
                    )
                )
            self.logger.addHandler(handler)

    def _should_log(self, level: LogLevel) -> bool:
        """Check if message should be logged."""
        level_order = {
            LogLevel.DEBUG: 0,
            LogLevel.INFO: 1,
            LogLevel.WARNING: 2,
            LogLevel.ERROR: 3,
            LogLevel.CRITICAL: 4,
        }
        return level_order[level] >= level_order[self.level]

    def _log(
        self,
        level: LogLevel,
        event_type: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        trace_id: Optional[str] = None,
    ) -> None:
        """Internal log method."""
        if not self._should_log(level):
            return

        entry = LogEntry(
            timestamp=datetime.now(),
            level=level,
            agent_name=self.agent_name,
            event_type=event_type,
            message=message,
            data=data or {},
            trace_id=trace_id,
        )

        if self.output_json:
            log_message = entry.model_dump_json()
        else:
            log_message = f"[{event_type}] {message}"
            if data:
                log_message += f" | {data}"

        log_fn = getattr(self.logger, level.value.lower())
        log_fn(log_message)

    def debug(
        self,
        event_type: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        trace_id: Optional[str] = None,
    ) -> None:
        """Log debug message."""
        self._log(LogLevel.DEBUG, event_type, message, data, trace_id)

    def info(
        self,
        event_type: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        trace_id: Optional[str] = None,
    ) -> None:
        """Log info message."""
        self._log(LogLevel.INFO, event_type, message, data, trace_id)

    def warning(
        self,
        event_type: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        trace_id: Optional[str] = None,
    ) -> None:
        """Log warning message."""
        self._log(LogLevel.WARNING, event_type, message, data, trace_id)

    def error(
        self,
        event_type: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        trace_id: Optional[str] = None,
    ) -> None:
        """Log error message."""
        self._log(LogLevel.ERROR, event_type, message, data, trace_id)

    def critical(
        self,
        event_type: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        trace_id: Optional[str] = None,
    ) -> None:
        """Log critical message."""
        self._log(LogLevel.CRITICAL, event_type, message, data, trace_id)
