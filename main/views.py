from django.shortcuts import render ,redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
from .forms import SimpleCaptchaForm
from django.contrib.auth.decorators import login_required
from allauth.socialaccount.models import SocialAccount
import random, string
from .models import User,Post,PostReaction,Comment,Bookmark,CommentReaction
from django.contrib.auth.hashers import make_password, check_password
import hashlib,json 
from django.db import IntegrityError, transaction



def generate_Otp():
    return str(random.randint(1000,9999))

def usenameGenerator():
    random_digits = ''.join(random.choices(string.digits, k=3))
    random_letters = ''.join(random.choices(string.ascii_letters, k=3))

    while User.objects.filter(username=f"Anon{random_digits}{random_letters}").exists():
        random_digits = ''.join(random.choices(string.digits, k=3))
        random_letters = ''.join(random.choices(string.ascii_letters, k=3))

    username = f"Anon{random_digits}{random_letters}"
    return username


def send_Email(email,subject,message):
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list,fail_silently=False)



def index(request):
    try:
        username = request.session['username']
        print(username)
    except KeyError:
        username = None
    
    if(username!=None):
        #latest first

        posts = Post.objects.all().order_by('-created_at')
    else:
        posts = Post.objects.values('id','title', 'description', 'upvotes', 'downvotes')

    return render(request, 'index.html', {'posts': posts, 'username': username})


@csrf_exempt
def register(request):
    if request.method == 'GET':
        captchaForm = SimpleCaptchaForm()
        template = loader.get_template('Register.html')
        return render(request, 'Register.html', {'captchaForm': captchaForm})
    elif request.method == 'POST':
        captchaForm = SimpleCaptchaForm(request.POST)
        if captchaForm.is_valid():
            print("Valid Captcha")    
            email = request.POST['email']
            
            if User.objects.filter(email=hashlib.sha256(email.encode('utf-8')).hexdigest()).exists():
                return HttpResponse("Email Already Exists")

            otp = generate_Otp()
            print(otp)
            subject = "Your OTP Verfification Code"
            message = f"Your OTP is {otp}"
            send_Email(email,subject,message)

            request.session['email'] = email
            request.session['otp'] = otp
            template = loader.get_template('otpVerify.html')
            return HttpResponse(template.render())
        else:
            return HttpResponse("Invalid Captcha")



@csrf_exempt
def otpVerify(request):
    if request.method == 'POST'or request.method == 'GET':
        req_method = request.method
        otp = request.POST['otp']
        print(otp)
        if otp == request.session['otp']:
            username = usenameGenerator()
            request.session['username'] = username
            subject = "OTP Verification Successful"
            message = f"Welcome {username}"
            email = request.session['email']
            send_Email(email,subject,message)
            return redirect('createPassword')
        else:
            return HttpResponse("OTP is InValid")
    return HttpResponse(f"Your OTP is {request.session['otp']}")


@csrf_exempt
def createPassword(request):
    
    if request.method == 'POST':
        password = request.POST['password']
        confirmpassword = request.POST['confirmpassword']
        if password == confirmpassword:
            username = request.session['username']
            email = request.session['email']
            hashed_email = hashlib.sha256(email.encode('utf-8')).hexdigest()
            hased_password = make_password(password)
            user = User(email=hashed_email,username=username,password=hased_password)
            user.save()
            print(username)
            

            return redirect('index')
        else:
            return HttpResponse("Password is Invalid")
    
    if request.method == 'GET':
        # context = {username: request.session['username']}
        return render(request, 'createPass.html', {"username": request.session['username']})
    


@csrf_exempt
def oauth_Verification(request):
    if request.method == 'GET':
        socialAcc = SocialAccount.objects.filter(user=request.user,provider='google').first()
        email = socialAcc.extra_data['email']
        if User.objects.filter(email=hashlib.sha256(email.encode('utf-8')).hexdigest()).exists():
            return HttpResponse("Email Already Exists")
        print(email)
        otp = generate_Otp()
        subject = "Your OTP Verfification Code"
        message = f"Your OTP is {otp}"
        send_Email(email,subject,message)
        request.session['email'] = email
        request.session['otp'] = otp

        captchaform = SimpleCaptchaForm()
        return render(request, 'oauth_Verification.html', {'captchaForm': captchaform})

    elif request.method == 'POST':
        print("POST")
        captchaform = SimpleCaptchaForm(request.POST)
        print(captchaform.is_valid())
        if captchaform.is_valid():
            if request.session['otp'] == request.POST['otp']:
                username = usenameGenerator()
                request.session['username'] = username
                subject = "OTP Verification Successful"
                message = f"Welcome {username}"
                email = request.session['email']
                send_Email(email,subject,message)
                return redirect('createPassword')
            else:
                return HttpResponse("OTP is InValid")
           
        else:
            print("Captcha is Invalid")
            return HttpResponse("Captcha is Invalid")
            

@csrf_exempt
def login(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = User.objects.filter(email=hashlib.sha256(email.encode('utf-8')).hexdigest()).first()
        if user:
            if check_password(password,user.password):
                request.session['username'] = user.username
                return redirect('index')
            else:
                return HttpResponse("Password is Invalid")
        else:
            return HttpResponse("Email is Invalid")
        



def add_post(request):
    if not request.session.get('username'):
        return redirect('login')
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        media = request.FILES.get('media')
        sensitive_content = request.POST.get('sensitive_content') == 'on'
        author = request.session['username']

        if not title or not description:
            return HttpResponse("Title and Description are required fields", status=400)

        post = Post.objects.create(
            title=title,
            description=description,
            media=media,
            sensitive_content=sensitive_content,
            author=User.objects.get(username=author)
        )
        post.save()
        return redirect('index')  

    return render(request, 'addpost.html', {'username': request.session['username']})

@csrf_exempt
def like_post(request, post_id):
    if not request.session.get('username'):  
        return JsonResponse({'success': False, 'error': 'User not logged in'})
    
    if request.method == 'POST':
        try:
            user = User.objects.get(username=request.session['username'])
            post = get_object_or_404(Post, id=post_id)

            with transaction.atomic():
                post_reaction, created = PostReaction.objects.select_for_update().get_or_create(
                    user=user,
                    post=post
                )

                if not created and post_reaction.reaction_type == 'upvote':
                    return JsonResponse({'success': False, 'error': 'You have already liked this post'})

                if post_reaction.reaction_type == 'downvote':
                    post_reaction.reaction_type = 'upvote'
                    post.downvotes -= 1
                    post.upvotes += 1
                else:
                    post_reaction.reaction_type = 'upvote'
                    post.upvotes += 1

                post_reaction.save()
                post.save()

            return JsonResponse({'success': True, 'likes': post.upvotes, 'dislikes': post.downvotes})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@csrf_exempt
def dislike_post(request, post_id):
    if not request.session.get('username'):  
        return JsonResponse({'success': False, 'error': 'User not logged in'})
    
    if request.method == 'POST':
        try:
            user = User.objects.get(username=request.session['username'])
            post = get_object_or_404(Post, id=post_id)

            with transaction.atomic():
                post_reaction, created = PostReaction.objects.select_for_update().get_or_create(
                    user=user,
                    post=post
                )

                if not created and post_reaction.reaction_type == 'downvote':
                    return JsonResponse({'success': False, 'error': 'You have already disliked this post'})

                if post_reaction.reaction_type == 'upvote':
                    post_reaction.reaction_type = 'downvote'
                    post.upvotes -= 1
                    post.downvotes += 1
                else:
                    post_reaction.reaction_type = 'downvote'
                    post.downvotes += 1

                post_reaction.save()
                post.save()

            return JsonResponse({'success': True, 'likes': post.upvotes, 'dislikes': post.downvotes})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def post_detail(request, post_id):
    if request.session.get('username'): 
        post = Post.objects.get(id=post_id)
        comments = Comment.objects.filter(post=post).order_by('-created_at')
        username = request.session['username']
        print(username)
        
        return render(request, 'post_detail.html', {'post': post,'username': username})
    else:
        return redirect('login')


def logout(request):

    request.session.flush()
    return redirect('add_post')


def search_suggestions(request):
    query = request.GET.get('q', '')
    if not query:
        return JsonResponse({'suggestions': []})
    suggestions = Post.objects.filter(title__icontains=query).values_list('id', 'title')
    print(suggestions)
    return JsonResponse({'suggestions': list(suggestions)})


def trending(request):
    if request.session.get('username'): 
        trending_posts = Post.objects.order_by('-upvotes')[:1]

        return render(request, 'index.html', {'posts': trending_posts, 'username': request.session['username']})
    else:
        return redirect('login')

    

@csrf_exempt
@csrf_exempt  # Disable CSRF for simplicity if testing; ensure CSRF token is passed in production.
def add_comment(request, post_id):
    if not request.session.get('username'):  
        return JsonResponse({'success': False, 'error': 'User not logged in.'}, status=403)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)  # Parse JSON data
            comment_text = data.get('comment', '').strip()
            
            if not comment_text:
                return JsonResponse({'success': False, 'error': 'Comment cannot be empty.'})

            username = User.objects.get(username=request.session['username'])
            post = Post.objects.get(id=post_id)

            # Save the comment
            comment = Comment.objects.create(content=comment_text, author=username, post=post)

            # Return the new comment's data
            return JsonResponse({
                'success': True,
                'comment': {
                    'id': comment.id,
                    'author': comment.author.username,
                    'content': comment.content,
                    'created_at': comment.created_at.strftime('%B %d, %Y'),
                }
            })

        except Post.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Post not found.'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=405)
    


def agree_comment(request, comment_id):
    # print(comment_id)
    # comment = Comment.objects.get(id=comment_id)
    # comment.agreeCount += 1
    # comment.save()
    # return JsonResponse({'success': True, 'agree': comment.agreeCount})

    comment = Comment.objects.get(id=comment_id)
    user = User.objects.get(username=request.session['username'])
    if CommentReaction.objects.filter(user=user, comment=comment).exists():
        if CommentReaction.objects.get(user=user, comment=comment).reaction_type == 'upvote':
            return JsonResponse({'success': False, 'error': 'You have already reacted to this comment'})
        
        if CommentReaction.objects.get(user=user, comment=comment).reaction_type == 'downvote':
            comment.disagreeCount -= 1
            comment.agreeCount += 1
            comment.save()
            CommentReaction.objects.filter(user=user, comment=comment).update(reaction_type='upvote')
    else:
        comment.agreeCount += 1
        comment.save()
        CommentReaction.objects.create(user=user, comment=comment, reaction_type='upvote')
    return JsonResponse({'success': True, 'agree': comment.agreeCount, 'disagree': comment.disagreeCount})
    
def disagree_comment(request, comment_id):
    # comment = Comment.objects.get(id=comment_id)
    # comment.disagreeCount += 1
    # comment.save()
    # return JsonResponse({'success': True, 'disagree': comment.disagreeCount})

    comment = Comment.objects.get(id=comment_id)
    user = User.objects.get(username=request.session['username'])
    if CommentReaction.objects.filter(user=user, comment=comment).exists():
        if CommentReaction.objects.get(user=user, comment=comment).reaction_type == 'downvote':
            return JsonResponse({'success': False, 'error': 'You have already reacted to this comment'})
        
        if CommentReaction.objects.get(user=user, comment=comment).reaction_type == 'upvote':
            comment.agreeCount -= 1
            comment.disagreeCount += 1
            comment.save()
            CommentReaction.objects.filter(user=user, comment=comment).update(reaction_type='downvote')
    else:
        comment.disagreeCount += 1
        comment.save()
        CommentReaction.objects.create(user=user, comment=comment, reaction_type='downvote')
    return JsonResponse({'success': True, 'agree': comment.agreeCount, 'disagree': comment.disagreeCount})

@csrf_exempt
def bookmark_post(request, post_id):
    if not request.session.get('username'):  
        return JsonResponse({'success': False, 'error': 'User not logged in'})
    user = User.objects.get(username=request.session['username'])
    post = Post.objects.get(id=post_id)
    if Bookmark.objects.filter(user=user, post=post).exists():
        return JsonResponse({'success': True, 'message': 'Post already bookmarked'})
    else:
        Bookmark.objects.create(user=user, post=post)
    return JsonResponse({'success': True, 'message': 'Post bookmarked successfully'})

def view_bookmarks(request):
    if not request.session.get('username'):
        return redirect('login')
    user = User.objects.get(username=request.session['username'])
    bookmarks = Bookmark.objects.filter(user=user)
    username = request.session['username']
    #latest first
    bookmarks = bookmarks.order_by('-created_at')
    return render(request, 'bookmarks.html', {'bookmarks': bookmarks, 'username': username})

@csrf_exempt
def remove_bookmark(request, bookmark_id):
    bookmark = Bookmark.objects.get(id=bookmark_id)
    bookmark.delete()
    return JsonResponse({'success': True, 'message': 'Bookmark removed successfully'})

def user_profile(request):
    # if not request.sesssion.get('username'):
    #     return redirect('login')

    user = User.objects.get(username=request.session['username'])
    #trim only date and time
    joined_at = user.joined_at.strftime('%B %d, %Y')
    print(joined_at)
    user_posts = Post.objects.filter(author=user)
    return render(request, 'user_profile.html', {'user': user, 'joined_at': joined_at, 'user_posts': user_posts, 'username': request.session['username']})