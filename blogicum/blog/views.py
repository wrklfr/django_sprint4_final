from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .models import Post, Category
from django.shortcuts import render, get_object_or_404, redirect
from .forms import PostForm
from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy
from .forms import ProfileEditForm
from django.contrib.auth import get_user_model
from django.http import Http404
from .models import Comment
from .forms import CommentForm

User = get_user_model()
def index(request):
    post_list = Post.objects.filter(
        is_published=True,
        pub_date__lte=timezone.now(),
        category__is_published=True
    ).order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'blog/index.html', {'page_obj': page_obj})


def post_detail(request, id):
    post = get_object_or_404(Post, id=id)
    if request.user != post.author:
        if not post.is_published or post.pub_date > timezone.now() or not post.category.is_published:
            raise Http404("Пост не найден")
    comment_form = CommentForm()
    return render(request, 'blog/detail.html', {
        'post': post,
        'comment_form': comment_form,
    })


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    post_list = Post.objects.filter(
        category=category,
        is_published=True,
        pub_date__lte=timezone.now()
    ).order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(
        request,
        'blog/category.html',
        {'category': category, 'page_obj': page_obj}
    )
from django.contrib.auth.decorators import login_required

@login_required(login_url='/auth/login/')
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.is_published = True
            post.save()
            return redirect('blog:index')  
    else:
        form = PostForm()
    return render(request, 'blog/create.html', {'form': form})

@login_required(login_url='/auth/login/')
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('blog:post_detail', id=post.id)  
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', id=post.id)
    else:
        form = PostForm(instance=post)
    context = {
        'form': form,
        'post': post,
    }
    return render(request, 'blog/create.html', context)

@login_required(login_url='/auth/login/')
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('blog:post_detail', id=post.id)
    if request.method == 'POST':
        post.delete()
        return redirect('blog:index')
    context = {
        'post': post,
    }
    return render(request, 'blog/delete_confirmation.html', context)

@login_required(login_url='/auth/login/')
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
    return redirect('blog:post_detail', id=post.id)

@login_required(login_url='/auth/login/')
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, post_id=post_id)
    if request.user != comment.author:
        return redirect('blog:post_detail', id=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', id=post_id)
    else:
        form = CommentForm(instance=comment)
    return render(request, 'blog/comment_form.html', {'form': form, 'comment': comment})

@login_required(login_url='/auth/login/')
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, post_id=post_id)
    if request.user != comment.author:
        return redirect('blog:post_detail', id=post_id)
    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', id=post_id)
    return render(request, 'blog/comment_confirm_delete.html', {'comment': comment})


class UserUpdateView(LoginRequiredMixin, UpdateView):
    """
    Представление для редактирования профиля пользователя.
    Доступно только авторизованному пользователю.
    """
    model = User
    form_class = ProfileEditForm
    template_name = 'registration/profile_edit.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy('profile', kwargs={'username': self.request.user.username})