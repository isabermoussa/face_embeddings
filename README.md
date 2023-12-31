# Face Embeddings APIs

[![Hacksoft](https://img.shields.io/badge/code%20style-hacksoft-ff69b4.svg)](https://github.com/HackSoftware/Django-Styleguide)

This repository contains the code for the Face Embeddings APIs, which provide a set of endpoints to calculate face embeddings of human faces from images. The APIs are built using Django Rest Framework (DRF) and utilize the face_recognition library for face encoding.

## API Endpoints

The following are the available API endpoints:

1. **GET /api/health-check/**: Validate Face Embeddings APIs service is running and its components integrated well.

2. **POST /api/face-image/**: Receives an image file and responds with the face encoding. This endpoint expects a `multipart/form-data` request with the image file attached.

3. **GET /api/face-image/{public_id}/**: Retrieves the face encoding for a previously calculated image identified by its `public_id`.

4. **GET /api/face-image/stats/**: Retrieves statistics about how many images were processed, including the count of images with each encoding status.

5. **GET /api/face-image/avg-encodings/**: Retrieves AVG about face encodings for all previously calculated images.

Here is a [link](https://drive.google.com/file/d/1O0lpLuYXUDd8dScqejQb69fKTpkaI7mF/view?usp=sharing) for postman collection with its environment For APIs.

## Getting Started

To run the Face Embeddings APIs on your local machine, follow these steps:

### Prerequisites

1. Install Docker and Docker Compose on your system.

### Setup

1. Clone this repository to your local machine.

2. Create a `.env` file in the root of the project and configure the environment variables as follows:

   ```plaintext
   # Django Settings
   DEBUG=True
   SECRET_KEY=your_secret_key_here
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432
   POSTGRES_DB=database_name
   POSTGRES_USER=username
   POSTGRES_PASSWORD=password
   ```

3. Build and run using Docker:

   ```bash
   docker compose up -d --build
   ```

4. Admin portal can be accessible at `http://localhost:8000/admin/` with credentials: `admin`, `admin_pass` to create api-key. You should change these credentials from admin portal.

5. The APIs should now be accessible at `http://localhost:8000/api/`.

### API Key Authentication

The Face Embeddings APIs require API key authentication. You must include the API key in the `Authorization` header of each request. For example:

```http
GET /api/face-image/ HTTP/1.1
Host: localhost:8000
Authorization: Api-Key <your_api_key_here>
```

$\textcolor{red}{\textsf{Note:}}$ Api-key generated From Admin portal by superuser, superuser can create new key, define expiry date, refresh and revoke it.

### API Documentation

The API documentation is available using the Swagger UI provided by DRF-Spectacular. You can access it at `http://localhost:8000/api/schema/redoc/`.

### Testing

To run the test suite, use the following command:

```bash
docker exec face_embeddings pytest
```

## Contributing

We welcome contributions to improve and expand the functionality of the Face Embeddings APIs. If you find any issues or have suggestions, please feel free to open a pull request or an issue on GitHub.

### Prerequisite

1. Install PostgreSQL on your system.

### Installation DEV steps

```sh
python3.10 -m pip install --upgrade pip
python3.10 -m pip install pipenv --upgrade
pipenv --python 3.10
pipenv shell
pipenv install (run `pipenv install -d` for local development)
python manage.py migrate
python manage.py createsuperuser
```

### Configuring [Pre-Commit](https://pre-commit.com/)

Please make sure to run following commands before starting any development.

```sh
pre-commit install --hook-type pre-commit
pre-commit install --hook-type pre-push
sh cmd/install_hooks.sh
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
