from api.algorithm.imports import *
from api.algorithm.processing_pipeline import ProcessingPipeline
from api.serializers import PlariarismRequestSerializer, PlariarismResultSerializer
from django.contrib.auth.models import User
from django.shortcuts import render
from rest_framework import authentication, generics, permissions, status
from rest_framework.response import Response
from django.views import View
from django.http import JsonResponse
from django.conf import settings
from dataclasses import dataclass
from api.algorithm.downloaders import Downloader

# from rest_framework.views import APIView

logger = logging.Logger(__name__)
pipeline = ProcessingPipeline()


@dataclass
class Entry:
    pos: int
    length: int
    url: str


@dataclass
class Result:
    plagiarism_percent: float
    urls: list[Dict[str, Union[int, str]]]
    entries: list[Entry]


class UploadChunkView(View):
    def post(self, request):
        file_name = request.headers.get('X-File-Name')
        chunk_index = int(request.headers.get('X-Chunk-Index'))
        total_chunks = int(request.headers.get('X-Total-Chunks'))

        chunk_data = request.body

        file_path = os.path.join(settings.MEDIA_ROOT, file_name)



class DetectPlagiarismView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = PlariarismRequestSerializer

    def process(self, text):
        """
        Process the given text to find plagiarism.

        Args:
            text (str): The text to be processed.

        Returns:
            Result: An instance of the Result class containing the plagiarism percentage,
            URLs of potentially plagiarized content, and other relevant information.
        """

        result = Result(
            plagiarism_percent=0.0,
            urls=[],
            entries=[],
        )

        results_text = pipeline.process(text)

        # loop url_to_plagiarism do
        for url_to_plagiarism in results_text:
            if url_to_plagiarism is None:
                logger.error("Помилка: функція results_text повернула None.")
                continue

            url, percentage = url_to_plagiarism

            try:
                percentage = float(percentage)

                result.urls.append(
                    {
                        "url": url,
                        "plagiarism_percent": percentage,
                    }
                )

                result.plagiarism_percent = max(result.plagiarism_percent, percentage)
            except ValueError:
                logger.error(f"Файл: {url} - отримано помилку: {percentage}.")

        for url_entry in result.urls:
            url_entry["plagiarism_percent"] = "{:.2f}".format(
                url_entry["plagiarism_percent"] * 100
            )

        result.plagiarism_percent = "{:.2f}".format(result.plagiarism_percent * 100)

        return result  # Result(plagiarism_percent=0.0, urls=[], entries=[])

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = self.process(serializer.extract_text())
        serialized_result = PlariarismResultSerializer(result).data
        return Response(serialized_result, status=status.HTTP_201_CREATED)
