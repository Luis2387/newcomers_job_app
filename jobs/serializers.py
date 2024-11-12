from rest_framework import serializers
from .models import User, JobSeeker, Employer, Job, Category, JobType, Skill, EducationLevel, CompanyProfile

class RegisterSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(allow_blank=True, required=False)

    class Meta:
        model = User
        fields = ['password', 'email', 'first_name', 'last_name', 'company_name', 'user_type']
        extra_kwargs = {
            'password': {'write_only': True},
            'first_name': {'required': False, 'allow_blank': True},
            'last_name': {'required': False, 'allow_blank': True},
        }

    def validate(self, data):
        user_type = data.get('user_type')

        if user_type == 'jobseeker':
            if not data.get('first_name'):
                raise serializers.ValidationError("Please enter first name")
            if not data.get('last_name'):
                raise serializers.ValidationError("Please enter last name")
            if not data.get('email'):
                raise serializers.ValidationError("Please enter email")
            if not data.get('password'):
                raise serializers.ValidationError("Please enter password")


        if user_type == 'employer':
            if not data.get('company_name'):
                raise serializers.ValidationError("Please enter a company name")
            if not data.get('email'):
                raise serializers.ValidationError("Please enter email")
            if not data.get('password'):
                raise serializers.ValidationError("Please enter password")

        return data

    def create(self, validated_data):
        user_type = validated_data.get('user_type')

        company_name = validated_data.pop('company_name', None)
        
        
        user = User.objects.create_user(
            username=validated_data['email'],
            password=validated_data['password'],
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            user_type=user_type
        )

        if user_type == 'jobseeker':
            JobSeeker.objects.create(user=user)
        elif user_type == 'employer':
            company_profile = CompanyProfile.objects.create()
            Employer.objects.create(user=user, company_name=company_name, company_profile=company_profile)

        return user


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']

class JobTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobType
        fields = ['id', 'name', 'description']

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name', 'description']

class EducationLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = EducationLevel
        fields = ['id', 'name', 'description']

class JobSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    job_type = serializers.PrimaryKeyRelatedField(queryset=JobType.objects.all())
    skills = serializers.PrimaryKeyRelatedField(many=True, queryset=Skill.objects.all())
    education_level = serializers.PrimaryKeyRelatedField(queryset=EducationLevel.objects.all())
    date_posted = serializers.DateTimeField(format="%Y-%m-%d %H:%M", read_only=True)
    active = serializers.BooleanField(read_only=True)
    id = serializers.ReadOnlyField()

    class Meta:
        model = Job
        fields = ['id','title', 'description', 'experience_level', 'min_salary', 'max_salary', 'location', 'category', 'job_type', 'skills', 'education_level','date_posted','active']

    def validate(self, data):
        if data['min_salary'] > data['max_salary']:
            raise serializers.ValidationError("Minimum salary can't be greater than maximum salary")
        return data

    def create(self, validated_data):
        skills_data = validated_data.pop('skills', [])
        request = self.context.get('request', None)
        employer = Employer.objects.get(user=request.user)
        job = Job.objects.create(employer=employer, **validated_data)
        job.skills.set(skills_data)
        return job


class CompanyProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyProfile
        fields = ['phone', 'email', 'website', 'profile_description', 'linkedin', 'facebook', 'twitter', 'tiktok', 'location', 'category']
