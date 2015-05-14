#coding:utf-8
import os
import unittest

import app


EVENT_ID = "58678c12-df3b-445b-95bc-41974d696019"
ALT_EVENT_ID = "alternative ID here"


class AppTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.make_app()
        self.client = self.app.test_client()

        self.app.config.update(validation_token=None,)

        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_data", "webhook.json")) as f:
            self.webhook_payload = f.read()
            self.alt_paylod = f.read()


    def test_rendering(self):
        # Check there are no records
        r = self.client.get("/")
        self.assertEqual(r.status_code, 200)
        txt = r.data.decode('utf-8')
        self.assertNotIn(EVENT_ID, txt)
        self.assertIn("No requests", txt)

        # Add a record
        r = self.client.post("/", content_type="application/json", data=self.webhook_payload)
        self.assertEqual(r.status_code, 202)

        # Check it's there
        r = self.client.get("/")
        self.assertEqual(r.status_code, 200)
        txt = r.data.decode('utf-8')
        self.assertIn(EVENT_ID, txt)
        self.assertNotIn("No requests", txt)

        # Add another record
        r = self.client.post("/", content_type="application/json", data=self.webhook_payload.replace(EVENT_ID, ALT_EVENT_ID))
        self.assertEqual(r.status_code, 202)

        # Check we now have two records
        r = self.client.get("/")
        self.assertEqual(r.status_code, 200)
        txt = r.data.decode('utf-8')
        self.assertIn(EVENT_ID, txt)
        self.assertIn(ALT_EVENT_ID, txt)
        self.assertNotIn("No requests", txt)

        # Test redaction
        self.assertIn("TEST_SECRET_VARIABLE", txt)
        self.assertNotIn("SECRET VALUE", txt)
        self.assertIn("******", txt)


if __name__ == '__main__':
    unittest.main()
