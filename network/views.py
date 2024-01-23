from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator
import json

from .models import User, Post, Follow, Like

def remove_like(request, post_id):
    post = Post.objects.get(id=post_id)
    user = User.objects.get(pk=request.user.id)
    like = Like.objects.filter(user=user, post=post)
    like.delete()
    return JsonResponse({"message": "Like deleted"})

def add_like(request, post_id):
    post = Post.objects.get(id=post_id)
    user = User.objects.get(pk=request.user.id)
    newLike = Like(user=user, post=post)
    newLike.save()
    return JsonResponse({"message": "Liked"})


def index(request):
    allPosts = Post.objects.all().order_by('id').reverse()

    paginator = Paginator(allPosts, 10)
    pageNumber = request.GET.get('page')
    posts_of_page = paginator.get_page(pageNumber)

    allLikes = Like.objects.all()

    whoYouLiked = []

    try:
        for like in allLikes:
            if like.user.id == request.user.id:
                whoYouLiked.append(like.post.id)
    except:
        whoYouLiked = []

    return render(request, "network/index.html", {
        "allPosts": allPosts,
        "postsOfPage": posts_of_page,
        "whoYouLiked": whoYouLiked
    })

def following(request):
    currentUser = User.objects.get(pk=request.user.id)
    followings = Follow.objects.filter(user_following=currentUser)
    allPosts = Post.objects.all().order_by('id').reverse()
    followingPosts = []

    for post in allPosts:
        for person in followings:
            if person.user_followed == post.user:
                followingPosts.append(post)
    
    paginator = Paginator(followingPosts, 10)
    pageNumber = request.GET.get('page')
    posts_of_page = paginator.get_page(pageNumber)

    return render(request, "network/following.html", {
        "postsOfPage": posts_of_page,
    })

def edit(request, post_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        edit_post = Post.objects.get(id=post_id)
        edit_post.content = data['content']
        edit_post.save()
        return JsonResponse({
            "message": "Change sucessfully",
            "data": data["content"],          
        })

def follow(request):
    userfollow = request.POST['userfollow']
    currentUser = User.objects.get(pk=request.user.id)
    userfollowData = User.objects.get(username=userfollow)
    f = Follow(user_following=currentUser, user_followed=userfollowData)
    f.save()
    user_id = userfollowData.id
    return HttpResponseRedirect(reverse(profile, kwargs={'user_id': user_id}))

def unfollow(request):
    userfollow = request.POST['userfollow']
    currentUser = User.objects.get(pk=request.user.id)
    userfollowData = User.objects.get(username=userfollow)
    f = Follow.objects.get(user_following=currentUser, user_followed=userfollowData)
    f.delete()
    user_id = userfollowData.id
    return HttpResponseRedirect(reverse(profile, kwargs={'user_id': user_id}))
    return


def profile(request, user_id):
    user = User.objects.get(pk=user_id)
    userPosts = Post.objects.filter(user=user).order_by('id').reverse()

    following = Follow.objects.filter(user_following=user)
    followers = Follow.objects.filter(user_followed=user)


    try:
        checkFollow = followers.filter(user_following=User.objects.get(pk=request.user.id))
        if len(checkFollow) > 0:
            isFollowing = True
        else:
            isFollowing = False
    except:
        isFollowing = False

    paginator = Paginator(userPosts, 10)
    pageNumber = request.GET.get('page')
    posts_of_page = paginator.get_page(pageNumber)

    return render(request, "network/profile.html", {
        "userPosts": userPosts,
        "postsOfPage": posts_of_page,
        "username": user.username,
        "followers": followers,
        "following": following,
        "isFollowing": isFollowing,
        "user_profile": user,
    })

def newPost(request):
    if request.method == 'POST':
        content = request.POST['content']
        user = User.objects.get(pk=request.user.id)
        post = Post(content=content, user=user)
        post.save()
        return HttpResponseRedirect(reverse(index))


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
