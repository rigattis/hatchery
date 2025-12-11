from django.contrib import admin
from .models import Space, Machine, Reservation, Schedule, Trainer
from .forms import MachineForm

@admin.register(Machine)
class MachineAdmin(admin.ModelAdmin):
    list_display = ("name", "custom_id", "category")
    filter_horizontal = ("certifications_required",)

# @admin.register(Machine)
# class MachineAdmin(admin.ModelAdmin):
#     form = MachineForm
#     list_display = ("name", "custom_id", "category", "amount", "display_locations")
#     #inlines = [LocationInline]                    # <-- show Locations on Machine page

#     def display_locations(self, obj):
#         return ", ".join(obj.locations.values_list("location_name", flat=True))
#     display_locations.short_description = "Locations"

@admin.register(Trainer)
class TrainerAdmin(admin.ModelAdmin):
    list_display = ("name", "major", "custom_id")
    search_fields = ("name", "major", "custom_id", "training_certificates")

#admin.site.register(Machine)
admin.site.register(Space)
admin.site.register(Reservation)
admin.site.register(Schedule)

