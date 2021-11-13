from django.urls import path

from .views import *

#
urlpatterns = [
##### All Profile #####
    path('all-profile/', ShowAllProfile.as_view(), name="all_profile__class"),
    path('all_profile__def/', AllProfile, name="all_profile__def"),

##### In Profile #####
    path('all-post-profile/<int:pk>', all_profile_posts, name="all_post_profile"),
    path('profile-detail/<int:pk>', ProfileDetail.as_view(), name="profile_detail"),
    path('update-profile/', UpdateProfileView.as_view(), name="update-profile"),
##### Post Detail #####
    # path('post-detail-cls/<int:pk>/<int:post_id>', PostDetail.as_view(), name="post_detail-cls"),
    path('post-detail-def/<int:pk>/<int:post_id>', post_detail, name="post_detail"),
    path("upload/", upload_post, name="upload"),
    path("upload-post-class/", UploadPostView.as_view(), name="upload_cls"),
    path("upload-post-def/", upload_post, name="upload_def"),

##### Search #####
    path("search-def/", search, name="search-def"),

##### In Follow #####
    path('do-follow/<int:pk>', do_follow, name="dofollow"),

##### LIKE #####
    path('like/<int:userpost_id>/<int:postid>', like_add_post, name="like-add-post"),

##### Comment #####
    path('commet/<int:post_id>', do_comment, name="comment"),

##### USER #####
    path('login/', login_view, name='login'),
    path('register/', signup, name='register'),
    path('logout/', logout_view, name='logout'),
]
#
#


# path('register-class/', RegisterView.as_view(), name='register_class'),
