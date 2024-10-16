from django.contrib import admin
from .models import User, JobSeeker, Employer, Category, JobType, Skill, EducationLevel, Job

admin.site.register(User)
admin.site.register(JobSeeker)
admin.site.register(Employer)
admin.site.register(Category)
admin.site.register(JobType)
admin.site.register(Skill)
admin.site.register(EducationLevel)
admin.site.register(Job)
