# Standard Library
import io
import os
import uuid

# Django
from django.conf import settings
from django.urls import reverse

# Third Parties
import numpy as np
from PIL import Image
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_api_key.models import APIKey

# Face Embeddings
from face_images.models import FaceImage


class FaceImageCreateViewTests(APITestCase):
    @classmethod
    def generate_image(cls):
        new_file = io.BytesIO()
        image = Image.new("RGBA", size=(100, 100), color="red")
        image.save(new_file, "png")
        new_file.name = "test.png"
        new_file.seek(0)
        return new_file

    @classmethod
    def setUpTestData(cls):
        cls.api_key_obj, cls.key = APIKey.objects.create_key(name="test_key")
        cls.url = reverse("encode-face-image")
        cls.face_image = cls.generate_image()
        cls.request_data = {
            "face_image": cls.face_image,
        }

    @classmethod
    def delete_image_file(cls):
        media_path = settings.MEDIA_ROOT
        for filename in os.listdir(media_path):
            if filename.startswith("test"):
                file_path = os.path.join(media_path, filename)
                os.remove(file_path)

    @classmethod
    def tearDownClass(cls):
        FaceImage.objects.all().delete()
        APIKey.objects.all().delete()
        cls.delete_image_file()

    def test_unauthenticated_encode_face_image(self):
        message = "Authentication credentials were not provided."
        response = self.client.post(data=self.request_data, path=self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn(message, str(response.data))

    def test_success_encode_face_image(self):
        response = self.client.post(data=self.request_data, path=self.url, HTTP_AUTHORIZATION=f"Api-Key {self.key}")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(FaceImage.objects.count(), 1)
        self.assertIn("public_id", response.data)
        self.assertIn("face_encoding", response.data)
        self.assertIn("encoding_status", response.data)
        self.assertIn("created_at", response.data)
        self.assertIn("updated_at", response.data)

    def test_encode_face_image_with_empty_body(self):
        message = "No file was submitted."
        response = self.client.post(data=dict(), path=self.url, HTTP_AUTHORIZATION=f"Api-Key {self.key}")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(message, str(response.data))


class FaceImageDetailViewTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.api_key_obj, cls.key = APIKey.objects.create_key(name="test_key")
        cls.face_record = FaceImage.objects.create(image_url=os.path.join(settings.MEDIA_ROOT, "test.png"))
        cls.url = reverse("retrieve-encode-face-image", args=[cls.face_record.public_id])

    @classmethod
    def tearDownClass(cls):
        FaceImage.objects.all().delete()
        APIKey.objects.all().delete()

    def test_unauthenticated_retrieve_encode_face_image(self):
        message = "Authentication credentials were not provided."
        response = self.client.get(path=self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn(message, str(response.data))

    def test_success_retrieve_encode_face_image(self):
        response = self.client.get(path=self.url, HTTP_AUTHORIZATION=f"Api-Key {self.key}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("face_encoding", response.data)
        self.assertIn("encoding_status", response.data)
        self.assertIn("created_at", response.data)
        self.assertIn("updated_at", response.data)

    def test_get_face_image_details_not_found(self):
        message = "No FaceImage matches the given query."
        url = reverse("retrieve-encode-face-image", args=[str(uuid.uuid4())])
        response = self.client.get(url, HTTP_AUTHORIZATION=f"Api-Key {self.key}")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn(message, str(response.data))


class FaceImageStatsViewTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.api_key_obj, cls.key = APIKey.objects.create_key(name="test_key")
        FaceImage.objects.create(image_url=os.path.join(settings.MEDIA_ROOT, "test1.png"), encoding_status="SUCCESS")
        FaceImage.objects.create(image_url=os.path.join(settings.MEDIA_ROOT, "test2.png"), encoding_status="PENDING")
        FaceImage.objects.create(image_url=os.path.join(settings.MEDIA_ROOT, "test3.png"), encoding_status="SUCCESS")
        FaceImage.objects.create(image_url=os.path.join(settings.MEDIA_ROOT, "test4.png"), encoding_status="SUCCESS")
        FaceImage.objects.create(image_url=os.path.join(settings.MEDIA_ROOT, "test5.png"), encoding_status="FAILED")
        FaceImage.objects.create(image_url=os.path.join(settings.MEDIA_ROOT, "test6.png"), encoding_status="PENDING")
        cls.url = reverse("retrieve-stats-face-image")

    @classmethod
    def tearDownClass(cls):
        FaceImage.objects.all().delete()
        APIKey.objects.all().delete()

    def test_unauthenticated_retrieve_stats_face_image(self):
        message = "Authentication credentials were not provided."
        response = self.client.get(path=self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn(message, str(response.data))

    def test_success_retrieve_stats_face_image(self):
        response = self.client.get(path=self.url, HTTP_AUTHORIZATION=f"Api-Key {self.key}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("encoding_status", response.data[0])
        self.assertIn("count", response.data[0])
        self.assertEqual(len(response.data), 3)

        status_counts = {entry["encoding_status"]: entry["count"] for entry in response.data}
        self.assertEqual(status_counts.get("SUCCESS"), 3)
        self.assertEqual(status_counts.get("PENDING"), 2)
        self.assertEqual(status_counts.get("FAILED"), 1)


class FaceImageEncodingAverageViewTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.api_key_obj, cls.key = APIKey.objects.create_key(name="test_key")
        cls.url = reverse("retrieve-avg-face-encodings")

        cls.face_encoding1 = np.array([0.5, -0.3, 0.7, 0.2, -0.1])
        cls.face_encoding2 = np.array([0.8, 0.1, -0.5, 0.4, 0.9])
        cls.face_encoding3 = np.array([-0.2, 0.6, 0.3, -0.4, 0.5])
        cls.face_encoding4 = np.array([0.1, 0.6, -0.1, 0.2, 0.7])
        cls.face_encoding5 = np.array([-0.5, 0.2, 0.3, -0.4, 0.5])
        cls.face_encoding6 = np.array([0.5, -0.3, 0.7, 0.2, -0.1])

        cls.face_image1 = FaceImage.objects.create(
            image_url=os.path.join(settings.MEDIA_ROOT, "test1.png"),
            face_encoding=cls.face_encoding1.tobytes(),
            encoding_status="SUCCESS",
        )
        cls.face_image2 = FaceImage.objects.create(
            image_url=os.path.join(settings.MEDIA_ROOT, "test2.png"),
            face_encoding=cls.face_encoding2.tobytes(),
            encoding_status="PENDING",
        )
        cls.face_image3 = FaceImage.objects.create(
            image_url=os.path.join(settings.MEDIA_ROOT, "test3.png"),
            face_encoding=cls.face_encoding3.tobytes(),
            encoding_status="SUCCESS",
        )
        cls.face_image4 = FaceImage.objects.create(
            image_url=os.path.join(settings.MEDIA_ROOT, "test4.png"),
            face_encoding=cls.face_encoding4.tobytes(),
            encoding_status="SUCCESS",
        )
        cls.face_image5 = FaceImage.objects.create(
            image_url=os.path.join(settings.MEDIA_ROOT, "test5.png"),
            face_encoding=cls.face_encoding5.tobytes(),
            encoding_status="FAILED",
        )
        cls.face_image6 = FaceImage.objects.create(
            image_url=os.path.join(settings.MEDIA_ROOT, "test6.png"),
            face_encoding=cls.face_encoding6.tobytes(),
            encoding_status="PENDING",
        )

    @classmethod
    def tearDownClass(cls):
        FaceImage.objects.all().delete()
        APIKey.objects.all().delete()

    def test_unauthenticated_retrieve_avg_face_encodings(self):
        message = "Authentication credentials were not provided."
        response = self.client.get(path=self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn(message, str(response.data))

    def test_success_retrieve_avg_face_encodings(self):
        expected_average_encoding = np.mean([self.face_encoding1, self.face_encoding3, self.face_encoding4], axis=0)

        response = self.client.get(path=self.url, HTTP_AUTHORIZATION=f"Api-Key {self.key}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(response.data["average_face_encoding"], expected_average_encoding.tolist())

    def test_calculate_average_face_encoding_insufficient_face_encodings_view(self):
        # Delete all face encodings except one from the database
        self.face_image3.delete()
        self.face_image4.delete()
        message = "Insufficient face encodings to calculate average."

        response = self.client.get(path=self.url, HTTP_AUTHORIZATION=f"Api-Key {self.key}")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(message, str(response.data))

    def test_calculate_average_face_encoding_no_face_encodings_view(self):
        # Delete all face encodings from the database
        FaceImage.objects.all().delete()
        message = "No face encodings found."

        response = self.client.get(path=self.url, HTTP_AUTHORIZATION=f"Api-Key {self.key}")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(message, str(response.data))
