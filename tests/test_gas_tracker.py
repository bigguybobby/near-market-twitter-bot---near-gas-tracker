import unittest

from near_gas_tracker import GasSnapshot, classify_gas, compose_tweet, fetch_gas_snapshot, gas_price_to_near_per_tgas


def fake_post_json(url, payload):
    assert payload["method"] == "gas_price"
    return {"result": {"gas_price": "100000000", "block_height": 123}}


class GasTrackerTests(unittest.TestCase):
    def test_conversion(self):
        self.assertEqual(gas_price_to_near_per_tgas(100_000_000), 0.0001)

    def test_fetch_snapshot(self):
        snap = fetch_gas_snapshot(post_json=fake_post_json)
        self.assertEqual(snap.gas_price, 100_000_000)
        self.assertEqual(snap.block_height, 123)

    def test_tweet_length_and_content(self):
        tweet = compose_tweet(GasSnapshot(100_000_000, 0.0001, 123, "now"))
        self.assertLessEqual(len(tweet), 280)
        self.assertIn("NEAR gas", tweet)
        self.assertIn("0.000100", tweet)

    def test_classification(self):
        self.assertEqual(classify_gas(50_000_000), "cheap")
        self.assertEqual(classify_gas(100_000_000), "normal")
        self.assertEqual(classify_gas(250_000_000), "busy")
        self.assertEqual(classify_gas(400_000_000), "congested")


if __name__ == "__main__":
    unittest.main()
