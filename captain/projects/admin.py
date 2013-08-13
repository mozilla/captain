from django.contrib import admin

from captain.websites import models


class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'homepage']


admin.site.register(models.Project, ProjectAdmin)
