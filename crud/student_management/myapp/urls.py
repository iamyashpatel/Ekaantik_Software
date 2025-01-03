from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, SubjectViewSet, MarksViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'subjects', SubjectViewSet)
router.register(r'marks', MarksViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
