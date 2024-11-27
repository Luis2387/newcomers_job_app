from rest_framework import serializers
from .models import User, JobSeeker, Employer, Job, Category, JobType, Skill, EducationLevel, CompanyProfile, JobSeekerProfile, Resume, CandidateSkill, Education, Experience, Application
import logging


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
            resume = Resume.objects.create()
            candidate_profile = JobSeekerProfile.objects.create()
            JobSeeker.objects.create(user=user,jobseeker_profile=candidate_profile, resume=resume)
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

class EmployerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employer
        fields = ['id', 'company_name']


class CompanyProfileSerializer(serializers.ModelSerializer):
    company_name = serializers.SerializerMethodField()

    class Meta:
        model = CompanyProfile
        fields = ['id','phone', 'email', 'website', 'profile_description', 'linkedin', 'facebook', 'twitter', 'tiktok', 'location', 'category', 'company_name']


    def get_company_name(self, obj):
        employer = Employer.objects.filter(company_profile=obj).first()
        return employer.company_name if employer else None


class JobSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    job_type = serializers.PrimaryKeyRelatedField(queryset=JobType.objects.all())
    skills = serializers.PrimaryKeyRelatedField(many=True, queryset=Skill.objects.all())
    education_level = serializers.PrimaryKeyRelatedField(queryset=EducationLevel.objects.all())
    date_posted = serializers.DateTimeField(format="%Y-%m-%d %H:%M", read_only=True)
    active = serializers.BooleanField(read_only=True)
    id = serializers.ReadOnlyField()
    employer_profile = CompanyProfileSerializer(source='employer.company_profile', read_only=True)

    class Meta:
        model = Job
        fields = ['id','title', 'description', 'experience_level', 'min_salary', 'max_salary', 'location', 'category', 'job_type', 'skills', 'education_level','date_posted','active','employer_profile']

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


class JobseekerSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = JobSeeker
        fields = ['id', 'user']

    def get_user(self, obj):
        return {
            "first_name": obj.user.first_name,
            "last_name": obj.user.last_name,
        }



class JobSeekerProfileSerializer(serializers.ModelSerializer):
    jobseeker = JobseekerSerializer(read_only=True)

    class Meta:
        model = JobSeekerProfile
        fields = ['id','jobseeker','profile_description', 'phone', 'email', 'website', 'linkedin', 'location']

    def get_user(self, obj):
        return {
            "first_name": obj.jobseeker.user.first_name,
            "last_name": obj.jobseeker.user.last_name,
        }


class CandidateSkillSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = CandidateSkill
        fields = ['id', 'name', 'proficiency']

class EducationSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False) 
    level = EducationLevelSerializer()

    class Meta:
        model = Education
        fields = ['id', 'level', 'school', 'start_date', 'end_date']


class ExperienceSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False) 

    class Meta:
        model = Experience
        fields = ['id', 'company', 'position', 'start_date', 'end_date', 'short_description']



class ResumeSerializer(serializers.ModelSerializer):
    candidate_skills = CandidateSkillSerializer(many=True)
    educations = EducationSerializer(many=True)
    experiences = ExperienceSerializer(many=True)

    class Meta:
        model = Resume
        fields = ['id', 'candidate_skills', 'educations', 'experiences']

    def update(self, instance, validated_data):

        # Handle candidate_skills
        candidate_skills_data = validated_data.pop('candidate_skills', [])
        instance.candidate_skills.clear()

        for skill_data in candidate_skills_data:
            skill_id = skill_data.get('id')
            if skill_id:
                
                skill = CandidateSkill.objects.get(id=skill_id)
                for attr, value in skill_data.items():
                    setattr(skill, attr, value)
                skill.save()
                instance.candidate_skills.add(skill)
            else:
                
                skill = CandidateSkill.objects.create(**skill_data)
                instance.candidate_skills.add(skill)

        # Handle educations
        educations_data = validated_data.pop('educations', [])
        instance.educations.clear()

        for education_data in educations_data:
            education_id = education_data.get('id')
           
            # Handle level
            level_data = education_data.pop('level', None)
            if level_data:
                level_id = level_data.get('id')
                
                if level_id:
                    level_instance = EducationLevel.objects.get(id=level_id)
                else:
                    level_instance, _ = EducationLevel.objects.get_or_create(**level_data)
                education_data['level'] = level_instance

            if education_id:
                education = Education.objects.get(id=education_id)
                for attr, value in education_data.items():
                    setattr(education, attr, value)
                education.save()
                instance.educations.add(education)
            else:
                education = Education.objects.create(**education_data)
                instance.educations.add(education)

        # Handle experiences
        experiences_data = validated_data.pop('experiences', [])
        instance.experiences.clear()

        for experience_data in experiences_data:
            experience_id = experience_data.get('id')
            if experience_id:
                experience = Experience.objects.get(id=experience_id)
                for attr, value in experience_data.items():
                    setattr(experience, attr, value)
                experience.save()
                instance.experiences.add(experience)
            else:
                experience = Experience.objects.create(**experience_data)
                instance.experiences.add(experience)

        instance.save()

        return instance


class ApplicationSerializer(serializers.ModelSerializer):
    jobseeker = JobseekerSerializer()
    job = serializers.SerializerMethodField()

    class Meta:
        model = Application
        fields = ['id', 'job', 'jobseeker', 'application_date', 'status']

    def get_job(self, obj):
        return {
            "id": obj.job.id,
            "title": obj.job.title,
            "location": obj.job.location,
            "company_name": obj.job.employer.company_name,
        }




