from django.contrib.auth import get_user_model
from django.db import transaction, IntegrityError

User = get_user_model()
try:
    with transaction.atomic():
        user, created = User.objects.get_or_create(
            username='admin',
            defaults={'email': 'admin@example.com', 'is_superuser': True, 'is_staff': True}
        )
        if created:
            user.set_password('admin')
            user.save()
            print(">> Created admin user: admin / admin")
        else:
            print(">> Admin user already exists.")
except IntegrityError:
    print(">> Race condition avoided; user already exists.")
except Exception as e:
    print(f">> Error creating admin user: {e}")
    