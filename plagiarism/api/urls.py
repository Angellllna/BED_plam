from api.views import DetectPlagiarismView
from django.urls import path

urlpatterns = [
    
    path("detect_plagiarism/", DetectPlagiarismView.as_view())
]