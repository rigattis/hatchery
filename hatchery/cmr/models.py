from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from django import forms
from core import constants as const
from pct.models import TrainingCourse, TrainingRecord

class Space (models.Model):
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
    
    title = models.CharField(max_length = 120)
    custom_id = models.CharField(max_length = 10, unique = True) #custom IDs of the form SP-2-01, where the second field indicates the floor and
    #the third field indicates the incremental id number
    capacity = models.IntegerField()
    location = models.CharField(choices=LOCATION_CHOICES)
    floor = models.IntegerField(choices=FLOOR_CHOICES)
    type = models.CharField(choices=TYPE_CHOICES)
    notes = models.TextField(blank=True, null=True)
    floorplan_image = models.ImageField(
        upload_to='floorplans/',
        blank=True,
        null=True,
        help_text="Upload an image showing the space's location on the floor plan."
    )
    
    capabilities = models.ManyToManyField( 
        'Machine', 
        related_name='supported_by_spaces', 
        blank=True, 
        help_text="Which machines this space is capable of hosting." )

    current_machine = models.ForeignKey(
        'Machine',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='installed_in_spaces'
    )

    def clean(self):
        """Ensure current_machine is one of the space capabilities."""
        super().clean()
        if self.current_machine and self.current_machine not in self.capabilities.all():
            raise ValidationError({
                'current_machine': "This machine is not in the list of capabilities for this space."
            })

    def get_absolute_url(self):
        return reverse("space-detail", kwargs={"custom_id": self.custom_id})
    

    def __str__(self):
        return self.title
    
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     # Set queryset here to avoid circular imports
    #     from .models import Machine
    #     self.capabilities = Machine.objects.all()
    
# staff adding machine
class Machine (models.Model):
    name = models.CharField(max_length=130)
    about = models.TextField(blank=True, null=True, default="None")
    custom_id = models.CharField(max_length = 10, unique = True) #custom IDs of the form M-3D-01, where the second field indicates the machine type
    #the third field indicates the incremental id number
    installed_in = models.ForeignKey(
        "Space",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="machines_installed_here"
    )
    category = models.TextField()
    certifications_required = models.ManyToManyField(
        TrainingCourse,
        blank=True,
        related_name="machines_requiring",
        help_text="Training courses required to operate this machine."
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    specifications = models.TextField(blank=True, null=True)
    machine_image = models.ImageField(
        upload_to='machines/',
        blank=True,
        null=True,
    )
    
    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("machine-detail", kwargs={"custom_id": self.custom_id})
    

# class Location(models.Model):
#   machine = models.ForeignKey(
#      Machine,
#      on_delete=models.CASCADE,
#      related_name="locations"
#      )
#   location_name = models.CharField(max_length=200)
    
#reservation for both a space and machine

class Trainer (models.Model):
    name = models.CharField(max_length=130)
    custom_id = models.CharField(max_length = 10, unique = True) #custom IDs of the form M-3D-01, where the second field indicates the machine type
    #the third field indicates the incremental id number
    major = models.TextField(max_length=200, blank=True)
    training_certificates = models.TextField(blank=True, null=True)
    trainer_image = models.ImageField(
        upload_to='trainers/',
        blank=True,
        null=True,
    )
    certified_machines = models.ManyToManyField(
        'Machine',
        related_name='certified_trainers',
        blank=True,
        help_text="Machines this trainer is certified to supervise"
    )
    
    def __str__(self):
        return self.name

    def get_absolute_url(self):
        # Use the pk-based trainer_detail URL (matches config/urls.py)
        return reverse("trainer_detail", kwargs={"pk": self.pk})

class Reservation (models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    space = models.ForeignKey(
        Space,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="space_reservations"
    )

    machine = models.ForeignKey(
        Machine,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="machine_reservations"
    )

    trainer = models.ForeignKey(
        Trainer,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="trainer_reservations"
    )

    linked_reservation = models.OneToOneField(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="reverse_link"
    )

    reservation_title = models.CharField(max_length=120)

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reservations"
    )

    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    notes = models.TextField(blank=True, null=True)
    
    # Status field - only applies to trainer reservations
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='approved',  # Default to approved for backward compatibility
        help_text="Approval status for trainer reservations"
    )

    class Meta:
        indexes = [
            models.Index(fields=['date', 'start_time', 'end_time'])
        ]

    def __str__(self):
        target = self.space or self.machine or self.trainer
        return f"Reservation by {self.user.username} for {target}"

    def get_reservable_object(self):
        return self.space or self.machine or self.trainer
    
    def clean(self):
        super().clean()

        # -- Time validation already present
        if self.start_time >= self.end_time:
            raise ValidationError("End time must be after start time.")

        # ---------- TRAINING VALIDATION ----------
        # If booking a machine:
        if self.machine:
            required = self.machine.certifications_required.all()

            if required.exists():
                person = getattr(self.user, "person", None)

                if not person:
                    raise ValidationError("Your user account is not linked to a Person record.")

                user_trainings = TrainingRecord.objects.filter(person=person).values_list(
                    "training_course_id", flat=True
                )

                missing = required.exclude(id__in=user_trainings)

                if missing.exists():
                    names = ", ".join(m.name for m in missing)
                    raise ValidationError(f"You do not have the required training to reserve this machine: {names}")
        if self.space and self.space.current_machine:
            machine = self.space.current_machine
            required = machine.certifications_required.all()

            if required.exists():
                person = getattr(self.user, "person", None)

                if not person:
                    raise ValidationError("Your user account is not linked to a Person record.")

                user_trainings = TrainingRecord.objects.filter(person=person).values_list(
                    "training_course_id", flat=True
                )

                missing = required.exclude(id__in=user_trainings)

                if missing.exists():
                    names = ", ".join(m.name for m in missing)
                    raise ValidationError(
                        f"You do not have the required training to reserve this space "
                        f"(it includes machine {machine.name}). Missing: {names}"
                    )

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

# Schedule model for defining operating schedules
class Schedule(models.Model):
    name = models.CharField(
        max_length=120,
        help_text="Name of the schedule (e.g., 'Fall 2024 Hours', 'Summer Break Schedule')"
    )
    start_date = models.DateField(
        help_text="The date when this schedule becomes active"
    )
    end_date = models.DateField(
        help_text="The date when this schedule ends"
    )
    open_time = models.TimeField(
        help_text="Daily opening time"
    )
    close_time = models.TimeField(
        help_text="Daily closing time"
    )
    days_of_week = models.CharField(
        max_length=50,
        help_text="Days this schedule applies to (stored as comma-separated values: Mon,Tue,Wed,Thu,Fri,Sat,Sun)"
    )
    location = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Location where this schedule applies"
    )
    holidays = models.TextField(
        blank=True,
        null=True,
        help_text="Holiday dates in mm-dd-yr format, separated by semicolons (e.g., '12-25-24;01-01-25')"
    )
    is_active = models.BooleanField(
        default=False,
        help_text="Whether this schedule is currently active (multiple schedules can be active)"
    )

    def __str__(self):
        return f"{self.name} ({self.start_date} to {self.end_date})"

    def get_days_set(self):
        """Return a set of days this schedule applies to"""
        if not self.days_of_week:
            return set()
        return set(day.strip() for day in self.days_of_week.split(','))

    def get_normalized_days_set(self):
        """
        Return a set of normalized day abbreviations (Mon, Tue, etc.)
        Handles both full names (Monday) and abbreviations (Mon)
        """
        if not self.days_of_week:
            return set()

        # Map full names to abbreviations
        day_map = {
            'Monday': 'Mon', 'Mon': 'Mon',
            'Tuesday': 'Tue', 'Tue': 'Tue',
            'Wednesday': 'Wed', 'Wed': 'Wed',
            'Thursday': 'Thu', 'Thu': 'Thu',
            'Friday': 'Fri', 'Fri': 'Fri',
            'Saturday': 'Sat', 'Sat': 'Sat',
            'Sunday': 'Sun', 'Sun': 'Sun'
        }

        normalized_days = set()
        for day in self.days_of_week.split(','):
            day = day.strip()
            if day in day_map:
                normalized_days.add(day_map[day])

        return normalized_days

    def check_conflicts_with_active_schedules(self):
        """
        Check if activating this schedule would conflict with currently active schedules.
        Returns a list of conflicting schedules with details about the conflicts.
        """
        conflicts = []

        # Get all currently active schedules except this one
        active_schedules = Schedule.objects.filter(is_active=True).exclude(id=self.id)

        # Get the normalized days this schedule applies to
        self_days = self.get_normalized_days_set()

        for active_schedule in active_schedules:
            # Get the normalized days the active schedule applies to
            active_days = active_schedule.get_normalized_days_set()

            # Find overlapping days
            overlapping_days = self_days & active_days

            if overlapping_days:
                # Check if date ranges overlap
                if not (self.end_date < active_schedule.start_date or
                        self.start_date > active_schedule.end_date):
                    # There's a conflict - same days and overlapping date ranges
                    conflicts.append({
                        'schedule': active_schedule,
                        'overlapping_days': sorted(overlapping_days),
                        'date_overlap': (
                            max(self.start_date, active_schedule.start_date),
                            min(self.end_date, active_schedule.end_date)
                        )
                    })

        return conflicts

    def set_as_active(self):
        """
        Set this schedule as active. Raises ValueError if there are conflicts
        with other active schedules.
        """
        conflicts = self.check_conflicts_with_active_schedules()

        if conflicts:
            # Build detailed error message
            error_parts = [f"Cannot activate schedule '{self.name}' due to conflicts:"]

            for conflict in conflicts:
                conflict_schedule = conflict['schedule']
                days = ', '.join(conflict['overlapping_days'])
                start_date, end_date = conflict['date_overlap']

                error_parts.append(
                    f"  - Conflicts with '{conflict_schedule.name}' on {days} "
                    f"from {start_date} to {end_date}"
                )

            raise ValueError('\n'.join(error_parts))

        self.is_active = True
        self.save()

    def get_absolute_url(self):
        return reverse("schedule-detail", kwargs={"id": self.id})

    class Meta:
        ordering = ['-start_date']

# Help Ticket model for user support requests
class HelpTicket(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('resolved', 'Resolved'),
    ]

    CATEGORY_CHOICES = [
        ('website', 'Website'),
        ('machine', 'Machine'),
        ('spaces', 'Spaces'),
        ('training', 'Training'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="help_tickets",
        help_text="User who submitted the ticket"
    )
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='website',
        help_text="Category of the issue"
    )
    subject = models.CharField(
        max_length=200,
        help_text="Brief subject of the help request"
    )
    description = models.TextField(
        help_text="Detailed description of the issue or request"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='open',
        help_text="Current status of the ticket"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the ticket was created"
    )
    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the ticket was resolved"
    )
    resolved_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="resolved_tickets",
        help_text="Admin who resolved the ticket"
    )

    def __str__(self):
        return f"Ticket #{self.id}: {self.subject} - {self.status}"

    def resolve(self, admin_user):
        """Mark ticket as resolved"""
        self.status = 'resolved'
        self.resolved_at = timezone.now()
        self.resolved_by = admin_user
        self.save()

    class Meta:
        ordering = ['-created_at']

# Contact model for staff directory
class Contact(models.Model):
    name = models.CharField(
        max_length=200,
        help_text="Full name of the contact"
    )
    position = models.CharField(
        max_length=200,
        help_text="Job title or position"
    )
    email = models.EmailField(
        help_text="Contact email address"
    )
    phone = models.CharField(
        max_length=20,
        help_text="Contact phone number"
    )
    photo = models.ImageField(
        upload_to='contacts/',
        blank=True,
        null=True,
        help_text="Profile photo (optional)"
    )
    order = models.IntegerField(
        default=0,
        help_text="Display order (lower numbers appear first)"
    )

    def __str__(self):
        return f"{self.name} - {self.position}"

    class Meta:
        ordering = ['order', 'name']

# Project model for showcasing student projects
class Project(models.Model):
    title = models.CharField(
        max_length=200,
        help_text="Project title"
    )
    description = models.TextField(
        help_text="Project description"
    )
    student_name = models.CharField(
        max_length=200,
        help_text="Name of student(s) who worked on this project"
    )
    image = models.ImageField(
        upload_to='projects/',
        blank=True,
        null=True,
        help_text="Project image (optional)"
    )
    date_completed = models.DateField(
        help_text="Date project was completed"
    )
    order = models.IntegerField(
        default=0,
        help_text="Display order (lower numbers appear first)"
    )

    def __str__(self):
        return f"{self.title} by {self.student_name}"

    class Meta:
        ordering = ['-date_completed', 'order']

# Event model for current and upcoming events
class Event(models.Model):
    title = models.CharField(
        max_length=200,
        help_text="Event title"
    )
    description = models.TextField(
        help_text="Event description"
    )
    event_date = models.DateField(
        help_text="Date of the event"
    )
    event_time = models.TimeField(
        help_text="Time of the event"
    )
    location = models.CharField(
        max_length=200,
        help_text="Event location"
    )
    image = models.ImageField(
        upload_to='events/',
        blank=True,
        null=True,
        help_text="Event image (optional)"
    )
    order = models.IntegerField(
        default=0,
        help_text="Display order (lower numbers appear first)"
    )

    def __str__(self):
        return f"{self.title} on {self.event_date}"

    class Meta:
        ordering = ['event_date', 'order']