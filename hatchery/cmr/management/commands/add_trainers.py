from django.core.management.base import BaseCommand
from cmr.models import Trainer


class Command(BaseCommand):
    help = 'Populate the trainers page with fake trainers'

    def handle(self, *args, **options):
        # Clear existing trainers
        Trainer.objects.all().delete()
        self.stdout.write(self.style.WARNING('Cleared existing trainers'))

        # Fake trainer data
        trainers_data = [
            {
                "name": "Dr. Sarah Mitchell",
                "custom_id": "T-01",
                "major": "Mechanical Engineering",
                "training_certificates": "3D Printing, CNC Mill, Laser Cutting",
            },
            {
                "name": "Prof. James Chen",
                "custom_id": "T-02",
                "major": "Electrical Engineering",
                "training_certificates": "Soldering, PCB Design, Arduino",
            },
            {
                "name": "Emily Rodriguez",
                "custom_id": "T-03",
                "major": "Computer Science",
                "training_certificates": "3D Printing, Laser Cutting, Electronics",
            },
            {
                "name": "Michael Thompson",
                "custom_id": "T-04",
                "major": "Industrial Design",
                "training_certificates": "CNC Router, Woodworking, 3D Printing",
            },
            {
                "name": "Dr. Lisa Wang",
                "custom_id": "T-05",
                "major": "Materials Science",
                "training_certificates": "3D Printing, Resin Printing, Vacuum Former",
            },
            {
                "name": "David Martinez",
                "custom_id": "T-06",
                "major": "Robotics Engineering",
                "training_certificates": "Soldering, CNC Mill, Electronics",
            },
            {
                "name": "Jessica Brown",
                "custom_id": "T-07",
                "major": "Product Design",
                "training_certificates": "Laser Cutting, Sewing, 3D Printing",
            },
            {
                "name": "Prof. Robert Kim",
                "custom_id": "T-08",
                "major": "Manufacturing Engineering",
                "training_certificates": "CNC Mill, CNC Router, Lathe, Bandsaw",
            },
            {
                "name": "Amanda Garcia",
                "custom_id": "T-09",
                "major": "Architecture",
                "training_certificates": "Laser Cutting, 3D Printing, Model Making",
            },
            {
                "name": "Chris Johnson",
                "custom_id": "T-10",
                "major": "Biomedical Engineering",
                "training_certificates": "3D Printing, Resin Printing, Electronics",
            },
        ]

        # Create trainers
        for data in trainers_data:
            trainer = Trainer.objects.create(
                name=data["name"],
                custom_id=data["custom_id"],
                major=data["major"],
                training_certificates=data["training_certificates"]
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'Created trainer: {trainer.name} ({trainer.custom_id}) - {trainer.major}'
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nSuccessfully created {len(trainers_data)} trainers!'
            )
        )
