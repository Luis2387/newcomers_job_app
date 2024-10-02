from django.contrib import admin
from .models import User, JobSeeker, Employer

admin.site.register(User)
admin.site.register(JobSeeker)
admin.site.register(Employer)

