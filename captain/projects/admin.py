from django.contrib import admin

from guardian.admin import GuardedModelAdmin

from captain.projects import models


class ProjectAdmin(GuardedModelAdmin):
    list_display = ['name', 'homepage']
    prepopulated_fields = {'slug': ('name',)}


admin.site.register(models.Project, ProjectAdmin)
