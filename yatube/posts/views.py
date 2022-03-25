from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User

POSTS_ON_PAGE = 10


def get_page_context(queryset, request):
    paginator = Paginator(queryset, POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return {
        'page_obj': page_obj,
    }


def index(request):
    keyword = request.GET.get("q")
    if keyword:
        posts = (
            Post.objects.select_related('author', 'group')
            .filter(text__contains=keyword)
        )
    else:
        posts = Post.objects.all()
    context = {
        'posts': posts,
        'keyword': keyword
    }
    context.update(get_page_context(posts, request))
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    context = {
        'group': group,
        'posts': posts,
    }
    context.update(get_page_context(posts, request))
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=author)
    following = author.following.filter(
        user=request.user.is_authenticated
    ).exists()
    context = {
        'posts': posts,
        'author': author,
        'following': following
    }
    context.update(get_page_context(posts, request))
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = Post.objects.get(id=post_id)
    form = CommentForm()
    comments = post.comments.all()
    author = post.author
    this_user = request.user
    context = {
        'post': post,
        'author': author,
        'this_user': this_user,
        'form': form,
        'comments': comments
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if form.is_valid():
        new_post = form.save(commit=False)
        new_post.author = request.user
        new_post.save()
        return redirect('posts:profile', request.user.username)
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = Post.objects.get(id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    author = post.author.username
    if author != request.user.username:
        return redirect('posts:post_detail', post.id)
    if form.is_valid():
        post.text = form.cleaned_data['text']
        post.save()
        return redirect('posts:post_detail', post.id)
    return render(request,
                  'posts/create_post.html',
                  {'form': form, 'is_edit': True, 'post': post})


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def post_delete(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    author = post.author.username
    if author != request.user.username:
        return redirect('posts:post_detail', post.id)
    post.delete()
    return redirect('posts:profile', request.user.username)


@login_required
def follow_index(request):
    authors_id = request.user.follower.all().values_list('author', flat=True)
    posts = Post.objects.filter(author_id__in=authors_id)
    context = {'posts': posts}
    context.update(get_page_context(posts, request))
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    user_name = User.objects.get(username=username)
    if not (Follow.objects.filter(
            user=request.user,
            author=user_name).exists() or username == request.user.username):
        user_name = User.objects.get(username=username)
        new_subscribe = Follow.objects.create(
            author=user_name,
            user=request.user
        )
        new_subscribe.save()
        return redirect('posts:profile', request.user.username)
    return redirect('posts:profile', request.user.username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=author).delete()
    return redirect('posts:profile', request.user.username)
