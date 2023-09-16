from django.shortcuts import render


def pagina_erro_404(request, exception):
    return render(request, '404.html', status=404)
