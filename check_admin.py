
import os
import django
import sys

# Setup Django environment
sys.path.append(r'c:\Users\admin\Documents\python pro\animal_rescue\animal')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'animal.settings')
django.setup()

from myapp.models import Login

try:
    user = Login.objects.get(username='admin')
    print(f"User 'admin' found.")
    print(f"User type: {user.usertype}")
    print(f"Is active: {user.is_active}")
    print(f"Is superuser: {user.is_superuser}")
    print(f"Check password 'admin': {user.check_password('admin')}")
except Login.DoesNotExist:
    print("User 'admin' does not exist.")
