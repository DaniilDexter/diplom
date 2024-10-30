from django.contrib import admin

from project.models import Project
from project.models import ProjectMembers

admin.site.register(Project)
admin.site.register(ProjectMembers)

