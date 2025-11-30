from accounts.models import CustomUser as User

def create_superuser():
    if not User.objects.filter(username="admin").exists():
        User.objects.create_superuser(
            uid="admin1",
            username="admin1",
            email="sidhusiddeshwar01@gmail.com",
            password="Admin@123"
        )
        print("Superuser created!")
