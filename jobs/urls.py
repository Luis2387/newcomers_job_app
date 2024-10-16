from django.urls import path
from .views import RegisterView, UserTypeProfileView, CategoryListView, JobTypeListView, SkillListView, EducationLevelListView, JobCreateAPIView, EmployerJobListAPIView, JobDeleteAPIView, JobSearchAPIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    
    path('register/', RegisterView.as_view(), name='register'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('userTypeProfile/', UserTypeProfileView.as_view(), name='UserTypeProfile'),
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('job-types/', JobTypeListView.as_view(), name='jobtype-list'),
    path('skills/', SkillListView.as_view(), name='skill-list'),
    path('education-levels/', EducationLevelListView.as_view(), name='educationlevel-list'),
    path('create-job/', JobCreateAPIView.as_view(), name='create_job'),
    path('employer-jobs/', EmployerJobListAPIView.as_view(), name='employer-jobs'),
    path('delete-job/<int:pk>/', JobDeleteAPIView.as_view(), name='job-delete'),
    path('search-jobs/', JobSearchAPIView.as_view(), name='search-jobs'),
]