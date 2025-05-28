import unittest
import json
import jwt
import datetime

from src.fit.app import create_app
from src.fit.database import init_db, db_session
from src.fit.models_db import Base, UserModel

class TestUserAPI(unittest.TestCase):
    def setUp(self):
        # Create app and test client
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

        # Initialize DB schema
        init_db()
        self.db = db_session()
        Base.metadata.create_all(bind=self.db.get_bind())

        # Create admin JWT token
        token_data = {
            "sub": "admin@test.com",
            "name": "Test Admin",
            "role": "admin",
            "iss": "fit-api",
            "iat": datetime.datetime.now(datetime.timezone.utc),
            "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=30)
        }
        self.admin_token = jwt.encode(token_data, "fit-secret-key", algorithm="HS256")

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(bind=self.db.get_bind())

    def test_create_user_success(self):
        test_user = {
            "email": "test@example.com",
            "password": "securepass123",
            "name": "Test User",
            "role": "user"
        }

        response = self.client.post(
            "/users",
            data=json.dumps(test_user),
            content_type="application/json",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )

        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data["email"], test_user["email"])
        self.assertEqual(data["name"], test_user["name"])
        self.assertEqual(data["role"], test_user["role"])

    def test_create_user_invalid_data(self):
        invalid_user = {
            "email": "invalid_email",  # malformed
            "name": "Test User",
            "role": "user"
        }
    

        response = self.client.post(
            "/users",
            data=json.dumps(invalid_user),
            content_type="application/json",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )

        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("error", data)

if __name__ == "__main__":
    unittest.main()
