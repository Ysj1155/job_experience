"""Platform-independent state model reconstructed from a board validation exercise."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any


class State(str, Enum):
    INIT = "INIT"
    AUTO = "AUTO"
    SAFE = "SAFE"
    DRIVER = "DRIVER"


@dataclass(frozen=True)
class Event:
    time_s: float
    name: str
    previous_state: State
    next_state: State
    reason: str
    sequence: int | None = None
    functional_result: str = ""
    physical_scope: str = "NOT_OBSERVED"

    def to_dict(self) -> dict[str, Any]:
        row = asdict(self)
        row["previous_state"] = self.previous_state.value
        row["next_state"] = self.next_state.value
        return row


class ValidationStateMachine:
    """State model used to make validation conditions explicit and testable.

    Manual recovery is a policy selected for this public reconstruction. It is
    not presented as a product requirement.
    """

    def __init__(self, timeout_s: float = 2.0, require_manual_recovery: bool = True) -> None:
        if timeout_s <= 0:
            raise ValueError("timeout_s must be positive")
        self.timeout_s = timeout_s
        self.require_manual_recovery = require_manual_recovery
        self.state = State.INIT
        self.link_alive = False
        self.last_heartbeat_s: float | None = None
        self.last_heartbeat_sequence: int | None = None
        self.driver_event_count = 0
        self.duplicate_event_count = 0
        self.events: list[Event] = []

    def _record(
        self,
        time_s: float,
        name: str,
        previous: State,
        reason: str,
        sequence: int | None = None,
        functional_result: str = "",
    ) -> Event:
        event = Event(
            time_s=time_s,
            name=name,
            previous_state=previous,
            next_state=self.state,
            reason=reason,
            sequence=sequence,
            functional_result=functional_result,
        )
        self.events.append(event)
        return event

    def heartbeat(self, time_s: float, sequence: int) -> Event:
        if sequence < 0:
            raise ValueError("sequence must be non-negative")

        previous = self.state
        was_alive = self.link_alive
        self.link_alive = True
        self.last_heartbeat_s = time_s
        self.last_heartbeat_sequence = sequence

        if self.state is State.INIT:
            self.state = State.AUTO
            return self._record(
                time_s,
                "HEARTBEAT",
                previous,
                "FIRST_VALID_HEARTBEAT",
                sequence,
                "PASS",
            )

        if self.state is State.SAFE and not was_alive:
            if self.require_manual_recovery:
                return self._record(
                    time_s,
                    "LINK_RECOVERED",
                    previous,
                    "MANUAL_RESET_REQUIRED_BY_TEST_POLICY",
                    sequence,
                    "PASS",
                )
            self.state = State.AUTO
            return self._record(
                time_s,
                "LINK_RECOVERED",
                previous,
                "AUTOMATIC_RECOVERY_POLICY",
                sequence,
                "PASS",
            )

        return self._record(time_s, "HEARTBEAT", previous, "LINK_HEALTHY", sequence)

    def check_timeout(self, time_s: float) -> Event | None:
        if not self.link_alive or self.last_heartbeat_s is None:
            return None
        elapsed_s = time_s - self.last_heartbeat_s
        if elapsed_s < self.timeout_s:
            return None

        previous = self.state
        self.link_alive = False
        if self.state is State.AUTO:
            self.state = State.SAFE
            return self._record(
                time_s,
                "HEARTBEAT_TIMEOUT",
                previous,
                "TIMEOUT_THRESHOLD_REACHED",
                self.last_heartbeat_sequence,
                "PASS",
            )

        return self._record(
            time_s,
            "HEARTBEAT_TIMEOUT",
            previous,
            "STATE_HELD_BY_TEST_POLICY",
            self.last_heartbeat_sequence,
        )

    def manual_reset(self, time_s: float) -> Event:
        previous = self.state
        if self.state is not State.SAFE:
            return self._record(time_s, "RESET_REJECTED", previous, "STATE_NOT_SAFE")
        if not self.link_alive:
            return self._record(
                time_s,
                "RESET_REJECTED",
                previous,
                "LINK_NOT_RECOVERED",
                functional_result="PASS",
            )

        self.state = State.AUTO
        return self._record(
            time_s,
            "MANUAL_RESET",
            previous,
            "LINK_HEALTHY",
            functional_result="PASS",
        )

    def driver_intervention(self, time_s: float, sequence: int | None = None) -> Event:
        previous = self.state
        if self.state is State.DRIVER:
            self.duplicate_event_count += 1
            return self._record(
                time_s,
                "DRIVER_EVENT_DUPLICATE",
                previous,
                "NO_ADDITIONAL_STATE_CHANGE",
                sequence,
                "PASS",
            )

        if self.state is not State.AUTO:
            return self._record(
                time_s,
                "DRIVER_EVENT_IGNORED",
                previous,
                "EVENT_NOT_VALID_IN_CURRENT_STATE",
                sequence,
            )

        self.driver_event_count += 1
        self.state = State.DRIVER
        return self._record(
            time_s,
            "DRIVER_INTERVENTION",
            previous,
            "FIRST_DRIVER_EVENT",
            sequence,
            "PASS",
        )
