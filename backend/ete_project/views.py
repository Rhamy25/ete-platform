from django.shortcuts import render
from django.http import JsonResponse

def home_view(request):
    """Page d'accueil ETE avec design intégré."""
    return render(request, 'home.html')

def api_status(request):
    """Status de l'API ETE."""
    return JsonResponse({
        'status': 'success',
        'message': 'API ETE fonctionnelle',
        'version': '1.0',
        'endpoints': {
            'accounts': '/api/accounts/',
            'clients': '/api/clients/', 
            'agents': '/api/agents/',
            'admin': '/admin/'
        }
    })