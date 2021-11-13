import json
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.utils.decorators import method_decorator


from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.generic import DetailView, ListView, View, FormView
from django.views.decorators.csrf import csrf_exempt
from django_redis import client
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth import get_user_model, authenticate, login as log_in, logout as log_out
from django.core.mail import send_mail
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import cache_page
from django.core.cache import cache, caches

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.utils.field_mapping import get_url_kwargs

from .models import Profile, Post, Comment, Log, FollowPendingRequests
from .forms import PostForm, ProfileForm, RegisterForm


# Create your views here.

#################  Profile #########################
# @cache_page(60*0.5,key_prefix="all_profile")
class ShowAllProfile(LoginRequiredMixin,ListView):  ##
    login_url = "login"
    model = Profile
    template_name = "profile.html"
    context_object_name = "qs_profile"
    queryset = Profile.objects.all()

    # def get_queryset(self):
    #     queryset = Profile.objects.all().filter(fg__profile_user=self.request.user.id)
    #     return queryset

# redis #TODO use "hashmap" stracture data
@cache_page(60)
def AllProfile(request):  ##
    data = Profile.objects.all().order_by("id")
    return render(request, "profile.html", {"data": data})


class ProfileDetail(LoginRequiredMixin,DetailView):  ####
    login_url = "login"
    model = Profile
    template_name = "profile_detail.html"
    context_object_name = "qs_detail_profile"


class AllProfilePosts(LoginRequiredMixin,ListView):
    login_url = "login"
    model = Post
    template_name = "profile_detail.html"
    context_object_name = "all_posts"
    # queryset = Profile.objects.filter(post_profile=pk)
    extra_context = {"title": "sholagh"}


def all_profile_posts(request, pk):  ##
    qs_detail_profile = Profile.objects.all().get(user=pk)
    queryset = Post.objects.all().filter(post_profile=pk).order_by("-modify_time")

    print(queryset)
    fw_exist = qs_detail_profile.fw.filter(fw__user=request.user.id).exists()
    return render(request, "profile_detail.html",
                  {"posts": queryset, "qs_detail_profile": qs_detail_profile, "fw_exist": fw_exist})

class UpdateProfileView(FormView):  ######
    template_name = "update-profile.html"
    form_class = ProfileForm
    success_url = "home"

    def form_valid(self, form):
        form.post_profile = form.cleaned_data.get(self.request.user)
        print(form)
        form.save()
        return redirect(self.success_url)

###############################  POST ##########################

@login_required(login_url="login")
def post_detail(request, pk, post_id):
    print("hhhhhhhhhhhhhhhhhhhhhh")
    queryset = Post.objects.filter(post_profile__pk=pk, id=post_id).first()
    is_like = queryset.like.exists()
    # caches[request.user.id] =queryset.like.count()
    print(queryset)
    print("issssssssssssssssss likeeeeeeee", is_like)
    return render(request, "post_detail.html", {"qs_detail_post": queryset, "is_like": is_like})


@login_required(login_url="login")
@csrf_exempt
def upload_post(request):  #####
    current_user = request.user
    if request.method == "GET":
        return render(request, "upload-post.html", {"post_form": UploadPostView})

    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid:
            post = form.save()
            post.post_profile = current_user
            post.save()
            return redirect("/")
        else:
            form = PostForm
        return render(request, "upload-post.html", {"form": form})
    return HttpResponse("not valid")


class UploadPostView(FormView):  ######
    template_name = "upload-post.html"
    form_class = PostForm
    success_url = "home"

    def form_valid(self, form):
        form.post_profile = form.cleaned_data.get(self.request.user)
        print(form)
        form.save()
        return redirect(self.success_url)


def uploadost(request):
    if request.method == "GET":
        return render(request,"upload-post.html",{"forms":PostForm})
    if request.method == "POST":

        form = PostForm(request.POST)
        form["post_profile"]=request.user
        if form.is_valid():
            form.save()
            return redirect("home")

    return HttpResponse("TNX")



########################### SEARCH ##################################
def search(request):
    qs = request.GET.get("search-box", None)
    current_user = request.user.id
    print("qssssssssssssssssss", qs)
    user_search_qs = User.objects.filter(username__icontains=qs)
    user_list = [i for i in user_search_qs]
    # for x in user_search_qs:
    #
    fg = Profile.objects.all().filter(user_id=current_user)

    current_Profile = Profile.objects.all().filter(user_id=current_user).only("fg")

    return render(request, "home.html", {"search_answer": user_search_qs,"fg":fg, "cp":current_Profile})


################### FOLLOW ######################
@login_required(login_url="/insta/login")
def do_follow(request, pk):  ###
    # target_user = request.Post.get("user",None)
    current_user = request.user.id
    current_profile = Profile.objects.filter(user_id=current_user).first()
    print(current_user,current_profile)
    print(current_user)
    if current_user:
        target_profile = Profile.objects.filter(id=pk).first()
        target_profile.fw.add(current_user)
        print(target_profile)
        fw_exist = target_profile.fw.exists()
        if fw_exist == False:
            print("OOOOOOOoooooooo")
            target_profile.fw.add(current_user)
            current_profile.fg.add(user_id=pk)
            FollowPendingRequests.objects.create(follow_receiver_id=target_profile,follow_sender_id=current_user)
            return redirect("home")

        elif fw_exist == True:
            print("OOOOOOOoooooooo")

            target_profile.fw.remove(current_user)
            # current_profile.fg.remove(user_id=pk)
            return redirect("home")

        # return redirect("home")
    return HttpResponseRedirect("home")


###################  LIKE ######################
@login_required(login_url="/insta/login")
def like_add_post(request, userpost_id, postid):
    if request.method == "GET":
        current_user = request.user.id
        print("id current_user: ", current_user)
        target_post = Post.objects.get(id=postid)
        like_exist = target_post.like.exists()

        if like_exist == False:
            target_post.like.add(current_user)
            return redirect(f"/insta/post-detail-def/{userpost_id}/{postid}")


        elif like_exist == True:
            target_post.like.remove(current_user)
            return redirect(f"/insta/post-detail-def/{userpost_id}/{postid}")


################### Comment ######################
@login_required(login_url="/insta/login")
def do_comment(request, post_id):  ###
    if request.method == "POST":
        cmnt = request.POST.get("comment", None)
        current_user = request.user.id
        target_user = Post.objects.filter(id=post_id).first()
        print("aaaaaaaaaaaaaaaaaaaaaaa", target_user)
        print("current_user", current_user)

        repeat = Comment.objects.filter(commnet_post=post_id).filter(user=current_user).count()
        count = Comment.objects.filter(commnet_post=post_id).count()

        counter = 0
        getcachkey = cache.get(f"{current_user}:{post_id}")

        if not getcachkey:
            x = Comment.objects.create(commnet_post_id=post_id, user_id=current_user, body=cmnt)
            cache.set(f"{current_user}:{post_id}", counter, 10)
        elif getcachkey == 1:
            x = Comment.objects.create(commnet_post_id=post_id, user_id=current_user, body=cmnt)
            cache.set(f"{current_user}:{post_id}", counter + 1, 10)
            # return redirect(f"/insta/post-detail-def/{userpost_id}/{post_id}")
        else:
            return HttpResponse("bish az had comment dadi")

        print("XXXXXXXXXXXXXXXXXXXX", x)
        print("tttttttttttttttttt", count)
        print("rrrrrrrrrrrrrrrrrrrr", repeat)

        return HttpResponseRedirect("/")


################### USERS ######################
User = get_user_model()


def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email", None)
        username = email
        if email:
            password = request.POST.get('password', None)
            if password:
                user = authenticate(request, email=email, password=password, username=username)
                if user:
                    log_in(request, user)
                    messages.error(request, 'welcome!')
                    if request.GET.get('next_url', None):
                        return redirect(request.GET.get('next_url'))
                    return redirect("/")
                else:
                    return HttpResponse("user pass eshtebah")
        else:
            return HttpResponse("email ro bezar")
    else:
        next_url = request.GET.get('next', "/")
        return render(request, 'login-register.html', {"next_url": next_url})


def logout_view(request):
    log_out(request)
    return redirect('/')


@require_http_methods(["POST"])
def signup(request, account_activation_token=None):
    if request.method == "POST":
        email = request.POST.get("email", None)
        # phone = request.POST.get("phone", None)
        if email:
            if User.objects.filter(email__iexact=email).count() == 0:
                password = request.POST.get('password', None)
                repeated_passweord = request.POST.get('repeat_password', None)
                if password:
                    if password == repeated_passweord:
                        try:
                            user = User.objects.create_user(email=email, password=password, username=email,
                                                            is_active=True, is_staff=True)
                            messages.success(request, "Register Successfully!")
                            return render(request, "login-register.html", {})
                            # return redirect('/')
                        except ValueError as e:
                            # return render(request, "user/error.html", {"message": e})
                            messages.error(request, f"{e}")
                            return redirect('user-view')
                    else:
                        return HttpResponse("pass va tekraresh equal nistan")
            else:
                return HttpResponse("email tekrari")

# class RegisterView(CreateView):
#     template_name = "register.html"
#     form_class = RegisterForm
#     success_url = '/insta/login'
#     http_method_names = ["GET", "POST"]
