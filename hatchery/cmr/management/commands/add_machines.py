from django.core.management.base import BaseCommand
from django.core.files import File
from cmr.models import Machine
import os
from pathlib import Path

class Command(BaseCommand):
    help = 'Add 29 hardcoded machine instances with images from static folder'

    def handle(self, *args, **kwargs):
        machines_data = [
            {"id": 1, "name": "Planer", "image": "Planer.jpg"},
            {"id": 2, "name": "Soldering Irons", "image": "Soldering Irons.jpg"},
            {"id": 3, "name": "Vertical Bandsaw", "image": "Vertical Bandsaw.jpg"},
            {"id": 4, "name": "CNC Mill", "image": "CNC Mill.jpg"},
            {"id": 5, "name": "Drill Press", "image": "Drill Press.jpg"},
            {"id": 6, "name": "Stratasys J55", "image": "Stratasys J55.jpg"},
            {"id": 7, "name": "Bambu", "image": "bambu_2048.jpg"},
            {"id": 8, "name": "Digital Embroidery Machine", "image": "Digital Embroidery Machine.jpg"},
            {"id": 9, "name": "Drum Sander", "image": "Drum Sander.jpg"},
            {"id": 10, "name": "Table Router", "image": "Table Router.jpg"},
            {"id": 11, "name": "UV Printer", "image": "UV Printer.jpg"},
            {"id": 12, "name": "Horizontal Bandsaw", "image": "Horizontal Bandsaw.jpg"},
            {"id": 13, "name": "CNC Router", "image": "CNC ROuter.jpg"},
            {"id": 14, "name": "Edge Sander", "image": "Edge Sander.jpg"},
            {"id": 15, "name": "Scroll Saw", "image": "Scroll Saw.jpg"},
            {"id": 16, "name": "Vacuum Former", "image": "Vacuum Former.jpg"},
            {"id": 17, "name": "Sewing Machines", "image": "Sewing Machines.jpg"},
            {"id": 18, "name": "Prusa Mini", "image": "Prusa Mini.jpg"},
            {"id": 19, "name": "Sticker Printer", "image": "Sticker Printer.jpg"},
            {"id": 20, "name": "Table Saw", "image": "Table Saw.jpg"},
            {"id": 21, "name": "Laser Cutters", "image": "Laser Cutters.jpg"},
            {"id": 22, "name": "Miter Saw", "image": "Miter Saw.jpg"},
            {"id": 23, "name": "Prusa SL1S", "image": "Prusa SL1S.jpg"},
            {"id": 24, "name": "Prusa XL", "image": "Prusa XL.jpg"},
            {"id": 25, "name": "Microcontrollers", "image": "Microcontrollers.jpg"},
            {"id": 26, "name": "Hand Tools", "image": "Hand Tools.jpg"},
            {"id": 27, "name": "Direct to Garment Printer", "image": "Direct to garment Printer.jpg"},
            {"id": 28, "name": "Jointer", "image": "Jointer.jpg"},
            {"id": 29, "name": "Formlabs", "image": "Formlabs.jpg"},
        ]

        static_images_path = Path(__file__).resolve().parent.parent.parent.parent / 'static' / 'images'

        for machine_data in machines_data:
            custom_id = f"M-{machine_data['id']:02d}"

            # Check if machine already exists
            if Machine.objects.filter(custom_id=custom_id).exists():
                self.stdout.write(self.style.WARNING(f'Machine {custom_id} already exists, skipping...'))
                continue

            image_path = static_images_path / machine_data['image']

            if not image_path.exists():
                self.stdout.write(self.style.ERROR(f'Image not found: {image_path}'))
                continue

            # Create machine instance
            machine = Machine(
                name=machine_data['name'],
                custom_id=custom_id,
                about="Placeholder description",
                category="General",
                amount=1,
                specifications="Placeholder specifications"
            )

            # Copy image to media folder
            with open(image_path, 'rb') as img_file:
                machine.machine_image.save(
                    machine_data['image'],
                    File(img_file),
                    save=True
                )

            machine.save()
            # certifications_required is a ManyToMany field, can be set after save if needed
            # machine.certifications_required.set([])  # Empty list for now
            self.stdout.write(self.style.SUCCESS(f'Successfully created machine: {machine.name} ({custom_id})'))

        self.stdout.write(self.style.SUCCESS(f'\nCompleted! Created {len(machines_data)} machines.'))
