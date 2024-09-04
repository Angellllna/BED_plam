from rest_framework import serializers
from api.algorithm.imports import *

class PlariarismRequestSerializer(serializers.Serializer):
    text = serializers.CharField(max_length=2048, required=False)
    file = serializers.FileField(required=False)

    def validate(self, data):
        if not data.get("text") and not data.get("file"):
            raise serializers.ValidationError(
                "Either 'text' or 'file' must be provided."
            )
        return data

    def extract_text(self):
        if self.validated_data.get("text"):
            return self.validated_data["text"]
        elif file := self.validated_data.get("file"):
            content = file.read()

            parsed = parser.from_buffer(content)

            return parsed["content"] or ""
        else:
            return ""


class PlagiarismEntrySerializer(serializers.Serializer):
    pos = serializers.IntegerField()
    length = serializers.IntegerField()
    url = serializers.URLField()


class PlariarismResultSerializer(serializers.Serializer):
    plagiarism_percent = serializers.CharField()
    urls = serializers.JSONField()
    entries = PlagiarismEntrySerializer(many=True)
