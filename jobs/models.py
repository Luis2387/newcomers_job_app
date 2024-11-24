from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

# Custom user model extending Django's AbstractUser
class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('jobseeker', 'Job Seeker'),
        ('employer', 'Employer'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    

class JobSeeker(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)    
    jobseeker_profile = models.OneToOneField('JobSeekerProfile', on_delete=models.SET_NULL, null=True, blank=True)
    resume = models.OneToOneField('Resume', on_delete=models.SET_NULL, null=True, blank=True, related_name='jobseeker_resume')

    
    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'


class JobSeekerProfile(models.Model):
    profile_description = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    location = models.CharField(max_length=255, blank=True)    

    def __str__(self):
        return f"Profile {self.id}"


class Resume(models.Model):
    candidate_skills = models.ManyToManyField('CandidateSkill', blank=True, related_name='resumes')  
    educations = models.ManyToManyField('Education', blank=True, related_name='resumes')  
    experiences = models.ManyToManyField('Experience', blank=True, related_name='resumes')

    def __str__(self):
        return f"Resume for {self.jobseeker_resume.user.username}"


class CandidateSkill(models.Model):
    name = models.CharField(max_length=255)
    PROFICIENCY_CHOICES = [
        ('basic', 'Basic'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    proficiency = models.CharField(max_length=15, choices=PROFICIENCY_CHOICES, default='basic')

    def __str__(self):
        return f"{self.name} - {self.proficiency}"


class EducationLevel(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Education(models.Model):
    level = models.ForeignKey('EducationLevel', on_delete=models.CASCADE, null=True, blank=True)    
    school = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    
    def __str__(self):
        return f"{self.level} - {self.school}"

class Experience(models.Model):
    company = models.CharField(max_length=255)
    position = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    short_description = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.position} at {self.company}"


class Employer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=200)    
    company_profile = models.OneToOneField('CompanyProfile', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.company_name


class CompanyProfile(models.Model):
    profile_description = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    facebook = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    tiktok = models.URLField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Profile {self.id}"


class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class JobType(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Skill(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Job(models.Model):
    employer = models.ForeignKey(Employer, on_delete=models.CASCADE, related_name="jobs")
    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)
    min_salary = models.DecimalField(max_digits=10, decimal_places=2)
    max_salary = models.DecimalField(max_digits=10, decimal_places=2)
    experience_level = models.CharField(max_length=50)
    date_posted = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    job_type = models.ForeignKey(JobType, on_delete=models.SET_NULL, null=True)
    skills = models.ManyToManyField(Skill, blank=True)
    education_level = models.ForeignKey(EducationLevel, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.title



class Application(models.Model):
    class StatusChoices(models.TextChoices):
        APPLIED = 'Applied', _('Applied')
        UNDER_REVIEW = 'Under Review', _('Under Review')
        INTERVIEWING = 'Interviewing', _('Interviewing')
        SHORTLISTED = 'Shortlisted', _('Shortlisted')
        HIRED = 'Hired', _('Hired')

    jobseeker = models.ForeignKey(JobSeeker, on_delete=models.CASCADE, related_name='applications')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    application_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=50,
        choices=StatusChoices.choices,
        default=StatusChoices.APPLIED,
    )

    def __str__(self):
        return f'{self.jobseeker} applied to {self.job}'

    class Meta:
        unique_together = ('jobseeker', 'job') 

