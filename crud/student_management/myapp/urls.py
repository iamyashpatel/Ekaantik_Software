from django.urls import path
from .views import home, user_api, marks_api, subject_api

urlpatterns = [
    path('', home, name='home'),  # Root URL
    path('api/users/', user_api, name='user_list_create'),
    path('api/users/<int:pk>/', user_api, name='user_detail_update_delete'),
    path('api/marks/', marks_api, name='marks_list_create'),
    path('api/marks/<int:pk>/', marks_api, name='marks_detail'),
    path('api/subjects/', subject_api, name='subject_list_create'),
    path('api/subjects/<int:pk>/', subject_api, name='subject_detail_update_delete'),
]
