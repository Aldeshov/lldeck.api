import logging

from django.utils.translation import gettext_lazy as _
from rest_framework import views, status
from rest_framework.exceptions import APIException

from applications.models import Profile

logger = logging.getLogger(__name__)


class ProfileCheckHelper(views.APIView):
    class ProfileDoesNotExist(APIException):
        status_code = status.HTTP_400_BAD_REQUEST
        default_detail = _('Profile for the current user does not exist.')
        default_code = 'do_not_have_profile'

    def check_permissions(self, request):
        super(ProfileCheckHelper, self).check_permissions(request)
        try:
            request.user.profile
        except Profile.DoesNotExist as error:
            logger.error(error)
            raise self.ProfileDoesNotExist()
