from django.db import models
from django.contrib.auth.models import AbstractUser

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

    
    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'


class JobSeekerProfile(models.Model):
    profile_description = models.TextField(blank=True)    

    def __str__(self):
        return self.id


class Employer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=200)    
    company_profile = models.OneToOneField('CompanyProfile', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.company_name


class CompanyProfile(models.Model):
    profile_description = models.TextField(blank=True)
    
    def __str__(self):
        return self.id