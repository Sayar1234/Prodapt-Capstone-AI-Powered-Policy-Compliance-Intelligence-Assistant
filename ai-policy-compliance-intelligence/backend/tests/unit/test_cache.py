import unittest

from app.database.redis import LocalCache


class LocalCacheTests(unittest.IsolatedAsyncioTestCase):
    async def test_get_set_and_ping(self) -> None:
        cache = LocalCache()
        await cache.set("answer", {"risk": "low"}, ttl=1)
        self.assertEqual(await cache.get("answer"), {"risk": "low"})
        self.assertTrue(await cache.ping())


if __name__ == "__main__":
    unittest.main()
