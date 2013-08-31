from guardian.mixins import PermissionRequiredMixin as GuardianPermissionRequiredMixin


class PermissionRequiredMixin(GuardianPermissionRequiredMixin):
    """
    Extends django-guardian's PermissionRequiredMixin to support redirecting if a user is logged in
    but doesn't have permission.
    """
    def check_permissions(self, request):
        forbidden = super(PermissionRequiredMixin, self).check_permissions(request)
        if forbidden and request.user.is_authenticated():
            return self.permission_denied()
        else:
            return forbidden

    def permission_denied(self):
        """Return a response if the user is authenticated but the permission check failed."""
