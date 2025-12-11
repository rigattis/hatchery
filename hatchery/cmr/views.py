from django.contrib import messages

from django.core.exceptions import ValidationError

from collections import defaultdict
from django.db.models import Q, Min

from django.http import Http404, JsonResponse

from django.db.models import Q

from django.shortcuts import render, get_object_or_404, redirect

from datetime import timedelta

from django.utils import timezone

from .models import Space, Machine, Reservation, Schedule, Trainer

from .forms import SpaceForm,MachineForm, ExistingMachineForm, ReservationForm, ScheduleForm,TrainerForm,TrainerFilterForm

import json

from django.contrib.auth.decorators import login_required

from django.http import HttpResponseForbidden

# Create your views here.

def landing_view(request):
    context = {}
    if request.user.is_authenticated:
        # Get all user reservations, but exclude pending/rejected trainer reservations
        user_reservations = Reservation.objects.filter(
            user=request.user
        ).filter(
            # Include all non-trainer reservations OR only approved trainer reservations
            Q(trainer__isnull=True) | Q(status='approved')
        )
        context = {
            'user': request.user,
            'reservations': user_reservations
        }
        return render(request, "login_success.html", context)
    return render(request, "landing.html", context)

@login_required
def my_reservations_json(request):
    # Get all user's reservations
    # For trainer reservations, only include approved ones (exclude pending and rejected)
    reservations = Reservation.objects.filter(
        user=request.user
    ).filter(
        # Include all non-trainer reservations OR only approved trainer reservations
        Q(trainer__isnull=True) | Q(status='approved')
    ).values(
        "id", "reservation_title", "date", "start_time", "end_time",
        "space__title", "machine__name", "trainer__name", "status"
    )
    return JsonResponse(list(reservations), safe=False)

@login_required
def edit_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)

    if request.method == "POST":
        title = request.POST.get("reservation_title")
        date = request.POST.get("date")
        start_time = request.POST.get("start_time")
        end_time = request.POST.get("end_time")
        notes = request.POST.get("notes", "")

        # Basic validation (optional)
        if not (title and date and start_time and end_time):
            messages.error(request, "Please fill in all required fields.")
            return redirect("landing page")  # Replace with your reservations page name

        # Update the reservation
        reservation.reservation_title = title
        reservation.date = date
        reservation.start_time = start_time
        reservation.end_time = end_time
        reservation.notes = notes
        reservation.save()

        messages.success(request, "Reservation updated successfully!")
        return redirect("landing page")
    
    return redirect("landing page")

@login_required
def delete_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)

    if request.method == "POST":
        reservation.delete()
        messages.success(request, "Reservation deleted successfully!")
        return redirect("landing page")

    return HttpResponseForbidden("You are not allowed to delete this reservation.")

def space_list_view(request):
    queryset = Space.objects.all()
    
    # Get search/filter parameters from the GET request
    search_query = request.GET.get('q', '')
    type_filter = request.GET.get('type', '')
    location_filter = request.GET.get('location', '')

    # Filter by title or custom_id
    if search_query:
        queryset = queryset.filter(
            Q(title__icontains=search_query) |
            Q(custom_id__icontains=search_query)
        )
    
    # Filter by type
    if type_filter:
        queryset = queryset.filter(type=type_filter)
    
    # Filter by location
    if location_filter:
        queryset = queryset.filter(location=location_filter)

    has_machines = request.GET.get("has_machines")
    if has_machines == "yes":
        queryset = queryset.exclude(current_machine__isnull=False)
    elif has_machines == "no":
        queryset = queryset.filter(current_machine__isnull=True)


    context = {
        "space_list": queryset,
        "search_query": search_query,
        "type_filter": type_filter,
        "location_filter": location_filter,
        "has_machines": has_machines,
        "type_choices": Space.TYPE_CHOICES,
        "location_choices": Space.LOCATION_CHOICES
    }
    return render(request, "spaceslist.html", context)

def space_edit_view(request, custom_id):
    space = get_object_or_404(Space, custom_id=custom_id)
    if request.method == "POST":
        form = SpaceForm(request.POST, instance=space)
        if form.is_valid():
            form.save()
            return redirect("space-detail", custom_id=space.custom_id)
    else:
        form = SpaceForm(instance=space)
    return render(request, "space_detail.html", {"object": space, "form": form})

def space_delete_view(request, custom_id):
    space = get_object_or_404(Space, custom_id=custom_id)
    if request.method == "POST":
        space.delete()
        return redirect("space-list")
    return redirect("space-list")

def space_create_view(request):
    if request.method == "POST":
        form = SpaceForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Space created successfully!")
            return redirect("space-list")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = SpaceForm()

    context = {'form': form}
    return render(request, "spaces_create.html", context)

def dynamic_lookup_view(request, custom_id):
    obj = get_object_or_404(Space, custom_id=custom_id)
    edit_form = SpaceForm(instance=obj)
    reservation_form = ReservationForm()
    context = {
        "object": obj,
        "edit_form": edit_form,
        "reservation_form": reservation_form
    }
    return render(request, "space_detail.html", context)

# adding machines form 

def New_machine_create_view(request):
    # Only accept POSTs for this modal submit
    if request.method != "POST":
        return redirect("machine_list")

    form = MachineForm(request.POST, request.FILES)
    if form.is_valid():
        form.save()
        return redirect("machine_list")

    # If invalid, re-render the same list page with BOTH forms:
    # - show the invalid New form (with errors) in its modal
    # - keep the Existing form available/blank
    queryset = Machine.objects.all()
    return render(
        request,
        "machine_list.html",
        {
            "object_list": queryset,
            "form_new": form,                       # preserve user input + errors
            "form_existing": ExistingMachineForm(),
            "open_modal": "new", # other modal still works
        },
    )

def Existing_machine_create_view(request):
    if request.method != "POST":
        return redirect("machine_list")  # safeguard against GETs

    form = ExistingMachineForm(request.POST)
    if form.is_valid():
        form.save()
        return redirect("machine_list")

    # If invalid, re-render machine_list.html with both forms
    queryset = Machine.objects.all()
    return render(
        request,
        "machine_list.html",
        {
            "object_list": queryset,
            "form_new": MachineForm(),      # keep both modals available
            "form_existing": form,          # preserve user's invalid input + errors
        },
    )


# def machine_list_view(request):
#    queryset = Machine.objects.all() #list of objects 
#    form_new = MachineForm()  # empty form for the modal
#    form_existing = ExistingMachineForm() 
#    return render(request, "machine_list.html", { "object_list": queryset,"form_new": form_new, "form_existing": form_existing})


def machines_by_name_view(request, name):
    # Find all machines that share this exact name
    machines = Machine.objects.filter(name=name)

    if not machines.exists():
        raise Http404("No machines found with that name")
    
    locations = set()
    for m in machines:
        if m.installed_in:
             locations.add(f"{m.installed_in.location}: {m.installed_in}")

    # Convert to sorted list
    all_locations = sorted(locations)

    # OPTIONAL:
    # Attach the locations to each machine instance (useful for templates)
    for m in machines:
        m.all_locations = all_locations

    # You can also keep your existing filters here if you want later
    return render(request, "machines_by_name.html", {
        "name": name,
        "machines": machines,
    })

def machine_list_view(request):
    # Read filters from the query string
    q = (request.GET.get('q') or "").strip()
    category = (request.GET.get('category') or "").strip()
    space_locations = Space.objects.values_list('location', flat=True).distinct().order_by('location')
    selected_location = request.GET.get('space_location', '').strip()

    queryset = Machine.objects.select_related('installed_in').all()

    # Text search
    if q:
        queryset = queryset.filter(
            Q(name__icontains=q) |
            Q(custom_id__icontains=q) |
            Q(specifications__icontains=q)
        )

    # Filter by category
    if category:
        queryset = queryset.filter(category=category)

    # Filter by space location
    if selected_location:
        queryset = queryset.filter(installed_in__location=selected_location)

    filtered_qs = queryset

    # JSON data for JS
    machines_for_js = [
        {
            "name": m.name,
            "category": m.category,
            "about": m.about,
            "specifications": m.specifications,
        }
        for m in filtered_qs
    ]

    # Deduplicate machines by name
    name_groups = filtered_qs.values('name').annotate(first_id=Min('id'))
    unique_ids = [row['first_id'] for row in name_groups]
    no_duplicates_qs = Machine.objects.filter(id__in=unique_ids).order_by('name')

    # Collect all locations (from installed_in)
    locations_by_name = defaultdict(set)
    for m in filtered_qs:
        if m.installed_in:
            locations_by_name[m.name].add(m.installed_in.location)

    machines = list(no_duplicates_qs)
    for m in machines:
        m.all_locations = sorted(locations_by_name.get(m.name, []))

    # Forms
    form_new = MachineForm()
    form_existing = ExistingMachineForm()
    filter_form = MachineForm()

    context = {
        "object_list": machines,
        "form_new": form_new,
        "form_existing": form_existing,
        "form": filter_form,
        "query": q,
        "category": category,
        "machines_json": json.dumps(machines_for_js),
        "space_locations": space_locations,
        "selected_location": selected_location
    }

    return render(request, "machine_list.html", context)

def _get_machine(custom_id=None, pk=None):
    if custom_id is not None:
        return get_object_or_404(Machine, custom_id=custom_id)
    return get_object_or_404(Machine, pk=pk)

def machine_detail_view(request, custom_id=None, pk=None):
    obj = _get_machine(custom_id, pk)
    edit_form = MachineForm(instance=obj)
    reservation_form = ReservationForm()
    
    trainers = Trainer.objects.filter(
        training_certificates__icontains=obj.category
    )
    
    return render(request, "machine_detail.html", {
        "object": obj,
        "edit_form": edit_form,
        "reservation_form": reservation_form,
        "trainers": trainers,
    })

def machine_edit_view(request, custom_id=None, pk=None):
    obj = _get_machine(custom_id, pk)
    if request.method == "POST":
        form = MachineForm(request.POST,request.FILES, instance=obj)
        if form.is_valid():
            obj = form.save()
            if obj.custom_id:
                return redirect("machine-detail", custom_id=obj.custom_id)
            return redirect("machine-detail-id", pk=obj.pk)
        # invalid → re-render detail with bound form (shows errors inside modal)
        
        return render(request, "machine_detail.html", {
            "object": obj,
            "edit_form": form,
        })
    # GET (rare if you only submit from modal) → show detail
    return redirect("machine-detail", custom_id=obj.custom_id) if obj.custom_id else redirect("machine-detail-id", pk=obj.pk)

def machine_delete_view(request, custom_id=None, pk=None):
    obj = _get_machine(custom_id, pk)
    if request.method == "POST":
        obj.delete()
        return redirect("machine_list")
    # If someone GETs the delete URL, just bounce back to detail
    return redirect("machine-detail", custom_id=obj.custom_id) if obj.custom_id else redirect("machine-detail-id", pk=obj.pk)

#space reservation

def reservation_create_view(request, custom_id=None):
    space = get_object_or_404(Space, custom_id=custom_id)
    
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to create a reservation.")
        return redirect("space-detail", custom_id=space.custom_id)

    if request.method == 'POST':
        form = ReservationForm(request.POST)

        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.user = request.user
            reservation.space = space

            try:
                reservation.full_clean()
                reservation.save()

            except ValidationError as e:
                for msg in e.messages:
                    messages.error(request, msg)
                
                return render(request, "space_detail.html", {
                    "object": space,
                    "reservation_form": form,
                    "edit_form": SpaceForm(instance=space)
                })

            
            # CREATE LINKED MACHINE RESERVATION (if machine installed)
            if space.current_machine:
                linked_res = Reservation(
                    machine=space.current_machine,
                    user=request.user,
                    reservation_title=f"Linked to {reservation.reservation_title}",
                    date=reservation.date,
                    start_time=reservation.start_time,
                    end_time=reservation.end_time,
                    linked_reservation=reservation
                )

                try:
                    linked_res.full_clean()  # ALSO validates training
                    linked_res.save()
                except ValidationError as e:
                    for msg in e.messages:
                        messages.error(request, msg)
                    
                    return render(request, "space_detail.html", {
                        "object": space,
                        "reservation_form": form,
                        "edit_form": SpaceForm(instance=space)
                    })

                # Link back to the machine reservation
                reservation.linked_reservation = linked_res
                reservation.save(update_fields=['linked_reservation'])

            # SUCCESS
            messages.success(request, "Reservation created successfully!")
            return redirect("space-detail", custom_id=space.custom_id)

        else:
            messages.error(request, "Please correct the errors below.")

    else:
        form = ReservationForm()
        form.fields.pop('space')
        form.fields.pop('machine')
        form.fields.pop('trainer')

    return render(request, "space_detail.html", {
        "object": space,
        "reservation_form": form,
        "edit_form": SpaceForm(instance=space)
    })

def space_reservation_edit_view(request, custom_id, reservation_id):
    """Edit an existing space reservation"""
    space = get_object_or_404(Space, custom_id=custom_id)
    reservation = get_object_or_404(Reservation, id=reservation_id, space=space)
    
    # Check if user is authenticated and owns this reservation or is staff
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to edit a reservation.")
        return redirect("space-detail", custom_id=custom_id)
    
    if reservation.user != request.user and not request.user.is_staff:
        messages.error(request, "You can only edit your own reservations.")
        return redirect("space-detail", custom_id=custom_id)
    
    if request.method == 'POST':
        form = ReservationForm(request.POST, instance=reservation)
        if form.is_valid():
            form.save()
            messages.success(request, "Reservation updated successfully!")
            return redirect("space-detail", custom_id=custom_id)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ReservationForm(instance=reservation)
    
    return render(request, "space_detail.html", {
        "object": space,
        "reservation_form": form,
        "form_edit": SpaceForm(instance=space),
        "editing_reservation": reservation
    })

def space_reservation_delete_view(request, custom_id, reservation_id):
    """Delete a space reservation"""
    space = get_object_or_404(Space, custom_id=custom_id)
    reservation = get_object_or_404(Reservation, id=reservation_id, space=space)
    
    # Check if user is authenticated and owns this reservation or is staff
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to delete a reservation.")
        return redirect("space-detail", custom_id=custom_id)
    
    if reservation.user != request.user and not request.user.is_staff:
        messages.error(request, "You can only delete your own reservations.")
        return redirect("space-detail", custom_id=custom_id)
    
    if request.method == 'POST':
        reservation.delete()
        messages.success(request, "Reservation deleted successfully!")
        return redirect("space-detail", custom_id=custom_id)
    
    return redirect("space-detail", custom_id=custom_id)

def reservation_create_viewMachines(request, custom_id=None):
    machine = get_object_or_404(Machine, custom_id=custom_id)
    # Check if user is authenticated
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to create a reservation.")
        return redirect("machine-detail", custom_id=machine.custom_id)
    
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.user = request.user
            reservation.machine = machine
            try:
                reservation.full_clean()
                reservation.save()

            except ValidationError as e:
                for msg in e.messages:
                    messages.error(request, msg)
                
                return render(request, "machine_detail.html", {
                    "object": machine,
                    "reservation_form": form,
                    "edit_form": SpaceForm(instance=machine)
                })

            # Check if the space has a current machine installed
            if machine.installed_in:
                linked_reservation = Reservation(
                    space=machine.installed_in,
                    user=request.user,
                    reservation_title=f"Linked to {reservation.reservation_title}",
                    date=reservation.date,
                    start_time=reservation.start_time,
                    end_time=reservation.end_time,
                    linked_reservation=reservation
                )
                linked_reservation.save()
                # Link back to the space reservation
                reservation.linked_reservation = linked_reservation
                reservation.save(update_fields=['linked_reservation'])

            messages.success(request, "Reservation created successfully!")
            return redirect("machine-detail", custom_id=machine.custom_id)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ReservationForm()
        form.fields.pop('space')
        form.fields.pop('machine')
        form.fields.pop('trainer')

    return render(request, "machine_detail.html", {
        "object": machine,
        "reservation_form": form,
        "edit_form": MachineForm(instance=machine)
    })

# Schedule views

def schedule_list_view(request):
    """List all schedules with search functionality"""
    queryset = Schedule.objects.all()

    # Get search parameter
    search_query = request.GET.get('q', '')

    # Filter by name
    if search_query:
        queryset = queryset.filter(name__icontains=search_query)

    # Create empty form for the create modal
    form = ScheduleForm()

    context = {
        "schedule_list": queryset,
        "search_query": search_query,
        "form": form
    }
    return render(request, "schedule_list.html", context)

def schedule_create_view(request):
    """Create a new schedule"""
    if request.method == 'POST':
        form = ScheduleForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('schedule-list')
        else:
            # If form has errors, return to schedule list with the form and its errors
            queryset = Schedule.objects.all()
            context = {
                "schedule_list": queryset,
                "search_query": "",
                "form": form,
                "open_modal_create": True
            }
            return render(request, "schedule_list.html", context)

    # For GET requests, redirect to schedule list
    return redirect('schedule-list')

def schedule_edit_view(request, id):
    """Edit an existing schedule"""
    schedule = get_object_or_404(Schedule, id=id)

    if request.method == "POST":
        form = ScheduleForm(request.POST, instance=schedule)
        if form.is_valid():
            form.save()
            return redirect("schedule-list")
        else:
            # If form has errors, return to schedule list with error indication
            queryset = Schedule.objects.all()
            context = {
                "schedule_list": queryset,
                "search_query": "",
                "form": ScheduleForm(),
                "edit_schedule_id": id,
                "edit_form_errors": form.errors
            }
            return render(request, "schedule_list.html", context)

    # For GET requests, redirect to schedule list
    return redirect("schedule-list")

def schedule_delete_view(request, id):
    """Delete a schedule"""
    schedule = get_object_or_404(Schedule, id=id)
    if request.method == "POST":
        schedule.delete()
        return redirect("schedule-list")
    return redirect("schedule-list")

def schedule_set_active_view(request, id):
    """Toggle a schedule as active/inactive"""
    schedule = get_object_or_404(Schedule, id=id)
    if request.method == "POST":
        if schedule.is_active:
            # Deactivate this schedule
            schedule.is_active = False
            schedule.save()
            messages.success(request, f"Schedule '{schedule.name}' has been deactivated.")
        else:
            # Activate this schedule - check for conflicts
            try:
                schedule.set_as_active()
                messages.success(request, f"Schedule '{schedule.name}' has been activated.")
            except ValueError as e:
                # Conflict detected
                messages.error(request, str(e))
        return redirect("schedule-list")
    return redirect("schedule-list")

def space_reservations_json(request, custom_id):
    space = get_object_or_404(Space, custom_id=custom_id)
    reservations = Reservation.objects.filter(
        space=space
    ).values(
        "id",
        "reservation_title",
        "date",
        "start_time",
        "end_time",
        "user__username"
    )
    return JsonResponse(list(reservations), safe=False)

def machines_reservations_json(request, custom_id):
    """Return all reservations for this space (as JSON)."""
    machine = get_object_or_404(Machine, custom_id=custom_id)
    reservations = Reservation.objects.filter(
        machine=machine
    ).values(
        "id",
        "reservation_title",
        "date",
        "start_time",
        "end_time",
        "user__username"
    )
    return JsonResponse(list(reservations), safe=False)

#Trainers

def trainer_list_view(request):
    q = (request.GET.get("q") or "").strip()
    selected_cert = (request.GET.get("training_certificates") or "").strip()

    queryset = Trainer.objects.all()

    if q:
        queryset = queryset.filter(
            Q(name__icontains=q) | Q(custom_id__icontains=q)
        )

    if selected_cert:
        # training_certificates is a comma-separated TextField, so use icontains
        queryset = queryset.filter(training_certificates__icontains=selected_cert)

    # use the same CATEGORY_CHOICES as the TrainerForm
    category_choices = TrainerForm.CATEGORY_CHOICES

    filter_form = TrainerFilterForm(
        initial={
            "q": q,
            "training_certificates": selected_cert,
        },
        category_choices=category_choices,
    )

    context = {
        "object_list": queryset,
        "filter_form": filter_form,
        "form_new": TrainerForm(),   # modal form for "Add Trainer"
        "q": q,
        "training_certificates": selected_cert,
        "open_modal": request.GET.get("open_modal"),
        "category_choices": category_choices,
    }
    return render(request, "trainer_list.html", context)
def trainer_create_view(request):
    if request.method == "POST":
        form = TrainerForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save()
            return redirect("trainer_detail", pk=obj.pk)
        # re-render list on error and reopen modal
        return render(request, "trainer_list.html", {
            "object_list": Trainer.objects.all(),
            "filter_form": TrainerFilterForm(
                major_choices=[value for value, _ in TrainerForm.CATEGORY_CHOICES]
            ),
            "form_new": form,
            "open_modal": "new",
            "q": "",
            "training_certificates": "",
            "category_choices": [value for value, _ in TrainerForm.CATEGORY_CHOICES],
        })

    return redirect("trainer_list")

def trainer_detail_view(request, pk):
    obj = get_object_or_404(Trainer, pk=pk)
    form_edit = TrainerForm(instance=obj)
    reservation_form = ReservationForm()
    return render(request, "trainer_detail.html", {
        "object": obj,
        "form_edit": form_edit,
        "reservation_form": reservation_form
    })

def trainer_edit_view(request, pk):
    obj = get_object_or_404(Trainer, pk=pk)
    if request.method == "POST":
        form = TrainerForm(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Trainer updated successfully!")
            return redirect("trainer_detail", pk=obj.pk)
        # re-render detail page with errors
        return render(request, "trainer_detail.html", {
            "object": obj,
            "form_edit": form,
        })
    return redirect("trainer_detail", pk=obj.pk)

def trainer_delete_view(request, pk):
    obj = get_object_or_404(Trainer, pk=pk)
    if request.method == "POST":
        obj.delete()
        messages.success(request, "Trainer deleted successfully!")
        return redirect("trainer_list")
    return redirect("trainer_detail", pk=obj.pk)

def reservation_create_viewTrainers(request, pk):
    trainer = get_object_or_404(Trainer, pk=pk)
    
    # Check if user is authenticated
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to create a reservation.")
        return redirect("trainer_detail", pk=trainer.pk)
    
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.user = request.user
            reservation.trainer = trainer
            # Set trainer reservations to pending by default
            reservation.status = 'pending'
            reservation.save()
            messages.success(request, "Reservation created successfully! Awaiting approval.")
            return redirect("trainer_detail", pk=trainer.pk)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ReservationForm()
    
    return render(request, "trainer_detail.html", {
        "object": trainer,
        "reservation_form": form,
        "form_edit": TrainerForm(instance=trainer)
    })

def trainers_reservations_json(request, pk):
    """Return all reservations for this trainer (as JSON)."""
    trainer = get_object_or_404(Trainer, pk=pk)
    # Exclude rejected reservations from the calendar
    reservations = Reservation.objects.filter(
        trainer=trainer
    ).exclude(
        status='rejected'
    ).values(
        "id",
        "reservation_title",
        "date",
        "start_time",
        "end_time",
        "user__username",
        "status"
    )
    return JsonResponse(list(reservations), safe=False)

def all_trainers_reservations_json(request):
    """Return all reservations for all trainers with trainer info (as JSON)."""
    # Exclude rejected reservations from the calendar
    reservations = Reservation.objects.filter(
        trainer__isnull=False
    ).exclude(
        status='rejected'
    ).select_related('trainer').values(
        "id",
        "reservation_title",
        "date",
        "start_time",
        "end_time",
        "user__username",
        "trainer__id",
        "trainer__name",
        "trainer__custom_id",
        "status"
    )
    return JsonResponse(list(reservations), safe=False)

def trainer_reservation_edit_view(request, pk, reservation_id):
    """Edit an existing trainer reservation"""
    trainer = get_object_or_404(Trainer, pk=pk)
    reservation = get_object_or_404(Reservation, id=reservation_id, trainer=trainer)
    
    # Check for redirect_to parameter in POST or GET
    redirect_url = request.POST.get('redirect_to') or request.GET.get('redirect_to')
    
    def get_redirect():
        if redirect_url == 'trainer_list':
            return redirect("trainer_list")
        return redirect("trainer_detail", pk=trainer.pk)
    
    # Check if user is authenticated and owns this reservation or is staff
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to edit a reservation.")
        return get_redirect()
    
    if reservation.user != request.user and not request.user.is_staff:
        messages.error(request, "You can only edit your own reservations.")
        return get_redirect()
    
    if request.method == 'POST':
        form = ReservationForm(request.POST, instance=reservation)
        if form.is_valid():
            form.save()
            messages.success(request, "Reservation updated successfully!")
            return get_redirect()
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ReservationForm(instance=reservation)
    
    return render(request, "trainer_detail.html", {
        "object": trainer,
        "reservation_form": form,
        "form_edit": TrainerForm(instance=trainer),
        "editing_reservation": reservation
    })

def trainer_reservation_delete_view(request, pk, reservation_id):
    """Delete a trainer reservation"""
    trainer = get_object_or_404(Trainer, pk=pk)
    reservation = get_object_or_404(Reservation, id=reservation_id, trainer=trainer)
    
    # Check for redirect_to parameter in POST or GET
    redirect_url = request.POST.get('redirect_to') or request.GET.get('redirect_to')
    
    def get_redirect():
        if redirect_url == 'trainer_list':
            return redirect("trainer_list")
        return redirect("trainer_detail", pk=trainer.pk)
    
    # Check if user is authenticated and owns this reservation or is staff
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to delete a reservation.")
        return get_redirect()
    
    if reservation.user != request.user and not request.user.is_staff:
        messages.error(request, "You can only delete your own reservations.")
        return get_redirect()
    
    if request.method == 'POST':
        reservation.delete()
        messages.success(request, "Reservation deleted successfully!")
        return get_redirect()
    
    return get_redirect()

def trainer_reservation_approve_view(request, pk, reservation_id):
    """Approve or reject a trainer reservation"""
    trainer = get_object_or_404(Trainer, pk=pk)
    reservation = get_object_or_404(Reservation, id=reservation_id, trainer=trainer)
    
    # Check for redirect_to parameter in POST or GET
    redirect_url = request.POST.get('redirect_to') or request.GET.get('redirect_to')
    
    def get_redirect():
        if redirect_url == 'trainer_list':
            return redirect("trainer_list")
        return redirect("trainer_detail", pk=trainer.pk)
    
    # Check if user is authenticated
    # NOTE: Currently allowing all authenticated users to approve for testing/demo
    # In production, uncomment the staff check below:
    # if not request.user.is_staff:
    #     messages.error(request, "Only staff members can approve reservations.")
    #     return get_redirect()
    
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to approve reservations.")
        return get_redirect()
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            reservation.status = 'approved'
            reservation.save()
            messages.success(request, "Reservation approved successfully!")
        elif action == 'reject':
            reservation.status = 'rejected'
            reservation.save()
            messages.success(request, "Reservation rejected.")
        return get_redirect()
    
    return redirect("trainer_detail", pk=trainer.pk)

def about_view(request):
    """Display about page with active schedule information"""
    from .models import Project, Event
    from datetime import date

    # Get all active schedules
    active_schedules = Schedule.objects.filter(is_active=True)

    # Create a list of all days with their hours
    all_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    schedule_days = []

    # For each day, find the most appropriate active schedule
    today = date.today()

    for day in all_days:
        day_schedule = None

        # Find active schedules that apply to this day
        for schedule in active_schedules:
            # Get the days set for this schedule
            days_set = schedule.get_days_set()

            # Check if this day is in the schedule (handle both full names and abbreviations)
            # days_set might contain "Monday" or "Mon", we check for both
            day_abbr = day[:3]  # "Monday" -> "Mon"
            if day in days_set or day_abbr in days_set:
                # Check if schedule covers today's date
                if schedule.start_date <= today <= schedule.end_date:
                    day_schedule = schedule
                    break

        if day_schedule:
            schedule_days.append({
                'day': day,
                'hours': f"{day_schedule.open_time.strftime('%I:%M %p')} - {day_schedule.close_time.strftime('%I:%M %p')}",
                'open': True,
                'schedule_name': day_schedule.name
            })
        else:
            schedule_days.append({
                'day': day,
                'hours': 'Closed',
                'open': False,
                'schedule_name': None
            })

    # Get projects and events
    projects = Project.objects.all()[:10]  # Latest 10 projects
    events = Event.objects.filter(event_date__gte=timezone.now().date())[:10]  # Upcoming 10 events

    context = {
        "active_schedules": active_schedules,
        "schedule_days": schedule_days,
        "projects": projects,
        "events": events
    }
    return render(request, "about.html", context)

# Help Ticket Views
from .forms import HelpTicketForm
from .models import HelpTicket
from django.contrib.auth.decorators import login_required

@login_required
def help_ticket_list_view(request):
    """Display list of open help tickets"""
    # Only show open tickets (resolved ones are removed from view)
    tickets = HelpTicket.objects.filter(status='open')

    # Check if user is admin/staff
    is_admin = request.user.is_staff or request.user.is_superuser

    context = {
        'tickets': tickets,
        'is_admin': is_admin,
        'form': HelpTicketForm(),
        'open_modal': request.GET.get('open_modal') == 'new',
    }
    return render(request, 'help_ticket_list.html', context)

@login_required
def help_ticket_create_view(request):
    """Create a new help ticket"""
    if request.method == 'POST':
        form = HelpTicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            return redirect('help-ticket-list')
        else:
            # Return to page with modal open and errors
            tickets = HelpTicket.objects.filter(status='open')
            is_admin = request.user.is_staff or request.user.is_superuser
            context = {
                'tickets': tickets,
                'is_admin': is_admin,
                'form': form,
                'open_modal': True,
            }
            return render(request, 'help_ticket_list.html', context)

    return redirect('help-ticket-list')

@login_required
def help_ticket_resolve_view(request, ticket_id):
    """Resolve a help ticket (admin only)"""
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('help-ticket-list')

    if request.method == 'POST':
        ticket = get_object_or_404(HelpTicket, id=ticket_id)
        ticket.resolve(request.user)

    return redirect('help-ticket-list')

# Contact Views
from .forms import ContactForm
from .models import Contact

def contact_list_view(request):
    """Display list of contacts"""
    contacts = Contact.objects.all()

    # Check if user is admin/staff
    is_admin = request.user.is_staff or request.user.is_superuser if request.user.is_authenticated else False

    context = {
        'contacts': contacts,
        'is_admin': is_admin,
        'form': ContactForm(),
        'open_modal': request.GET.get('open_modal') == 'new',
    }
    return render(request, 'contact_list.html', context)

@login_required
def contact_create_view(request):
    """Create a new contact (admin only)"""
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('contact-list')

    if request.method == 'POST':
        form = ContactForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('contact-list')
        else:
            # Return to page with modal open and errors
            contacts = Contact.objects.all()
            context = {
                'contacts': contacts,
                'is_admin': True,
                'form': form,
                'open_modal': True,
            }
            return render(request, 'contact_list.html', context)

    return redirect('contact-list')

