import sys
import unittest
from pathlib import Path

SOURCE_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SOURCE_DIR))

from validation_state_machine import State, ValidationStateMachine  # noqa: E402


class HeartbeatTests(unittest.TestCase):
    def test_first_heartbeat_enters_auto(self) -> None:
        model = ValidationStateMachine()
        event = model.heartbeat(time_s=0.0, sequence=1)
        self.assertEqual(model.state, State.AUTO)
        self.assertEqual(event.reason, "FIRST_VALID_HEARTBEAT")

    def test_timeout_enters_safe(self) -> None:
        model = ValidationStateMachine(timeout_s=2.0)
        model.heartbeat(time_s=0.0, sequence=1)
        self.assertIsNone(model.check_timeout(time_s=1.99))
        event = model.check_timeout(time_s=2.0)
        self.assertIsNotNone(event)
        self.assertEqual(model.state, State.SAFE)

    def test_reset_is_rejected_until_link_recovers(self) -> None:
        model = ValidationStateMachine(timeout_s=2.0)
        model.heartbeat(time_s=0.0, sequence=1)
        model.check_timeout(time_s=2.0)
        event = model.manual_reset(time_s=2.1)
        self.assertEqual(event.reason, "LINK_NOT_RECOVERED")
        self.assertEqual(model.state, State.SAFE)

    def test_manual_recovery_policy_holds_safe_until_reset(self) -> None:
        model = ValidationStateMachine(timeout_s=2.0, require_manual_recovery=True)
        model.heartbeat(time_s=0.0, sequence=1)
        model.check_timeout(time_s=2.0)
        recovery = model.heartbeat(time_s=2.2, sequence=2)
        self.assertEqual(recovery.next_state, State.SAFE)
        model.manual_reset(time_s=2.3)
        self.assertEqual(model.state, State.AUTO)

    def test_automatic_recovery_can_be_selected(self) -> None:
        model = ValidationStateMachine(timeout_s=2.0, require_manual_recovery=False)
        model.heartbeat(time_s=0.0, sequence=1)
        model.check_timeout(time_s=2.0)
        model.heartbeat(time_s=2.2, sequence=2)
        self.assertEqual(model.state, State.AUTO)


class DriverEventTests(unittest.TestCase):
    def setUp(self) -> None:
        self.model = ValidationStateMachine()
        self.model.heartbeat(time_s=0.0, sequence=1)

    def test_first_event_enters_driver(self) -> None:
        event = self.model.driver_intervention(time_s=1.0, sequence=10)
        self.assertEqual(event.previous_state, State.AUTO)
        self.assertEqual(event.next_state, State.DRIVER)
        self.assertEqual(self.model.driver_event_count, 1)

    def test_repeated_event_does_not_change_state_again(self) -> None:
        self.model.driver_intervention(time_s=1.0, sequence=10)
        duplicate = self.model.driver_intervention(time_s=1.1, sequence=10)
        self.assertEqual(duplicate.previous_state, State.DRIVER)
        self.assertEqual(duplicate.next_state, State.DRIVER)
        self.assertEqual(self.model.driver_event_count, 1)
        self.assertEqual(self.model.duplicate_event_count, 1)


if __name__ == "__main__":
    unittest.main()
