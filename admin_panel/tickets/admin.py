from django.contrib import admin
from .models import Venue, Event, TicketTier, Reservation

admin.site.site_header = "Panel de Administración - Tickets"
admin.site.site_title = "Admin Tickets"
admin.site.index_title = "Gestión del Sistema de Eventos"

@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'created')
    search_fields = ('name', 'city')

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'venue', 'event_date', 'created')
    search_fields = ('title', 'venue__name')
    list_filter = ('event_date', 'venue__city')

@admin.register(TicketTier)
class TicketTierAdmin(admin.ModelAdmin):
    list_display = ('name', 'event', 'price', 'available_quantity', 'total_capacity')
    search_fields = ('name', 'event__title')
    list_filter = ('event',)

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'customer_email', 'ticket_tier', 'quantity_bought', 'status', 'reservation_date')
    search_fields = ('customer_name', 'customer_email', 'ticket_tier__name')
    list_filter = ('status', 'reservation_date')