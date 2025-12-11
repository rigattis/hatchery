from django.core.management.base import BaseCommand
from cmr.models import Schedule
from datetime import date, time


class Command(BaseCommand):
    help = 'Create a schedule from 8/25/25 to 12/5/25, weekdays from 12pm to 10pm'

    def handle(self, *args, **options):
        # Create the schedule
        schedule = Schedule.objects.create(
            name="Fall 2025 Schedule",
            start_date=date(2025, 8, 25),
            end_date=date(2025, 12, 5),
            open_time=time(12, 0),  # 12:00 PM
            close_time=time(22, 0),  # 10:00 PM
            days_of_week="Monday,Tuesday,Wednesday,Thursday,Friday",
            location="Hatchery",
            holidays="11-27-25",  # Thanksgiving
            is_active=True
        )

        # Set this as the active schedule
        schedule.set_as_active()

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created schedule: {schedule.name}\n'
                f'  Period: {schedule.start_date} to {schedule.end_date}\n'
                f'  Hours: {schedule.open_time.strftime("%I:%M %p")} - {schedule.close_time.strftime("%I:%M %p")}\n'
                f'  Days: Weekdays (Monday-Friday)\n'
                f'  Status: Active'
            )
        )
