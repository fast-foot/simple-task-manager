from rest_framework import status


class ResponsePayload:
    def __init__(self):
        self.BAD_REQUEST = {
            'code': status.HTTP_400_BAD_REQUEST,
            'message': 'Bad request'
        }


class APIConfig:
    def __init__(self):
        self.response_payload = ResponsePayload()

api_config = APIConfig()