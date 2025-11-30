import os
import django
import json
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'college_connect_demo.settings')
django.setup()

from accounts.models import CustomUser

with open('accounts.json') as f:
    data = json.load(f)

for item in data:
    fields = item['fields']
    user_id = item['pk']
    # Check if user already exists
    if not CustomUser.objects.filter(pk=user_id).exists():
        CustomUser.objects.create(**fields)

print("Users loaded successfully")
