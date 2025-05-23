from django.urls import path
from .views import*
urlpatterns = [

      path('registeruser/', RegisterUser.as_view(), name='register'),
      path('login/', LoginUser.as_view(), name='login'),
      # path('register/', UserRegisterView.as_view(), name='user-register'),
      path('users/', UserListView.as_view(), name='user-list'),
      path('subjects/', SubjectListCreateAPIView.as_view(), name='subject-list-create'),
      path('enrollments/', EnrollmentListCreateAPIView.as_view(), name='enrollment-list-create'),


]









