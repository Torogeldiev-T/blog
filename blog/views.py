from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .models import Post, Comment
from django.views.generic import ListView
from .forms import EmailPostForm, CommentPostForm
from django.core.mail import send_mail
from taggit.models import Tag
from django.db.models import Count


def post_list(request, tag_slug=None):
    object_list = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])
    paginator = Paginator(object_list, 3)  # 3 posts in each page
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer deliver the first page
        posts = paginator.page(1)
    except EmptyPage:
        # If page is out of range deliver last page of results
        posts = paginator.page(paginator.num_pages)
    return render(request, 'blog/post/list.html', {'page': page, 'posts': posts, 'tag': tag})


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post, status='published', publish__year=year, publish__month=month,
                             publish__day=day)
    tags_in_post_ids = post.tags.values_list('id', flat=True)[:10]
    similar_posts = Post.published.filter(tags__in=tags_in_post_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]
    if request.method == 'POST':
        form = CommentPostForm(data=request.POST)
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.post = post
            new_comment.save()
            return render(request, 'blog/post/detail.html', {'post': post,
                                                             'comments': post.comments.filter(opened=True),
                                                             'form': form,
                                                             'similar_posts': similar_posts})
    else:
        form = CommentPostForm()
        return render(request, 'blog/post/detail.html', {'post': post, 'comments': post.comments.filter(opened=True),
                                                         'form': form, 'similar_posts': similar_posts})


def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False
    if request.method == 'POST':
        # Form was submitted
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Form fields passed validation
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(
                post.get_absolute_url())
            subject = f"{cd['name']} recommends you read " \
                      f"{post.title}"
            message = f"Read {post.title} at {post_url}\n\n" \
                      f"{cd['name']}\'s comments: {cd['comments']}"
            send_mail(subject, message, 'torogeldiev_t@auca.kg',
                      [cd['to']])
            sent = True
    # ... send email
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post,
                                                    'form': form,
                                                    'sent': sent})


def comment_post(request, post_id):
    created = False
    if request.method == 'POST':
        form = CommentPostForm(data=request.POST)
        if form.is_valid():

            data = form.cleaned_data
            name = data['username']
            body = data['body']
            email = data['email']
            post = Post.published.get(pk=post_id)
            obj = Comment.objects.create(post=post, username=name, body=body, email=email)
            obj.save()
            if obj is not None:
                return render(request, r'blog\post\detail.html', {'post': post})
    else:
        form = CommentPostForm()
        return render(request, r'blog\comment\comment_post.html', {'form': form,
                                                                   })


class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'
