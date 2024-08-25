from django.core.management.base import BaseCommand
from core.models import User

class Command(BaseCommand):
    help = 'Creates a superuser.'

    def handle(self, *args, **options):
        # Get the superuser's email and password
        admin_email = 'test@admin.com'
        admin_password = '1234'
        
        # Check if a user with the admin_email exists, and if not, create a superuser
        if not User.objects.filter(email=admin_email).exists():
            User.objects.create_superuser(
                email=admin_email,
                password=admin_password
            )
            print(f'Superuser {admin_email} has been created.')
        else:
            print(f'Superuser {admin_email} already exists.')
