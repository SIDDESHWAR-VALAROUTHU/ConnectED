from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.conf import settings
from django.db import models


from .models import PrivacySettings, Notification, Connection
from accounts.models import Post, Comment, Like  # adjust app names if needed
from jobs.models import Job

User = get_user_model()


# ⚙️ 1️⃣ Auto-create privacy settings for new users
@receiver(post_save, sender=User)
def create_privacy_settings(sender, instance, created, **kwargs):
    if created:
        PrivacySettings.objects.create(user=instance)

@receiver(post_save, sender=Connection)
def notify_on_connection(sender, instance, created, **kwargs):
    if created and instance.status == 'pending':
        # Notify receiver about new connection request
        Notification.objects.create(
            user=instance.to_user,
            from_user=instance.from_user,
            message=f"{instance.from_user.username} sent you a connection request.",
            timestamp=timezone.now(),
        )
    elif instance.status == 'accepted':
        # Notify both users about successful connection
        Notification.objects.create(
            user=instance.from_user,
            from_user=instance.to_user,
            message=f"{instance.to_user.username} accepted your connection request.",
            timestamp=timezone.now(),
        )
        Notification.objects.create(
            user=instance.to_user,
            from_user=instance.from_user,
            message=f"You are now connected with {instance.from_user.username}.",
            timestamp=timezone.now(),
        )


# 🟣 When someone likes or comments on a post
@receiver(post_save, sender=Comment)
def notify_on_comment(sender, instance, created, **kwargs):
    if created and instance.post.author != instance.user:
        Notification.objects.create(
            user=instance.post.author,
            from_user=instance.user,
            message=f"{instance.user.username} commented on your post.",
            timestamp=timezone.now(),
        )


@receiver(post_save, sender=Post)
def notify_on_post(sender, instance, created, **kwargs):
    if created:
        # Notify all connected users when user creates a new post
        connections = Connection.objects.filter(
            status='accepted'
        ).filter(
            models.Q(from_user=instance.author) | models.Q(to_user=instance.author)
        )

        for conn in connections:
            connected_user = conn.to_user if conn.from_user == instance.author else conn.from_user
            Notification.objects.create(
                user=connected_user,
                from_user=instance.author,
                message=f"{instance.author.username} posted a new update.",
                timestamp=timezone.now(),
            )


# 🟡 When a new job is posted
@receiver(post_save, sender=Job)
def notify_all_users_on_new_job(sender, instance, created, **kwargs):
    if created:
        # Notify all users except the job author
        all_users = User.objects.exclude(id=instance.author.id)
        for user in all_users:
            Notification.objects.create(
                user=user,
                from_user=instance.author,
                message=f"{instance.author.username} posted a new job: {instance.title}.",
                timestamp=timezone.now(),
            )

@receiver(post_save, sender=Like)
def notify_on_post_like(sender, instance, created, **kwargs):
    """Notify the post author when someone likes their post."""
    if created:
        post = instance.post
        liker = instance.user
        author = post.author

        if liker != author:  # avoid self-like notifications
            post_title = post.title if hasattr(post, 'title') and post.title else post.content[:30]
            Notification.objects.create(
                user=author,
                message=f"{liker.username} liked your post '{post_title}'.",
                timestamp=timezone.now()
            )