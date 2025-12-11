from django import forms

from .models import Space, Machine, Reservation, Schedule, Trainer, HelpTicket, Contact

from django.db.models import Q, Min

from pct.models import TrainingCourse

class SpaceForm(forms.ModelForm):
    TYPE_CHOICES = [
        ('station', 'Table Workstation'),
        ('classroom', 'Classroom Space'),
    ]
    LOCATION_CHOICES = [
        ('2nd Floor: Hatch Front', '2nd Floor: Hatch Front'),
        ('2nd Floor: Hatch Back', '2nd Floor: Hatch Back'),
        ('3rd Floor: Prototyping Studio', '3rd Floor: Prototyping Studio'),
        ('3rd Floor: Prototyping Shop', '3rd Floor: Prototyping Shop')
    ]
    FLOOR_CHOICES = (
        (2, '2nd Floor'),
        (3, '3rd Floor')
    )
    title = forms.CharField(label='',
                            widget=forms.TextInput(attrs = {"placeholder": "space title"}))
    custom_id = forms.CharField(label='',
                            widget=forms.TextInput(attrs = {"placeholder": "unique ID"}))
    capacity = forms.IntegerField(initial = 1)
    location = forms.ChoiceField(
        choices=LOCATION_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'dropdown'})
    )
    floor = forms.ChoiceField(
        choices = FLOOR_CHOICES,
        required = True,
        widget=forms.Select(attrs={'class': 'dropdown'})
    )
    type = forms.ChoiceField(
        choices=TYPE_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'dropdown'})
    )
    notes = forms.CharField(required=False, 
                                  widget=forms.Textarea(attrs={
                                      "placeholder": "your description",
                                      "class": "new-class-name two",
                                      "rows": 1,
                                      "cols": 20
                                  }))
    
    floorplan_image = forms.ImageField(required=False,
        widget=forms.ClearableFileInput(attrs={
            "class": "form-control-file",
            "accept": "image/*"
        }),
        label="Add Floor Plan Image"
    )

    capabilities = forms.ModelMultipleChoiceField(
        queryset=Machine.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Supported Machines"
    )

    current_machine = forms.ModelChoiceField(
        queryset=Machine.objects.none(),
        required=False,
        label="Current Machine Installed",
        widget=forms.Select(attrs={"class": "form-control"})
    )

    class Meta:
        model = Space
        fields = ['title', 'custom_id', 'capacity', 'location', 'floor', 'type', 'notes', 'floorplan_image', 'capabilities', 'current_machine']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if isinstance(self.instance, Space):
            if self.instance.pk:
                self.fields['current_machine'].queryset = self.instance.capabilities.all()
            else:
                self.fields['current_machine'].queryset = Machine.objects.none()

    def save(self, commit=True):
        space = super().save(commit=False)
        selected_machine = self.cleaned_data.get('current_machine')

        if commit:
            space.save()
            self.save_m2m()

            if selected_machine:
                if selected_machine.installed_in != space:
                    selected_machine.installed_in = space
                    selected_machine.save(update_fields=['installed_in'])

            Machine.objects.filter(installed_in=space).exclude(pk=getattr(selected_machine, 'pk', None)).update(installed_in=None)

        return space
# staff adding machine 

class MachineForm(forms.ModelForm):
    CATEGORY_CHOICES = [
        ('3D Printing', '3D Printing'),
        ('Textiles', 'Textiles'),
        ('Vinyl Cutting', 'Vinyl Cutting'),
        ('Woodworking', 'Woodworking'),
        ('Laser', 'Laser'),
        ('Metalworking', 'Metalworking'),
        ('Electronics', 'Electronics'),
    ]

    name = forms.CharField(required=True)
    custom_id = forms.CharField(required=True)
    about = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            "placeholder": "About",
            "class": "new-class-name two",
            "rows": 10,
            "cols": 40
        })
    )

    installed_in = forms.ModelChoiceField(
        queryset=Space.objects.all(),
        required=False,
        label="Current space the machine is installed in",
        widget=forms.Select(attrs={"class": "form-control"})
    )

    machine_image = forms.ImageField(required=False,
        widget=forms.ClearableFileInput(attrs={
            "class": "form-control-file",
            "accept": "image/*"
        }),
        label="Add Floor Plan Image"
    )
    
    specifications = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            "placeholder": "machine specifications",
            "class": "new-class-name two",
            "rows": 10,
            "cols": 40
        })
    )

    category = forms.ChoiceField(
        choices=CATEGORY_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'dropdown'})
    )

    amount = forms.DecimalField(required=True, initial=1)
    certifications_required = forms.ModelMultipleChoiceField(
        queryset=TrainingCourse.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={"class": "form-control"}),
        label="Required Training Courses"
    )

    def clean_name(self):
        name = self.cleaned_data['name'].strip()
        if self.instance and self.instance.pk:
            return name
        if Machine.objects.filter(name__iexact=name).exists():
            raise forms.ValidationError("A machine with this name already exists.")
        return name

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # Preselect trainings already assigned
            self.fields["certifications_required"].initial = self.instance.certifications_required.all()

    def save(self, commit=True):
        machine = super().save(commit=False)

        if commit:
            machine.save()
            self.save_m2m()

            # Sync installed_in → Space
            if machine.installed_in:
                space = machine.installed_in
                if space.current_machine != machine:
                    space.current_machine = machine
                if machine not in space.capabilities.all():
                    space.capabilities.add(machine)
                space.save(update_fields=['current_machine'])
            else:
                # Clear any spaces pointing to this machine if none selected
                Space.objects.filter(current_machine=machine).update(current_machine=None)

        return machine

    class Meta:
        model = Machine
        fields = ['name', 'about', 'category', 'certifications_required', 'amount',
                  'specifications', 'custom_id', 'machine_image', 'installed_in']


class ExistingMachineForm(forms.ModelForm):
    name = forms.ModelChoiceField(
        queryset=Machine.objects.all(),
        to_field_name='name',
        empty_label="Select a machine",
        label="Machine Name",
        required=True
    ) 
  

    custom_id = forms.CharField(required=True)
    amount = forms.DecimalField(required=True, initial=1)
    certifications_required = forms.ModelMultipleChoiceField(
        queryset=TrainingCourse.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Required Training Courses"
    )

    installed_in = forms.ModelChoiceField(
        queryset=Space.objects.all(),
        required=False,
        label="Current space the machine is installed in",
        widget=forms.Select(attrs={"class": "form-control"})
    )

    class Meta:
        model = Machine
        fields = ['name', 'amount', 'custom_id', 'certifications_required', 'installed_in']

    def save(self, commit=True):
        """
        Create a new Machine based on the selected existing Machine,
        copying category / about / specifications.
        """
        instance = super().save(commit=False)
        source_machine = self.cleaned_data['name']

        instance.name = source_machine.name
        instance.category = source_machine.category
        instance.about = source_machine.about
        instance.specifications = source_machine.specifications
        instance.installed_in = self.cleaned_data.get('installed_in')
        
        if source_machine.machine_image:
            instance.machine_image = source_machine.machine_image
            
        if commit:
            instance.save()

            # Sync installed_in → Space
            if instance.installed_in:
                space = instance.installed_in
                if space.current_machine != instance:
                    space.current_machine = instance
                if instance not in space.capabilities.all():
                    space.capabilities.add(instance)
                space.save(update_fields=['current_machine'])
            else:
                Space.objects.filter(current_machine=instance).update(current_machine=None)

        return instance
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        name_groups = (
            Machine.objects
            .values('name')
            .annotate(first_id=Min('id'))
        )
        unique_ids = [row['first_id'] for row in name_groups]

        
        no_duplicates_qs = Machine.objects.filter(id__in=unique_ids).order_by('name')

        self.fields['name'].queryset = no_duplicates_qs

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['reservation_title', 'date', 'start_time', 'end_time', 'notes']
        widgets = {
            'reservation_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter a short title for your reservation'
            }),
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'start_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control'
            }),
            'end_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Add any notes or special requests (optional)',
                'rows': 3
            }),
        }

    def __init__(self, *args, space=None, machine=None, trainer=None, **kwargs):
        super().__init__(*args, **kwargs)

        if space:
            self.instance.space = space
            self.fields['space'].widget = forms.HiddenInput()
        if machine:
            self.instance.machine = machine
            self.fields['machine'].widget = forms.HiddenInput()
        if trainer:
            self.instance.trainer = trainer
            self.fields['trainer'].widget = forms.HiddenInput()

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
        return instance

# Schedule form for creating and editing schedules
class ScheduleForm(forms.ModelForm):
    LOCATION_CHOICES = [
        ('2nd Floor: Hatch Front', '2nd Floor: Hatch Front'),
        ('2nd Floor: Hatch Back', '2nd Floor: Hatch Back'),
        ('3rd Floor: Prototyping Studio', '3rd Floor: Prototyping Studio'),
        ('3rd Floor: Prototyping Shop', '3rd Floor: Prototyping Shop')
    ]

    # Days of week checkboxes
    monday = forms.BooleanField(required=False, initial=True)
    tuesday = forms.BooleanField(required=False, initial=True)
    wednesday = forms.BooleanField(required=False, initial=True)
    thursday = forms.BooleanField(required=False, initial=True)
    friday = forms.BooleanField(required=False, initial=True)
    saturday = forms.BooleanField(required=False, initial=False)
    sunday = forms.BooleanField(required=False, initial=False)

    location = forms.ChoiceField(
        choices=LOCATION_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Schedule
        fields = ['name', 'start_date', 'end_date', 'open_time', 'close_time', 'location', 'holidays']

        widgets = {
            'name': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Schedule Name (e.g., Fall 2024 Hours)'}
            ),
            'start_date': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'}
            ),
            'end_date': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'}
            ),
            'open_time': forms.TimeInput(
                attrs={'type': 'time', 'class': 'form-control'}
            ),
            'close_time': forms.TimeInput(
                attrs={'type': 'time', 'class': 'form-control'}
            ),
            'holidays': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Enter holiday dates in mm-dd-yr format, separated by semicolons (e.g., 12-25-24;01-01-25)'
                }
            ),
        }

        labels = {
            'name': 'Schedule Name',
            'start_date': 'Start Date',
            'end_date': 'End Date',
            'open_time': 'Opening Time',
            'close_time': 'Closing Time',
            'holidays': 'Holiday Dates',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # If editing existing schedule, populate day checkboxes
        if self.instance and self.instance.pk and self.instance.days_of_week:
            days = self.instance.days_of_week.split(',')
            self.fields['monday'].initial = 'Mon' in days
            self.fields['tuesday'].initial = 'Tue' in days
            self.fields['wednesday'].initial = 'Wed' in days
            self.fields['thursday'].initial = 'Thu' in days
            self.fields['friday'].initial = 'Fri' in days
            self.fields['saturday'].initial = 'Sat' in days
            self.fields['sunday'].initial = 'Sun' in days

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Build days_of_week string from checkboxes
        selected_days = []
        if self.cleaned_data.get('monday'):
            selected_days.append('Mon')
        if self.cleaned_data.get('tuesday'):
            selected_days.append('Tue')
        if self.cleaned_data.get('wednesday'):
            selected_days.append('Wed')
        if self.cleaned_data.get('thursday'):
            selected_days.append('Thu')
        if self.cleaned_data.get('friday'):
            selected_days.append('Fri')
        if self.cleaned_data.get('saturday'):
            selected_days.append('Sat')
        if self.cleaned_data.get('sunday'):
            selected_days.append('Sun')

        instance.days_of_week = ','.join(selected_days)

        if commit:
            instance.save()
        return instance
    
    
class TrainerForm(forms.ModelForm):
    certified_machines = forms.ModelMultipleChoiceField(
        queryset=Machine.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Certified to Supervise (Machines)",
        help_text="Select all machines this trainer is certified to supervise"
    )

    # NEW: category choices + multi-select field
    CATEGORY_CHOICES = [
        ('3D Printing', '3D Printing'),
        ('Textiles', 'Textiles'),
        ('Vinyl Cutting', 'Vinyl Cutting'),
        ('Woodworking', 'Woodworking'),
        ('Laser', 'Laser'),
        ('Metalworking', 'Metalworking'),
        ('Electronics', 'Electronics'),
    ]

    training_certificates = forms.MultipleChoiceField(
        choices=CATEGORY_CHOICES,
        required=False,
        widget=forms.SelectMultiple(
            attrs={
                "class": "form-select",
                "size": 6,  
            }
        ),
        label="Training Certificates",
        help_text="Hold Ctrl (Cmd on Mac) to select multiple categories.",
    )
    
    class Meta:
        model = Trainer
        fields = ["custom_id", "name", "major", "training_certificates", "certified_machines", "trainer_image"]
        widgets = {
            "custom_id": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g., T-001"}),
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Trainer Name"}),
            "major": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g., Computer Science"}),
            "trainer_image": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk and self.instance.training_certificates:
            existing = [
                c.strip()
                for c in self.instance.training_certificates.split(",")
                if c.strip()
            ]
            self.initial.setdefault("training_certificates", existing)

    def clean_name(self):
        name = self.cleaned_data.get("name", "").strip()
        if not name:
            raise forms.ValidationError("Name is required.")
        qs = Trainer.objects.filter(name__iexact=name)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("A trainer with this name already exists.")
        return name
    
    def clean_custom_id(self):
        custom_id = self.cleaned_data.get("custom_id", "").strip()
        if not custom_id:
            raise forms.ValidationError("Custom ID is required.")
        qs = Trainer.objects.filter(custom_id__iexact=custom_id)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("A trainer with this custom ID already exists.")
        return custom_id

    def clean_training_certificates(self):
        data = self.cleaned_data.get("training_certificates") or []
        return ", ".join(data)



# Small filter form for the list page (search + major)
class TrainerFilterForm(forms.Form):
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Search by name or ID",
            }
        ),
        label="Search",
    )

    training_certificates = forms.ChoiceField(
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
        label="Training Certificates",
    )

    def __init__(self, *args, category_choices=None, **kwargs):
        super().__init__(*args, **kwargs)

        # category_choices expected as list of (value, label) pairs
        if category_choices is None:
            category_choices = []

        self.fields["training_certificates"].choices = [
            ("", "All Certificates"),
            *category_choices,
        ]

# Help Ticket Form
class HelpTicketForm(forms.ModelForm):
    category = forms.ChoiceField(
        label='Issue Category',
        choices=HelpTicket.CATEGORY_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    subject = forms.CharField(
        label='Subject',
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Brief description of your issue'
        })
    )
    description = forms.CharField(
        label='Description',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Please provide detailed information about your request or issue',
            'rows': 5
        })
    )

    class Meta:
        model = HelpTicket
        fields = ['category', 'subject', 'description']

# Contact Form
class ContactForm(forms.ModelForm):
    name = forms.CharField(
        label='Name',
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Full name'
        })
    )
    position = forms.CharField(
        label='Position',
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Job title or position'
        })
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'email@example.com'
        })
    )
    phone = forms.CharField(
        label='Phone',
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '(123) 456-7890'
        })
    )
    photo = forms.ImageField(
        label='Photo',
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control'
        })
    )
    order = forms.IntegerField(
        label='Display Order',
        initial=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '0'
        }),
        help_text='Lower numbers appear first'
    )

    class Meta:
        model = Contact
        fields = ['name', 'position', 'email', 'phone', 'photo', 'order']
