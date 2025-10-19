from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods

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
            'admin': '/admin/',
            'admin_custom': '/administration/'
        }
    })

@staff_member_required
def admin_redirect(request):
    """Redirection vers l'interface d'administration personnalisée."""
    return redirect('admin_dashboard')

@csrf_protect
@require_http_methods(["POST"])
def admin_login_view(request):
    """Vue de connexion pour l'administration"""
    
    username = request.POST.get('username')
    password = request.POST.get('password')
    user_type = request.POST.get('user_type', 'admin')
    
    if not username or not password:
        messages.error(request, 'Veuillez remplir tous les champs.')
        return redirect('home')
    
    # Authentification de l'utilisateur
    user = authenticate(request, username=username, password=password)
    
    if user is not None:
        # Vérifier si l'utilisateur est autorisé selon le type de connexion
        if user_type == 'admin' and user.is_staff:
            login(request, user)
            messages.success(request, f'Bienvenue {user.get_full_name() or user.username} !')
            return redirect('admin_dashboard')
        elif user_type == 'agent' and hasattr(user, 'agent_profile'):
            login(request, user)
            messages.success(request, f'Bienvenue Agent {user.agent_profile.matricule} !')
            return redirect('admin_dashboard')  # Ou une page spécifique aux agents
        else:
            messages.error(request, 'Vous n\'avez pas les permissions pour accéder à cette interface.')
    else:
        messages.error(request, 'Identifiants incorrects. Veuillez réessayer.')
    
    return redirect('home')

@login_required
def admin_logout_view(request):
    """Déconnexion de l'administration"""
    logout(request)
    messages.success(request, 'Vous avez été déconnecté avec succès.')
    return redirect('home')