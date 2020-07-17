from rest_framework.views import exception_handler 

def tracker_exception_handler(exc, context):

    # Let DRF's exception handler construct the initial response
    response = exception_handler(exc, context)

    # If exception is known to us, list it here
    handlers = {
        'ValidationError': _handle_generic_error
    }

    # Get exception class name
    exception_class = exc.__class__.__name__

    # If known, then we handle it
    if exception_class in handlers:
        return handlers[exception_class](exc, context, response)
    
    return response 


def _handle_generic_error(exc, context, response):
    # Handler which wraps DRF exception handler's response 
    # in 'errors'
    response.data = {
        'errors': response.data
    }

    return response

