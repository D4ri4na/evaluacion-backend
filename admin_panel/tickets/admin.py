from django.contrib import admin
from .models import Venue, Event, TicketTier, Reservation

admin.site.site_header = "Panel de Administración - Tickets"

class TicketTierInline(admin.TabularInline):
    model = TicketTier
    extra = 0

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'venue', 'event_date', 'created')
    search_fields = ('title', 'venue__name')
    list_filter = ('event_date', 'venue__city')
    inlines = [TicketTierInline] 

@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'created')

@admin.register(TicketTier)
class TicketTierAdmin(admin.ModelAdmin):
    list_display = ('name', 'event', 'price', 'available_quantity', 'total_capacity')

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'customer_email', 'ticket_tier', 'quantity_bought', 'status')