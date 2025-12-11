from django.core.management.base import BaseCommand
from cmr.models import Contact


class Command(BaseCommand):
    help = 'Populate the contacts page with 10 generic contacts'

    def handle(self, *args, **options):
        # Clear existing contacts
        Contact.objects.all().delete()
        self.stdout.write(self.style.WARNING('Cleared existing contacts'))

        # Generic contact names
        names = [
            "John Doe",
            "Jane Doe",
            "Jack Doe",
            "Jill Doe",
            "Jake Doe",
            "Joan Doe",
            "Joel Doe",
            "June Doe",
            "Jade Doe"
        ]

        # Create 10 contacts
        for i, name in enumerate(names, start=1):
            contact = Contact.objects.create(
                name=name,
                position="Assistant Manager",
                email=f"hatch{i:02d}@bc.edu",  # Format as hatch01, hatch02, etc.
                phone="(123) 456-7890",
                order=i
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'Created contact: {contact.name} - {contact.email}'
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nSuccessfully created {len(names)} contacts!'
            )
        )
