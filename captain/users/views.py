from django.contrib import messages
from django.core.urlresolvers import reverse_lazy
from django.views.generic import UpdateView

from guardian.mixins import LoginRequiredMixin

from captain.users.forms import EditProfileForm


class UpdateUserProfile(LoginRequiredMixin, UpdateView):
    template_name = 'users/update_profile.html'
    success_url = reverse_lazy('projects.all')

    def get_object(self, *args, **kwargs):
        """Return the current user's profile instead of fetching one from the URL."""
        return self.request.user.profile

    def get_form_class(self):
        return EditProfileForm

    def form_valid(self, *args, **kwargs):
        response = super(UpdateUserProfile, self).form_valid(*args, **kwargs)
        messages.success(self.request, 'Your profile has been updated!')
        return response
