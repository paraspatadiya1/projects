from .models import patientsignup

def patient_context(request):
    """
    Context processor that injects the currently logged-in patient into all templates.
    """
    user = None
    if hasattr(request, 'session') and 'userid' in request.session:
        user = patientsignup.objects.filter(id=request.session['userid']).first()
    return {
        'patient_user': user,
        'user': user, # overrides or provides user object safely for all templates
    }
