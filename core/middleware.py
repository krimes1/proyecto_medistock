class VendedorReferidoMiddleware:
    """Atrapa el parametro ?ref= de la URL en cualquier pagina y lo guarda en la sesion."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ref = request.GET.get('ref')
        if ref:
            request.session['vendedor_ref'] = ref.strip()
        
        response = self.get_response(request)
        return response
