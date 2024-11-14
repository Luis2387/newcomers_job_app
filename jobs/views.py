from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import RegisterSerializer
from rest_framework import generics
from .models import Category, JobType, Skill, EducationLevel, Job, CompanyProfile, Employer
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .serializers import RegisterSerializer,CategorySerializer, JobTypeSerializer, SkillSerializer, EducationLevelSerializer, JobSerializer, CompanyProfileSerializer, JobSeekerProfileSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db.models import Q
from rest_framework.exceptions import NotFound


class RegisterView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User created successfully"}, status=201)
        return Response(serializer.errors, status=400)

class UserTypeProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_type = request.user.user_type
        return Response({'user_type': user_type}, status=200)


class CategoryListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class JobTypeListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = JobType.objects.all()
    serializer_class = JobTypeSerializer


class SkillListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer


class EducationLevelListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = EducationLevel.objects.all()
    serializer_class = EducationLevelSerializer


class JobCreateAPIView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Job.objects.all()
    serializer_class = JobSerializer

class JobDetailAPIView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    queryset = Job.objects.all()
    serializer_class = JobSerializer


class EmployerJobListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = JobSerializer

    def get_queryset(self):
        employer = self.request.user.employer
        return Job.objects.filter(employer=employer)


class JobDeleteAPIView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Job.objects.all()
    serializer_class = JobSerializer

    def delete(self, request, *args, **kwargs):
        job = self.get_object()
        if job.employer.user == request.user:
            job.delete()
            return Response({"message": "Job deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)


class JobUpdateAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Job.objects.all()

    def get_object(self):
        obj = super().get_object()        
        if obj.employer.user != self.request.user:
            raise PermissionDenied("Failed to update Job")
        return obj


class JobSearchAPIView(generics.ListAPIView):
    permission_classes = [AllowAny]
    queryset = Job.objects.all()
    serializer_class = JobSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        search_term = self.request.query_params.get('q', None)

        if search_term:
            queryset = queryset.filter(
                Q(title__icontains=search_term) |
                Q(description__icontains=search_term) |
                Q(location__icontains=search_term) |
                Q(min_salary__icontains=search_term) |
                Q(max_salary__icontains=search_term) |
                Q(experience_level__icontains=search_term) |
                Q(employer__user__first_name__icontains=search_term) |
                Q(employer__user__last_name__icontains=search_term) |
                Q(category__name__icontains=search_term) |
                Q(job_type__name__icontains=search_term) |
                Q(skills__name__icontains=search_term) |
                Q(education_level__name__icontains=search_term)
            ).distinct()  
        return queryset


class EmployerProfileAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CompanyProfileSerializer

    def get_object(self):
        
        employer = getattr(self.request.user, 'employer', None)
        
        if not employer or not employer.company_profile:
            raise NotFound("Company profile not assigned")
       
        return employer.company_profile


class JobSeekerProfileAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = JobSeekerProfileSerializer

    def get_object(self):

        jobseeker = getattr(self.request.user, 'jobseeker', None)

        if not jobseeker or not jobseeker.jobseeker_profile:
            raise NotFound("Job seeker profile not assigned.")
        
        return jobseeker.jobseeker_profile
