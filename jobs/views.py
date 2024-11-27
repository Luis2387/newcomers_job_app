from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from .models import Category, JobType, Skill, EducationLevel, Job, CompanyProfile, Employer, Resume, Application, JobSeekerProfile, JobSeeker
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .serializers import RegisterSerializer,CategorySerializer, JobTypeSerializer, SkillSerializer, EducationLevelSerializer, JobSerializer, CompanyProfileSerializer, JobSeekerProfileSerializer, ResumeSerializer, ApplicationSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db.models import Q
from rest_framework.exceptions import NotFound
from rest_framework import viewsets, mixins
from django.contrib.auth import logout
from rest_framework_simplejwt.tokens import RefreshToken


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
    permission_classes = [AllowAny]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class JobTypeListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    queryset = JobType.objects.all()
    serializer_class = JobTypeSerializer


class SkillListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer


class EducationLevelListView(generics.ListAPIView):
    permission_classes = [AllowAny]
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
    permission_classes = [AllowAny]
    serializer_class = CompanyProfileSerializer

    def get_object(self):

        profile_id = self.kwargs.get("id", None)
        
        if profile_id:
            try:
                profile = CompanyProfile.objects.get(id=profile_id)
                return profile
            except CompanyProfile.DoesNotExist:
                raise NotFound("Company profile not found for the provided ID.")

        
        employer = getattr(self.request.user, 'employer', None)
        
        if not employer or not employer.company_profile:
            raise NotFound("Company profile not assigned")
       
        return employer.company_profile


class JobSeekerProfileAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = JobSeekerProfileSerializer

    def get_permissions(self):
        if self.request.method == 'GET' and not self.kwargs.get("id"):
            return [IsAuthenticated()]  # Asegura autenticación para peticiones sin ID
        elif self.request.method == 'PUT':
            return [IsAuthenticated()]
        return [AllowAny()]


    def get_object(self):

        profile_id = self.kwargs.get("id", None)
        
        if profile_id:
            try:
                profile = JobSeekerProfile.objects.get(id=profile_id)
                return profile
            except JobSeekerProfile.DoesNotExist:
                raise NotFound("Candidate profile not found for the provided ID.")

        jobseeker = getattr(self.request.user, 'jobseeker', None)

        if not jobseeker or not jobseeker.jobseeker_profile:
            raise NotFound("Job seeker profile not assigned.")
        
        return jobseeker.jobseeker_profile


class ResumeAPIView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET' and not self.kwargs.get("id"):
            return [IsAuthenticated()]  # Asegura autenticación para peticiones sin ID
        elif self.request.method == 'PUT':
            return [IsAuthenticated()]
        return [AllowAny()]

    def get(self, request, id=None):

        try:
            if id:
                jobseeker_profile = JobSeekerProfile.objects.get(id=id)
                jobseeker = jobseeker_profile.jobseeker
                resume = Resume.objects.get(jobseeker_resume=jobseeker)
            else:
                if not request.user.is_authenticated:
                    return Response({"detail": "Authentication required for this action."}, status=status.HTTP_401_UNAUTHORIZED)
                resume = Resume.objects.get(jobseeker_resume__user=request.user)
            
            serializer = ResumeSerializer(resume)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except JobSeekerProfile.DoesNotExist:
            return Response({"detail": "Candidate not found."}, status=status.HTTP_404_NOT_FOUND)
        except Resume.DoesNotExist:
            return Response({"detail": "Resume not found."}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request):

        if not request.user.is_authenticated:
            return Response({"detail": "Authentication required for this action."}, status=status.HTTP_401_UNAUTHORIZED)

        print("Datos recibidos en el backend:", request.data)

        try:
            resume = Resume.objects.get(jobseeker_resume__user=request.user)
            serializer = ResumeSerializer(resume, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                print("Errores del serializer:", serializer.errors)  # Para depurar errores
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Resume.DoesNotExist:
            return Response({"detail": "Resume not found."}, status=status.HTTP_404_NOT_FOUND)


class JobApplicationsListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        jobseeker = request.user.jobseeker
        applications = Application.objects.filter(jobseeker=jobseeker).select_related('job', 'job__employer')
        serializer = ApplicationSerializer(applications, many=True)
        return Response(serializer.data)


class JobApplicantsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, job_id):
        applications = Application.objects.filter(job__id=job_id).select_related('jobseeker__user')
        serializer = ApplicationSerializer(applications, many=True)
        return Response(serializer.data)


class ApplicationStatusUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            application = Application.objects.get(pk=pk)
            status_value = request.data.get("status")
            if status_value:
                application.status = status_value
                application.save()
                serializer = ApplicationSerializer(application)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Status is required."}, status=status.HTTP_400_BAD_REQUEST)
        except Application.DoesNotExist:
            return Response({"error": "Application not found."}, status=status.HTTP_404_NOT_FOUND)


class LogoutAPIView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response({"error": "Refresh token missing"}, status=400)

            token = RefreshToken(refresh_token)
            token.blacklist() 
            return Response({"message": "Logout successful"}, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=400)


class CreateApplicationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:

            job_id = request.data.get("job")
            if not job_id:
                return Response({"error": "Job ID is required."}, status=status.HTTP_400_BAD_REQUEST)

            try:
                job = Job.objects.get(id=job_id)
            except Job.DoesNotExist:
                return Response({"error": "Job not found."}, status=status.HTTP_404_NOT_FOUND)

            jobseeker = getattr(request.user, 'jobseeker', None)
            if not jobseeker:
                return Response({"error": "Only jobseekers can apply for jobs."}, status=status.HTTP_403_FORBIDDEN)

            if Application.objects.filter(job=job, jobseeker=jobseeker).exists():
                return Response({"error": "You have already applied for this job."}, status=status.HTTP_400_BAD_REQUEST)

            application = Application.objects.create(job=job, jobseeker=jobseeker)
            return Response({"message": "Application submitted successfully."}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)