# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.http import require_POST
from django.db.models import Count, Q

from taggit.models import Tag

from .models import Post, Comment, Category
from .forms import EmailPostForm, CommentForm

# -------------------------------------
# Home – Startseite
# -------------------------------------
def home(request):
    latest_posts = Post.published.select_related('category')[:6]
    categories = Category.objects.all()
    return render(request, 'blog/home.html', {
        'latest_posts': latest_posts,
        'categories': categories,
    })


# -------------------------------------
# Alle Posts (+ optional Tag-Filter)
# -------------------------------------
def post_list(request, tag_slug=None):
    post_list_qs = Post.published.select_related('category')
    tag = None
    categories = Category.objects.all()

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        post_list_qs = post_list_qs.filter(tags__in=[tag])

    paginator = Paginator(post_list_qs, 9)
    page_number = request.GET.get('page', 1)
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    return render(request, 'blog/post_list.html', {
        'posts': posts,
        'tag': tag,
        'categories': categories,
    })


# -------------------------------------
# Posts nach Kategorie (per category_id)
# -------------------------------------
def category_list(request, category_id=None):
    category = None
    posts_qs = Post.published.select_related('category')
    categories = Category.objects.all()

    if category_id:
        category = get_object_or_404(Category, id=category_id)
        posts_qs = posts_qs.filter(category=category)

    paginator = Paginator(posts_qs, 9)
    page_number = request.GET.get('page', 1)
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    return render(request, 'blog/category_list.html', {
        'category': category,
        'posts': posts,
        'categories': categories,
    })


# -------------------------------------
# Post-Detail
# -------------------------------------
def post_detail(request, year, month, day, post):
    post = get_object_or_404(
        Post.objects.select_related('category'),
        status=Post.Status.PUBLISHED,
        slug=post,
        publish__year=year,
        publish__month=month,
        publish__day=day,
    )

    comments = post.comments.filter(active=True)
    form = CommentForm()
    categories = Category.objects.all()

    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = (
        Post.published
        .filter(tags__in=post_tags_ids)
        .exclude(id=post.id)
        .annotate(same_tags=Count('tags'))
        .order_by('-same_tags', '-publish')[:4]
        .select_related('category')
    )

    return render(request, 'blog/post_detail.html', {
        'post': post,
        'comments': comments,
        'form': form,
        'similar_posts': similar_posts,
        'categories': categories,
    })


# -------------------------------------
# Post per E-Mail teilen
# -------------------------------------
def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    sent = False
    categories = Category.objects.all()

    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recommends you read {post.title}"
            message = (
                f"Read {post.title} at {post_url}\n\n"
                f"{cd['name']}'s comments: {cd.get('comments', '')}"
            )
            from django.core.mail import send_mail
            send_mail(subject, message, 'your_account@gmail.com', [cd['to']])
            sent = True
    else:
        form = EmailPostForm()

    return render(request, 'blog/post_share.html', {
        'post': post,
        'form': form,
        'sent': sent,
        'categories': categories,
    })


# -------------------------------------
# Kommentar erstellen
# -------------------------------------
@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    comment = None
    form = CommentForm(data=request.POST)
    categories = Category.objects.all()

    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.save()

    return render(request, 'blog/post_comment.html', {
        'post': post,
        'form': form,
        'comment': comment,
        'categories': categories,
    })


# -------------------------------------
# Suche (GET)
# -------------------------------------
def post_search(request):
    query = (request.GET.get("query") or "").strip()
    categories = Category.objects.all()

    results_qs = Post.published.none()
    if query:
        results_qs = (
            Post.published.filter(
                Q(title__icontains=query)
                | Q(body__icontains=query)
                | Q(category__name__icontains=query)
                | Q(tags__name__icontains=query)
            )
            .select_related("category")
            .prefetch_related("tags")
            .distinct()
            .order_by("-publish")
        )

    paginator = Paginator(results_qs, 9)
    page_number = request.GET.get("page", 1)
    try:
        results = paginator.page(page_number)
    except PageNotAnInteger:
        results = paginator.page(1)
    except EmptyPage:
        results = paginator.page(paginator.num_pages)

    return render(
        request,
        "blog/search_results.html",
        {"query": query, "results": results, "categories": categories},
    )