from django.core.management.base import BaseCommand
from django.utils.timezone import make_aware
from datetime import datetime, timedelta
from tickets.models import Venue, Event, TicketTier, Reservation

class Command(BaseCommand):
    help = 'Limpia la base de datos y genera >300 recursos principales y >500 hijos para pruebas de estrés'

    def handle(self, *args, **options):
        self.stdout.write('Limpiando registros antiguos...')
        Reservation.objects.all().delete()
        TicketTier.objects.all().delete()
        Event.objects.all().delete()
        Venue.objects.all().delete()

        # 1. Creamos el Venue
        ucb_venue = Venue.objects.create(name="UCB - Santa Cruz", city="Santa Cruz")

        # 2. Creamos los 2 eventos específicos del Frontend
        self.stdout.write('Creando 300 Eventos (Main Resources)...')
        events_to_create = [
            Event(
                venue=ucb_venue,
                title="NASA SPACE",
                event_date=make_aware(datetime(2026, 5, 26, 7, 0)),
                description="Evento destacado del Frontend"
            ),
            Event(
                venue=ucb_venue,
                title="COMMUNITY DAY",
                event_date=make_aware(datetime(2026, 7, 9, 13, 0)),
                description="Evento destacado del Frontend"
            )
        ]

        # Agregamos 298 eventos genéricos para cumplir los 300 exigidos
        base_date = make_aware(datetime(2026, 8, 1, 20, 0))
        for i in range(298):
            events_to_create.append(Event(
                venue=ucb_venue,
                title=f"LOUD NIGHT VOL {i+1}",
                event_date=base_date + timedelta(days=i),
                description="Stress test event"
            ))
        
        # BULK CREATE para Eventos (Ultra rápido)
        Event.objects.bulk_create(events_to_create)
        all_events = list(Event.objects.all())

        # 3. Creamos 1 TicketTier para cada uno de los 300 eventos
        self.stdout.write('Asignando categorías de entrada a los eventos...')
        tiers_to_create = []
        for ev in all_events:
            tiers_to_create.append(TicketTier(
                event=ev,
                name="General Pass",
                price=100.00 if "NASA" in ev.title else (0.00 if "COMMUNITY" in ev.title else 50.00),
                total_capacity=1000,
                available_quantity=45 if "NASA" in ev.title else (0 if "COMMUNITY" in ev.title else 500)
            ))
        TicketTier.objects.bulk_create(tiers_to_create)
        all_tiers = list(TicketTier.objects.all())

        # 4. Creamos 500 Reservas (Hijos) por cada uno de los 300 eventos = 150,000 registros
        self.stdout.write('Generando 500 reservas por evento (Total: 150,000 registros). Esto tomará unos segundos...')
        reservations_to_create = []
        batch_size = 10000  # Evita que la RAM colapse insertando de a 10,000

        for tier in all_tiers:
            for j in range(500):
                reservations_to_create.append(Reservation(
                    ticket_tier=tier,
                    customer_name=f"Fanático {j}",
                    customer_email=f"fan_{j}@loud.com",
                    quantity_bought=1,
                    status='confirmed'
                ))
            
            # Si acumulamos muchos, hacemos la inserción por lote y vaciamos la lista
            if len(reservations_to_create) >= batch_size:
                Reservation.objects.bulk_create(reservations_to_create)
                reservations_to_create = []

        # Insertar los restantes
        if reservations_to_create:
            Reservation.objects.bulk_create(reservations_to_create)

        self.stdout.write(self.style.SUCCESS('¡Éxito! Creados 300 recursos principales y 150,000 recursos hijos usando Bulk Create.'))