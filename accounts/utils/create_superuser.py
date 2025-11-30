from django.contrib.auth import get_user_model

def create_superuser():
    User = get_user_model()
    if not User.objects.filter(username="admin").exists():
        User.objects.create_superuser(
            uid="admin1",
            email="sidhusiddeshwar01@gmail.com",
            password="Admin@123"
        )
        print("Superuser created!")
