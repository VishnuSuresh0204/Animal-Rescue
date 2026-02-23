
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
    user.usertype = 'admin'
    user.view_password = 'admin' # Ideally shouldn't store plain text, but keeping consistent with existing bad practice for now
    user.save()
    print("User 'admin' updated successfully. usertype set to 'admin'.")
except Login.DoesNotExist:
    print("User 'admin' does not exist.")
