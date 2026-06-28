import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from spatial_governance import (
    OperationalEnvelope,
    classify_spatial_event,
    create_spatial_event,
    validate_spatial_receipt,
    write_spatial_receipt,
)


class SpatialGovernanceTests(unittest.TestCase):
    def envelope(self, **overrides):
        data = {
            "envelope_id": "search-zone-alpha",
            "authority_id": "mission-authority-1",
            "center_x": 0.0,
            "center_y": 0.0,
            "radius_m": 100.0,
            "min_altitude_m": 5.0,
            "max_altitude_m": 80.0,
            "max_speed_mps": 8.0,
            "min_human_distance_m": 12.0,
            "receipt_required": True,
            "authority_transfer_allowed": False,
        }
        data.update(overrides)
        return OperationalEnvelope(**data)

    def event(self, **overrides):
        data = {
            "agent_id": "spatial-adapter",
            "operator_id": "operator",
            "vehicle_id": "hummingbird-demo-1",
            "mission_id": "mission-1",
            "envelope_id": "search-zone-alpha",
            "authority_id": "mission-authority-1",
            "position": {"x": 10.0, "y": 5.0, "altitude_m": 20.0},
            "velocity_mps": 3.0,
            "nearest_human_distance_m": 25.0,
            "zone_authorized": True,
            "sensor_confidence": 0.86,
            "rho": 0.82,
            "delta": 0.14,
        }
        data.update(overrides)
        return create_spatial_event(**data)

    def write(self, event=None, envelope=None):
        with tempfile.TemporaryDirectory() as temp:
            resolved_envelope = self.envelope() if envelope == "default" or envelope is None else envelope
            receipt = write_spatial_receipt(Path(temp) / "spatial.jsonl", event or self.event(), resolved_envelope)
            self.assertFalse(validate_spatial_receipt(receipt))
            return receipt

    def test_authorized_envelope_proceeds(self):
        receipt = self.write()
        self.assertEqual(receipt["decision"], "PROCEED")
        self.assertFalse(receipt["operator_review_required"])
        self.assertIn("does not navigate", receipt["boundary"])

    def test_missing_envelope_pauses(self):
        receipt = self.write(envelope=None)
        self.assertEqual(receipt["decision"], "PROCEED")
        with tempfile.TemporaryDirectory() as temp:
            receipt = write_spatial_receipt(Path(temp) / "spatial.jsonl", self.event(), None)
        self.assertEqual(receipt["decision"], "PAUSE")
        self.assertIn("missing operational envelope", receipt["decision_reason"])

    def test_zone_authorization_missing_pauses(self):
        receipt = self.write(self.event(zone_authorized=False))
        self.assertEqual(receipt["decision"], "PAUSE")
        self.assertIn("zone authorization missing", receipt["decision_reason"])

    def test_outside_envelope_pauses(self):
        receipt = self.write(self.event(position={"x": 130.0, "y": 0.0, "altitude_m": 20.0}))
        self.assertEqual(receipt["decision"], "PAUSE")
        self.assertIn("outside operational envelope", receipt["decision_reason"])

    def test_proximity_breach_pauses(self):
        receipt = self.write(self.event(nearest_human_distance_m=5.0))
        self.assertEqual(receipt["decision"], "PAUSE")
        self.assertIn("proximity breach", receipt["decision_reason"])

    def test_authority_transfer_without_receipt_pauses(self):
        receipt = self.write(self.event(authority_transfer_requested=True))
        self.assertEqual(receipt["decision"], "PAUSE")
        self.assertIn("authority transfer requires receipt", receipt["decision_reason"])

    def test_actuator_request_aborts(self):
        receipt = self.write(self.event(actuator_command_requested=True))
        self.assertEqual(receipt["decision"], "ABORT")
        self.assertIn("adapter cannot issue physical action", receipt["decision_reason"])

    def test_broken_chain_safe_mode(self):
        receipt = self.write(self.event(receipt_chain_valid=False))
        self.assertEqual(receipt["decision"], "SAFE_MODE")
        self.assertIn("receipt chain broken", receipt["decision_reason"])

    def test_schema_file_is_parseable(self):
        schema = json.loads((ROOT / "schemas" / "spatial_governance.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(schema["title"], "Echo Root VE Spatial Governance Gate Receipt")
        self.assertIn("calibration_reason", schema["required"])

    def test_classification_reports_path_envelope_difference(self):
        classification = classify_spatial_event(self.event(position={"x": 60.0, "y": 80.0, "altitude_m": 20.0}), self.envelope())
        self.assertEqual(classification["distance_from_center_m"], 100.0)
        self.assertTrue(classification["inside_envelope"])


if __name__ == "__main__":
    unittest.main()
