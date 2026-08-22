import unittest

from infra.azure.quota_guard import environment_decision, regional_decision


class RegionalQuotaDecisionTests(unittest.TestCase):
    def test_existing_environment_does_not_require_new_regional_slot(self) -> None:
        document = {"value": [{"name": {"value": "ManagedEnvironmentCount"}, "currentValue": 1, "limit": 1}]}
        decision = regional_decision(document, resource_name="ManagedEnvironmentCount", environment_exists=True, minimum_limit=1, request_increment=1)
        self.assertEqual(decision["action"], "ok")
        self.assertIsNone(decision["requestedLimit"])

    def test_free_regional_slot_is_accepted(self) -> None:
        document = {"value": [{"name": {"value": "ManagedEnvironmentCount"}, "currentValue": 1, "limit": 2}]}
        decision = regional_decision(document, resource_name="ManagedEnvironmentCount", environment_exists=False, minimum_limit=1, request_increment=1)
        self.assertEqual(decision["action"], "ok")
        self.assertEqual(decision["available"], 1)

    def test_full_regional_quota_requests_one_more_slot(self) -> None:
        document = {"value": [{"name": {"localizedValue": "ManagedEnvironmentCount"}, "currentValue": 2, "limit": 2}]}
        decision = regional_decision(document, resource_name="ManagedEnvironmentCount", environment_exists=False, minimum_limit=1, request_increment=1)
        self.assertEqual(decision["action"], "request")
        self.assertEqual(decision["requestedLimit"], 3)


class EnvironmentQuotaDecisionTests(unittest.TestCase):
    def test_environment_core_capacity_is_accepted(self) -> None:
        document = {"value": [{"name": {"value": "ManagedEnvironmentConsumptionCores"}, "currentValue": 0.5, "limit": 10}]}
        decision = environment_decision(document, resource_name="ManagedEnvironmentConsumptionCores", required_available=1.5)
        self.assertEqual(decision["action"], "ok")
        self.assertEqual(decision["available"], 9.5)

    def test_environment_core_shortage_requires_manual_request(self) -> None:
        document = {"value": [{"name": {"value": "ManagedEnvironmentConsumptionCores"}, "currentValue": 0.5, "limit": 1}]}
        decision = environment_decision(document, resource_name="ManagedEnvironmentConsumptionCores", required_available=1.5)
        self.assertEqual(decision["action"], "manual_request")
        self.assertEqual(decision["available"], 0.5)


if __name__ == "__main__":
    unittest.main()
