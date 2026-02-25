from django.contrib import admin
from django.urls import include, path
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import CreateView
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator          
from django.utils import timezone                    
from blog.models import Post   
from django.conf import settings
from django.conf.urls.static import static       
from blog.views import UserUpdateView               


def profile_view(request, username):
    user = get_object_or_404(get_user_model(), username=username)
    if request.user == user:
        post_list = user.post_set.all().order_by('-pub_date')
    else:
        post_list = user.post_set.filter(
            is_published=True,
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(
        request,
        'profile.html',
        {'profile_user': user, 'page_obj': page_obj}
    )


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('blog.urls', namespace='blog')),
    path('pages/', include('pages.urls', namespace='pages')),
    path('auth/', include('django.contrib.auth.urls')),
    path('auth/registration/',
         CreateView.as_view(
             template_name='registration/registration_form.html',
             form_class=UserCreationForm,
             success_url='/auth/login/'
         ), name='registration'),
    path('profile/<str:username>/', profile_view, name='profile'),
    path('auth/edit/', UserUpdateView.as_view(), name='edit_profile'),
]

handler403 = 'pages.views.csrf_failure'
handler404 = 'pages.views.page_not_found'
handler500 = 'pages.views.server_error'

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)