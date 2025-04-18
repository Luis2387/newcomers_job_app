from django.contrib import admin
from .models import User, JobSeeker, Employer, Category, JobType, Skill, EducationLevel, Job, CompanyProfile, JobSeekerProfile, Resume, CandidateSkill, Education, Experience, Application

admin.site.register(User)
admin.site.register(JobSeeker)
admin.site.register(Employer)
admin.site.register(Category)
admin.site.register(JobType)
admin.site.register(Skill)
admin.site.register(EducationLevel)
admin.site.register(Job)
admin.site.register(CompanyProfile)
admin.site.register(JobSeekerProfile)
admin.site.register(Resume)
admin.site.register(CandidateSkill)
admin.site.register(Education)
admin.site.register(Experience)
admin.site.register(Application)


