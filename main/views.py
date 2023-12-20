from rest_framework import viewsets, response


class StatusView(viewsets.ViewSet):

    def list(self, request, format=None):
        return response.Response({
            'status': True,
            'message': 'Service is running.'
        })
    