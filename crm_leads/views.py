from django.shortcuts import render

def dark_mode_test(request):
    """
    View for testing dark mode implementation across different app components.
    """
    return render(request, 'dark_mode_test.html') 