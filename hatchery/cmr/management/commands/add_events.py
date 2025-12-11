from django.core.management.base import BaseCommand
from cmr.models import Event
from datetime import date, time


class Command(BaseCommand):
    help = 'Populate events with fake upcoming events'

    def handle(self, *args, **options):
        # Clear existing events
        Event.objects.all().delete()
        self.stdout.write(self.style.WARNING('Cleared existing events'))

        # Fake event data
        events_data = [
            {
                "title": "3D Printing Workshop",
                "description": "Learn the basics of 3D printing, from design to finished product. All skill levels welcome!",
                "event_date": date(2025, 12, 10),
                "event_time": time(14, 0),
                "location": "Hatchery - 3rd Floor",
            },
            {
                "title": "Laser Cutting Safety Training",
                "description": "Required safety training for using the laser cutter. Get certified to use this amazing tool!",
                "event_date": date(2025, 12, 15),
                "event_time": time(16, 30),
                "location": "Hatchery - Prototyping Studio",
            },
            {
                "title": "Arduino Basics for Beginners",
                "description": "Introduction to microcontrollers and basic circuits. No prior experience needed.",
                "event_date": date(2025, 12, 18),
                "event_time": time(13, 0),
                "location": "Hatchery - 2nd Floor",
            },
            {
                "title": "CNC Milling Demo",
                "description": "Watch a live demonstration of our CNC mill creating precision parts from metal and wood.",
                "event_date": date(2025, 12, 22),
                "event_time": time(15, 0),
                "location": "Hatchery - Prototyping Shop",
            },
            {
                "title": "Holiday Maker Fair",
                "description": "Showcase your semester projects! Food, demos, and prizes for best projects in various categories.",
                "event_date": date(2025, 12, 20),
                "event_time": time(17, 0),
                "location": "Hatchery - All Floors",
            },
            {
                "title": "Soldering Workshop",
                "description": "Learn proper soldering techniques for electronics projects. Materials provided.",
                "event_date": date(2026, 1, 10),
                "event_time": time(14, 30),
                "location": "Hatchery - 2nd Floor",
            },
            {
                "title": "CAD Design Fundamentals",
                "description": "Introduction to 3D CAD software for mechanical design. Bring your laptop!",
                "event_date": date(2026, 1, 15),
                "event_time": time(13, 30),
                "location": "Hatchery - 3rd Floor",
            },
            {
                "title": "PCB Design Workshop",
                "description": "Learn to design custom printed circuit boards for your electronics projects.",
                "event_date": date(2026, 1, 20),
                "event_time": time(16, 0),
                "location": "Hatchery - 2nd Floor",
            },
        ]

        # Create events
        for i, data in enumerate(events_data, start=1):
            event = Event.objects.create(
                title=data["title"],
                description=data["description"],
                event_date=data["event_date"],
                event_time=data["event_time"],
                location=data["location"],
                order=i
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'Created event: {event.title} on {event.event_date}'
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nSuccessfully created {len(events_data)} events!'
            )
        )
