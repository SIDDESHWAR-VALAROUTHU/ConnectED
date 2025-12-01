# accounts/models.py
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.validators import RegexValidator
from django.conf import settings
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    def create_user(self, uid, email, username, password=None, **extra_fields):
        if not uid:
            raise ValueError("The UID field must be set")
        if not email:
            raise ValueError("The Email field must be set")

        email = self.normalize_email(email)
        user = self.model(uid=uid, email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, uid, email, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(uid, email, username, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    uid = models.CharField(max_length=20, unique=True)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    department = models.CharField(max_length=50, blank=True, null=True)
    batch = models.CharField(max_length=20, blank=True, null=True)
    location = models.CharField(max_length=50, blank=True, null=True)

    ROLE_CHOICES = (
        ('student', 'Student'),
        ('alumni', 'Alumni'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')

    contact_number = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r'^\d{10}$',
                message="Contact number must be exactly 10 digits.",
                code='invalid_number'
            )
        ]
    )
    '''
    profile_pic = models.URLField(max_length=500, blank=True, null=True)
    cover_pic = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        default="https://res.cloudinary.com/YOUR_CLOUD_NAME/image/upload/v123456/default_cover.jpg"
    )
    '''
    #modified these two line to store images in render
    profile_pic = models.BinaryField(null=True, blank=True)
    cover_pic = models.BinaryField(null=True, blank=True)

    about = models.TextField(blank=True, null=True)
    current_designation = models.CharField(max_length=100, blank=True, null=True)
    company = models.CharField(max_length=100, blank=True, null=True)

    linkedin = models.URLField(blank=True, null=True)
    github = models.URLField(blank=True, null=True)
    portfolio = models.URLField(blank=True, null=True)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'uid'  # login field
    REQUIRED_FIELDS = ['email', 'username', 'department', 'role']

    objects = CustomUserManager()

    def __str__(self):
        return self.username


class Project(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=200)
    description = models.TextField()
    link = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.user.username})"


class Experience(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="experiences")
    title = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)


    def __str__(self):
        return f"{self.title} at {self.company}"


class Achievement(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='achievements')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.title} ({self.user.username})"




class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='posts/', blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    

    def __str__(self):
        return self.title

    @property
    def like_count(self):
        return self.likes.count()

    @property
    def comment_count(self):
        return self.comments.count()


class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')

    def __str__(self):
        return f"{self.user.username} liked {self.post.title}"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} commented on {self.post.title}"


class PostView(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')

    def __str__(self):
        return f"{self.user.username} viewed {self.post.title}"



class Connection(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_requests'
    )
    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_requests'
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_user', 'to_user')  # Prevent duplicates

    def __str__(self):
        return f"{self.from_user.username} → {self.to_user.username} ({self.status})"


class PrivacySettings(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='privacy')

    show_experience = models.BooleanField(default=True)
    show_projects = models.BooleanField(default=True)
    show_achievements = models.BooleanField(default=True)
    show_posts = models.BooleanField(default=True)
    show_contact_info = models.BooleanField(default=True)
    show_connections = models.BooleanField(default=True) 
    
    def __str__(self):
        return f"Privacy settings for {self.user.username}"



class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='sent_notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(default=timezone.now)
    notification_type = models.CharField(max_length=50, default='general')  # e.g., 'connection', 'post', etc.
    connection = models.ForeignKey('Connection', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"Notification to {self.user.username} - {self.message[:20]}"