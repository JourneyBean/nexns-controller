from rest_framework.authentication import SessionAuthentication


class SessionAuthenticationExemptApiKeyCsrf(SessionAuthentication):
    def enforce_csrf(self, request):
        if request.is_apikey_auth:
            return
        return super().enforce_csrf(request)
