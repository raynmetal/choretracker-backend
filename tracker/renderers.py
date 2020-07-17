import json 

from rest_framework.renderers import JSONRenderer 

class UserJSONRenderer(JSONRenderer):
    """
    Renderers take the intermediate step of template and context 
    and converts it to the final byte stream served to the client.
    """
    charset = 'utf-8'

    def render(self, data, media_type=None, renderer_context=None):
        
        token = data.get('token', None)

        # Replace byte token with utf-8 token, which plays 
        # better with a serializer
        if token is not None and isinstance(token, bytes):
            data['token'] = token.decode('utf-8')
        
        # Return the new 'data', which is the old data nested under
        # the key 'user'
        return json.dumps({
            'user': data
        })