from django.core.management.base import BaseCommand
from django.core.files import File
from cmr.models import Space
from pathlib import Path

class Command(BaseCommand):
    help = 'Add Space instances from JSON-like data with floorplan images'

    def handle(self, *args, **kwargs):
        spaces_data = [
    {
        "title": "Classroom Lab: Hatch Front",
        "custom_id": "CS-02-01",
        "capacity": 30,
        "location": "2nd Floor: Hatch Front",
        "floor": 2,
        "type": "classroom",
        "notes": "",
        "floorplan_image": "floorplans/CS-02-01_36EJ2By.png",
        "current_machine": None,
        "capabilities": []
    },
    {
        "title": "Workstation 01",
        "custom_id": "SP-02-01",
        "capacity": 1,
        "location": "2nd Floor: Hatch Front",
        "floor": 2,
        "type": "station",
        "notes": "Table workstation, no machines. In to use a machine, create a separate machine reservation.",
        "floorplan_image": "floorplans/SP-02-01.png",
        "current_machine": None,
        "capabilities": []
    },
    {
        "title": "Workstation 02",
        "custom_id": "SP-02-02",
        "capacity": 1,
        "location": "2nd Floor: Hatch Front",
        "floor": 2,
        "type": "station",
        "notes": "Workstation only, no machine capabilities. Please reserve a machine separately.",
        "floorplan_image": "floorplans/SP-02-02.png",
        "current_machine": None,
        "capabilities": []
    },
    {
        "title": "Workstation 03",
        "custom_id": "SP-02-03",
        "capacity": 1,
        "location": "2nd Floor: Hatch Front",
        "floor": 2,
        "type": "station",
        "notes": "No machine capability, table station only. Reserve a machine separately.",
        "floorplan_image": "floorplans/SP-02-03.png",
        "current_machine": None,
        "capabilities": []
    },
    {
        "title": "Workstation 04",
        "custom_id": "SP-02-04",
        "capacity": 1,
        "location": "2nd Floor: Hatch Front",
        "floor": 2,
        "type": "station",
        "notes": "No machine capability. Table workstation only. Please reserve a machine separately.",
        "floorplan_image": "floorplans/SP-02-04.png",
        "current_machine": None,
        "capabilities": []
    },
    {
        "title": "Workstation 05",
        "custom_id": "SP-02-05",
        "capacity": 1,
        "location": "2nd Floor: Hatch Front",
        "floor": 2,
        "type": "station",
        "notes": "",
        "floorplan_image": "floorplans/SP-02-05.png",
        "current_machine": None,
        "capabilities": []
    },
    {
        "title": "Workstation 06",
        "custom_id": "SP-02-06",
        "capacity": 1,
        "location": "2nd Floor: Hatch Front",
        "floor": 2,
        "type": "station",
        "notes": "",
        "floorplan_image": "floorplans/SP-02-06.png",
        "current_machine": None,
        "capabilities": []
    },
    {
        "title": "Workstation 07",
        "custom_id": "SP-02-07",
        "capacity": 1,
        "location": "2nd Floor: Hatch Front",
        "floor": 2,
        "type": "station",
        "notes": "",
        "floorplan_image": "floorplans/SP-02-07.png",
        "current_machine": None,
        "capabilities": []
    },
    {
        "title": "Workstation 08",
        "custom_id": "SP-02-08",
        "capacity": 1,
        "location": "2nd Floor: Hatch Front",
        "floor": 2,
        "type": "station",
        "notes": "",
        "floorplan_image": "floorplans/SP-02-08.png",
        "current_machine": None,
        "capabilities": []
    },
    {
        "title": "Workstation 09",
        "custom_id": "SP-02-09",
        "capacity": 1,
        "location": "2nd Floor: Hatch Front",
        "floor": 2,
        "type": "station",
        "notes": "",
        "floorplan_image": "floorplans/SP-02-09.png",
        "current_machine": None,
        "capabilities": []
    },
    {
        "title": "Workstation 10",
        "custom_id": "SP-02-10",
        "capacity": 1,
        "location": "2nd Floor: Hatch Front",
        "floor": 2,
        "type": "station",
        "notes": "",
        "floorplan_image": "floorplans/SP-02-10.png",
        "current_machine": None,
        "capabilities": []
    },
    {
        "title": "Workstation 11",
        "custom_id": "SP-02-11",
        "capacity": 1,
        "location": "2nd Floor: Hatch Front",
        "floor": 2,
        "type": "station",
        "notes": "",
        "floorplan_image": "floorplans/SP-02-11.png",
        "current_machine": None,
        "capabilities": []
    },
    {
        "title": "Workstation 12",
        "custom_id": "SP-02-12",
        "capacity": 1,
        "location": "2nd Floor: Hatch Front",
        "floor": 2,
        "type": "station",
        "notes": "",
        "floorplan_image": "floorplans/SP-02-12.png",
        "current_machine": None,
        "capabilities": []
    },
    {
        "title": "Workstation 13",
        "custom_id": "SP-02-13",
        "capacity": 1,
        "location": "2nd Floor: Hatch Back",
        "floor": 2,
        "type": "station",
        "notes": "",
        "floorplan_image": "floorplans/SP-02-13.png",
        "current_machine": None,
        "capabilities": []
    },
    {
        "title": "Workstation 14",
        "custom_id": "SP-02-14",
        "capacity": 1,
        "location": "2nd Floor: Hatch Back",
        "floor": 2,
        "type": "station",
        "notes": "",
        "floorplan_image": "floorplans/SP-02-14.png",
        "current_machine": None,
        "capabilities": []
    },
    {
        "title": "Workstation 15",
        "custom_id": "SP-02-15",
        "capacity": 1,
        "location": "2nd Floor: Hatch Back",
        "floor": 2,
        "type": "station",
        "notes": "",
        "floorplan_image": "floorplans/SP-02-15.png",
        "current_machine": None,
        "capabilities": []
    },
    {
        "title": "Workstation 16",
        "custom_id": "SP-02-16",
        "capacity": 1,
        "location": "2nd Floor: Hatch Back",
        "floor": 2,
        "type": "station",
        "notes": "",
        "floorplan_image": "floorplans/SP-02-16.png",
        "current_machine": None,
        "capabilities": []
    },
    {
        "title": "Workstation 17",
        "custom_id": "SP-02-17",
        "capacity": 1,
        "location": "2nd Floor: Hatch Back",
        "floor": 2,
        "type": "station",
        "notes": "",
        "floorplan_image": "floorplans/SP-02-17.png",
        "current_machine": None,
        "capabilities": []
    },
    {
        "title": "Workstation 18",
        "custom_id": "SP-02-18",
        "capacity": 1,
        "location": "2nd Floor: Hatch Back",
        "floor": 2,
        "type": "station",
        "notes": "",
        "floorplan_image": "floorplans/SP-02-18.png",
        "current_machine": None,
        "capabilities": []
    },
    {
        "title": "Workstation 19",
        "custom_id": "SP-02-19",
        "capacity": 1,
        "location": "2nd Floor: Hatch Back",
        "floor": 2,
        "type": "station",
        "notes": "",
        "floorplan_image": "floorplans/SP-02-19.png",
        "current_machine": None,
        "capabilities": []
    },
    {
        "title": "Workstation 20",
        "custom_id": "SP-02-20",
        "capacity": 1,
        "location": "2nd Floor: Hatch Back",
        "floor": 2,
        "type": "station",
        "notes": "",
        "floorplan_image": "floorplans/SP-02-20.png",
        "current_machine": None,
        "capabilities": []
    },
    {
        "title": "Workstation 21",
        "custom_id": "SP-02-21",
        "capacity": 1,
        "location": "2nd Floor: Hatch Back",
        "floor": 2,
        "type": "station",
        "notes": "",
        "floorplan_image": "floorplans/SP-02-21.png",
        "current_machine": None,
        "capabilities": []
    },
    {
        "title": "Workstation 22",
        "custom_id": "SP-02-22",
        "capacity": 1,
        "location": "2nd Floor: Hatch Back",
        "floor": 2,
        "type": "station",
        "notes": "",
        "floorplan_image": "floorplans/SP-02-22.png",
        "current_machine": None,
        "capabilities": []
    },
    {
        "title": "Workstation 23",
        "custom_id": "SP-02-23",
        "capacity": 1,
        "location": "2nd Floor: Hatch Back",
        "floor": 2,
        "type": "station",
        "notes": "",
        "floorplan_image": "floorplans/SP-02-23.png",
        "current_machine": None,
        "capabilities": []
    },
    {
        "title": "Workstation 24",
        "custom_id": "SP-02-24",
        "capacity": 1,
        "location": "2nd Floor: Hatch Back",
        "floor": 2,
        "type": "station",
        "notes": "",
        "floorplan_image": "floorplans/SP-02-24.png",
        "current_machine": None,
        "capabilities": []
    },
    {
        "title": "Workstation 25",
        "custom_id": "SP-02-25",
        "capacity": 1,
        "location": "2nd Floor: Hatch Back",
        "floor": 2,
        "type": "station",
        "notes": "",
        "floorplan_image": "floorplans/SP-02-25.png",
        "current_machine": None,
        "capabilities": []
    },
    {
        "title": "Workstation 26",
        "custom_id": "SP-02-26",
        "capacity": 1,
        "location": "2nd Floor: Hatch Back",
        "floor": 2,
        "type": "station",
        "notes": "",
        "floorplan_image": "floorplans/SP-02-26.png",
        "current_machine": None,
        "capabilities": []
    },
    {
        "title": "Classroom Lab: Hatch Back",
        "custom_id": "CS-02-02",
        "capacity": 40,
        "location": "2nd Floor: Hatch Back",
        "floor": 2,
        "type": "classroom",
        "notes": "",
        "floorplan_image": "floorplans/CS-02-02.png",
        "current_machine": None,
        "capabilities": []
    }
]


        static_images_path = Path(__file__).resolve().parent.parent.parent.parent / 'static' / 'images'

        for space_data in spaces_data:
            custom_id = space_data['custom_id']

            # Skip if the space already exists
            if Space.objects.filter(custom_id=custom_id).exists():
                self.stdout.write(self.style.WARNING(f'Space {custom_id} already exists, skipping...'))
                continue

            floorplan_file = space_data.pop('floorplan_image', None)
            current_machine = space_data.pop('current_machine', None)
            capabilities = space_data.pop('capabilities', [])

            space = Space(**space_data)

            if floorplan_file:
                image_path = static_images_path / floorplan_file
                if image_path.exists():
                    with open(image_path, 'rb') as img_file:
                        space.floorplan_image.save(floorplan_file, File(img_file), save=False)
                else:
                    self.stdout.write(self.style.ERROR(f'Image not found: {image_path}'))

            space.save()

            if current_machine:
                try:
                    from cmr.models import Machine
                    machine_instance = Machine.objects.get(pk=current_machine)
                    space.current_machine = machine_instance
                    space.save(update_fields=['current_machine'])
                except Machine.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f'Current machine ID {current_machine} not found for {custom_id}'))

            if capabilities:
                space.capabilities.set(capabilities)

            self.stdout.write(self.style.SUCCESS(f'Successfully created space: {space.title} ({custom_id})'))

        self.stdout.write(self.style.SUCCESS('\nCompleted!'))
