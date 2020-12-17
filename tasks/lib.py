

class PmPermissionMixin:
    def only_for_pm(self, request):
        if request.user.is_anonymous:
            return True
        return True if request.user.role == 'pm' else False


