import unittest
from rest_framework.test import APIClient
from rest_framework import status
from .src.backend.AFM_API.views import WaterLevelView
from .src.backend.AFM_API.models import WaterLevel
from .src.backend.AFM_API.serializers import WaterLevelSerializer

class TestWaterLevelView(unittest.TestCase):
    def setUp(self):
        self.client = APIClient()
        self.valid_data = {
            "location_id": 1,
            "value_at_time": 10.5,
            "unit": "cm",
            "created_at": "2023-11-13T12:00:00Z"
        }

        self.invalid_data = {
            "location_id": None,
            "value_at_time": -5,
            "unit": "invalid",
            "created_at": "2023-13-11T12:00:00Z"
        }

    def test_post_valid_data(self):
        response = self.client.post('/path/to/waterlevel/', self.valid_data, format='json') # Checking if the response status code is 201 created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED) # WaterLevel object is created?
        self.assertEqual(WaterLevel.objects.count(), 1) # expected field value
        self.assertEqual(WaterLevel.objects.get().location_id, self.valid_data['location_id'])

    def test_post_invalid_data(self):
        response = self.client.post('/path/to/waterlevel/', self.invalid_data, format='json')# to check if the response status code is 400 baaaad request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST) # Checking if no waterLevel object is created
        self.assertEqual(WaterLevel.objects.count(), 0)







if __name__ == '__main__':
    unittest.main()