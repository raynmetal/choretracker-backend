import jwt
from datetime import datetime

from django.conf import settings 

from rest_framework import authentication, exceptions

from tracker.models import User 

class JWTAuthentication(authentication.BaseAuthentication):
    authentication_header_prefix = 'Token'

    def authenticate(self, request):
        """
        This method is called on every request, regardless of
        whether the endpoint requires authentication
        
        'authenticate' has two possible return values:
        None 
            if authentication will fail, say if the request does not
            include a token in the headers 
        
        (user, token)
            When authentication is successful

        raise 'AuthenticationFailed' 
            otherwise
        """

        request.user = None 

        # Is an array with two elements. The name of authentication 
        # header, and the JWT to authenticate against
        auth_header = authentication.get_authorization_header(request).split()
        auth_header_prefix = self.authentication_header_prefix.lower()

        if not auth_header:
            return None 
        
        if len(auth_header) == 1:
            # Invalid token header, no credentials provided
            return None
        
        elif len(auth_header) > 2:
            # Invalid token header. Token string should not contain 
            # spaces
            return None 
        
        # Python 3 commonly use the 'byte' type, while the 
        # jwt library we're using expects utf-8 encoding
        prefix = auth_header[0].decode('utf-8')
        token = auth_header[1].decode('utf-8')

        if prefix.lower() != auth_header_prefix:
            # Auth header prefix not what we expected
            return None 
        
        return self._authenticate_credentials(request, token)

    def _authenticate_credentials(self, request, token):
        """
        Authenticate with given credentials 
        """
        
        try:
            payload = jwt.decode(token, settings.SECRET_KEY)
        except:
            msg = 'Invalid authentication. Could not decode token.'
            raise exceptions.AuthenticationFailed(msg)

        try:
            user = User.objects.get(pk=payload['id'])
        except User.DoesNotExist:
            msg = 'No user matching this token was found.'
            raise exceptions.AuthenticationFailed(msg)
        
        if not user.is_active:
            msg = 'This user has been deactivated.'
            raise exceptions.AuthenticationFailed(msg)
        
        if datetime.fromtimestamp(payload['exp']) <= datetime.now():
            msg = 'This token is no longer valid. Please log in again'
            raise exceptions.AuthenticationFailed(msg)


        return(user, token)