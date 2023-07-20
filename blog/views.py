from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Post, Comment, Hashtag, Reply
from .forms import Postform, CommentForm, HashtagForm, ReplyForm
# Create your views here.


class PostWrite(LoginRequiredMixin, View):
    def get(self, request):
        form = Postform()
        context = {
            'form': form,
        }
        return render(request, 'blog/post_form.html', context)

    def post(self, request):
        form = Postform(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect('blog:list')
        context = {
            'form': form
        }
        return render(request, 'blog/post_form.html', context)


class PostList(View):
    def get(self, request):
        posts = Post.objects.all()
        context = {
            'posts': posts
        }
        return render(request, 'blog/post_list.html', context)


class PostDetail(View):
    def get(self, request, pk):
        post = Post.objects.prefetch_related(
            'comment_set', 'hashtag_set').get(pk=pk)
        comments = post.comment_set.all()
        hashtags = post.hashtag_set.all()

        comment_form = CommentForm()
        hashtag_form = HashtagForm()
        reply_form = ReplyForm()
        context = {
            'post': post,
            'comments': comments,
            'hashtags': hashtags,
            'comment_form': comment_form,
            'hashtag_form': hashtag_form,
            'reply_form': reply_form,
        }
        return render(request, 'blog/post_detail.html', context)


class PostUpdate(LoginRequiredMixin, View):
    def get(self, request, pk):
        post = Post.objects.get(pk=pk)
        form = Postform(initial={'title': post.title, 'content': post.content})
        context = {
            'form': form,
            'post': post
        }
        return render(request, 'blog/post_edit.html', context)

    def post(self, request, pk):
        post = Post.objects.get(pk=pk)
        form = Postform(request.POST)
        if form.is_valid():
            post.title = form.cleaned_data['title']
            post.content = form.cleaned_data['content']
            post.save()
            return redirect('blog:detail', pk=pk)
        context = {
            'form': form
        }
        return render(request, 'blog/post_edit.html', context)


class PostDelete(LoginRequiredMixin, View):
    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        post.delete()
        return redirect('blog:list')


class CommentWrite(LoginRequiredMixin, View):
    def post(self, request, post_id):
        form = CommentForm(request.POST)
        post = Post.objects.prefetch_related(
            'comment_set', 'hashtag_set').get(pk=post_id)
        if form.is_valid():
            content = form.cleaned_data['content']
            user = request.user
            comment = Comment.objects.create(
                post=post, content=content, user=user)
            return redirect('blog:detail', pk=post_id)
        hashtag_form = HashtagForm()
        context = {
            'post': post,
            'comments': post.comment_set.all(),
            'hashtags': post.hashtag_set.all(),
            'comment_form': form,
            'hashtag_form': hashtag_form,
        }
        return render(request, 'blog/post_detail.html', context)


class CommentDelete(LoginRequiredMixin, View):
    def post(self, request, comment_id):
        comment = get_object_or_404(Comment, pk=comment_id)
        post_id = comment.post.id
        comment.delete()
        return redirect('blog:detail', pk=post_id)


class HashtagWrite(LoginRequiredMixin, View):
    def post(self, request, post_id):
        form = HashtagForm(request.POST)
        post = Post.objects.prefetch_related(
            'comment_set', 'hashtag_set').get(pk=post_id)
        if form.is_valid():
            name = form.cleaned_data['name']
            hashtag = Hashtag.objects.create(post=post, name=name)
            return redirect('blog:detail', pk=post_id)
        comment_form = CommentForm()
        context = {
            'post': post,
            'comments': post.comment_set.all(),
            'hashtags': post.hashtag_set.all(),
            'comment_form': comment_form,
            'hashtag_form': form,
        }
        return render(request, 'blog/post_detail.html', context)


class HashtagDelete(View):
    def post(self, request, hashtag_id):
        hashtag = get_object_or_404(Hashtag, pk=hashtag_id)
        post_id = hashtag.post.id
        hashtag.delete()
        return redirect('blog:detail', pk=post_id)


class PostSearch(View):
    def get(self, request, tag):
        print(f'request.GET: {request.GET}')
        posts = Post.objects.prefetch_related(
            'hashtag_set').filter(hashtag__name=tag).order_by('-created_at')
        print(f'tag: {tag}')
        context = {
            'posts': posts,
        }
        return render(request, 'blog/post_list.html', context)


class ReplyWrite(View):
    def post(self, request, comment_id):
        form = ReplyForm(request.POST)
        parent = Comment.objects.get(pk=comment_id)
        post_id = parent.post.id
        if form.is_valid():
            content = form.cleaned_data['content']
            user = request.user
            children = Reply.objects.create(
                parent=parent, content=content, user=user)
            return redirect('blog:detail', pk=post_id)


class ReplyDelete(View):
    def post(self, request, reply_id):
        reply = get_object_or_404(Reply, pk=reply_id)
        post_id = reply.parent.post.id
        reply.delete()
        return redirect('blog:detail', pk=post_id)
