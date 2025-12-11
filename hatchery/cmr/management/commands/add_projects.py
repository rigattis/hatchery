from django.core.management.base import BaseCommand
from cmr.models import Project
from datetime import date


class Command(BaseCommand):
    help = 'Populate the project showcase with fake projects'

    def handle(self, *args, **options):
        # Clear existing projects
        Project.objects.all().delete()
        self.stdout.write(self.style.WARNING('Cleared existing projects'))

        # Fake project data
        projects_data = [
            {
                "title": "3D Printed Robotic Arm",
                "description": "A fully functional robotic arm with 6 degrees of freedom, designed and printed in the Hatchery.",
                "student_name": "Alex Johnson",
                "date_completed": date(2024, 11, 15),
            },
            {
                "title": "Smart Garden System",
                "description": "An IoT-based automated watering system with sensors for soil moisture and temperature monitoring.",
                "student_name": "Sarah Chen",
                "date_completed": date(2024, 10, 20),
            },
            {
                "title": "Custom Mechanical Keyboard",
                "description": "A hand-wired mechanical keyboard with custom 3D printed keycaps and programmable firmware.",
                "student_name": "Mike Rodriguez",
                "date_completed": date(2024, 9, 5),
            },
            {
                "title": "Laser Cut LED Art Panel",
                "description": "An interactive LED art installation featuring laser-cut acrylic panels with programmable lighting effects.",
                "student_name": "Emily Zhang",
                "date_completed": date(2024, 8, 12),
            },
            {
                "title": "CNC Machined Chess Set",
                "description": "A beautiful chess set with pieces and board machined from various hardwoods using the CNC mill.",
                "student_name": "David Kim",
                "date_completed": date(2024, 7, 30),
            },
            {
                "title": "Arduino Weather Station",
                "description": "A comprehensive weather monitoring station with LCD display and data logging capabilities.",
                "student_name": "Jessica Brown",
                "date_completed": date(2024, 6, 18),
            },
            {
                "title": "3D Printed Prosthetic Hand",
                "description": "An affordable prosthetic hand prototype designed for children, featuring articulated fingers.",
                "student_name": "Ryan Patel",
                "date_completed": date(2024, 5, 25),
            },
            {
                "title": "Custom Guitar Effects Pedal",
                "description": "A handmade guitar distortion pedal with custom circuit design and laser-etched enclosure.",
                "student_name": "Maria Garcia",
                "date_completed": date(2024, 4, 10),
            },
        ]

        # Create projects
        for i, data in enumerate(projects_data, start=1):
            project = Project.objects.create(
                title=data["title"],
                description=data["description"],
                student_name=data["student_name"],
                date_completed=data["date_completed"],
                order=i
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'Created project: {project.title} by {project.student_name}'
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nSuccessfully created {len(projects_data)} projects!'
            )
        )
