from django.core.management.base import BaseCommand
from cmr.models import (
    Space, Machine, Trainer, Reservation, Schedule,
    HelpTicket, Contact, Project, Event
)


class Command(BaseCommand):
    help = 'Clear all data from the database (except users)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm you want to delete all data',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING(
                    'This command will delete ALL data (except users) from the database.\n'
                    'To proceed, run: python manage.py clear_data --confirm'
                )
            )
            return

        self.stdout.write(self.style.WARNING('Starting data deletion...'))

        # Delete all data in order (respecting foreign key constraints)
        models_to_clear = [
            ('Reservations', Reservation),
            ('Help Tickets', HelpTicket),
            ('Trainers', Trainer),
            ('Machines', Machine),
            ('Spaces', Space),
            ('Schedules', Schedule),
            ('Contacts', Contact),
            ('Projects', Project),
            ('Events', Event),
        ]

        total_deleted = 0
        for name, model in models_to_clear:
            count = model.objects.count()
            if count > 0:
                model.objects.all().delete()
                self.stdout.write(
                    self.style.SUCCESS(f'Deleted {count} {name}')
                )
                total_deleted += count
            else:
                self.stdout.write(
                    self.style.WARNING(f'No {name} to delete')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nSuccessfully deleted {total_deleted} total records!'
            )
        )
        self.stdout.write(
            self.style.SUCCESS('User data preserved.')
        )
