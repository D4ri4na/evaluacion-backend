import uuid
from django.db import models

class Event(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    event_date = models.DateTimeField()
    venue = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'content"."event'
        verbose_name = 'Concierto / Evento'
        verbose_name_plural = 'Conciertos / Eventos'

    def __str__(self):
        return self.title


class TicketTier(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, db_column='event_id')
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total_capacity = models.IntegerField()
    available_quantity = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'content"."ticket_tier'
        unique_together = (('event', 'name'),)
        verbose_name = 'Categoría de Entrada'
        verbose_name_plural = 'Categorías de Entradas'

    def __str__(self):
        return f"{self.name} - {self.event.title}"


class Reservation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket_tier = models.ForeignKey(TicketTier, on_delete=models.RESTRICT, db_column='ticket_tier_id')
    customer_name = models.CharField(max_length=255)
    customer_email = models.CharField(max_length=255)
    quantity_bought = models.IntegerField()
    status = models.CharField(max_length=50, default='confirmed')
    reservation_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'content"."reservation'
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'

    def __str__(self):
        return f"{self.customer_name} ({self.quantity_bought} paxs)"