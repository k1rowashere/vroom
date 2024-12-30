import json

from django.contrib.auth.models import User
from django.db import connection
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.urls import path
from django.views.decorators.http import require_GET, require_POST
from django.views.generic import RedirectView

from app.utils import highlight_partial_matches


# TODO:
# vm.description,
# vm.transmission,
# vm.fuel,
# vm.seats,
# vm.doors,
# vm.ac,
# vm.automatic,
# vm.airbags,
#
# vm.electric_windows,
# vm.power_steering,
# vm.central_locking,
# vm.cruise_control,
# vm.audio_input,
# vm.bluetooth,
# vm.usb,
# vm.gps,
# vm.wifi,
# vm.parking_sensors,
# vm.rear_camera,
# vm.sunroof,
# vm.heated_seats,


def reservations(request):
    # user = request.user
    # if not user.is_authenticated or not user.has_perm('app.view_reservation'):
    #     return HttpResponse("<p>Not authorised to view this page</p>", status=403)

    with connection.cursor() as cursor:
        cursor.execute('''
            SELECT r.id,
                   r.owed_amount,
                   r.pickup,
                   r.dropoff,
                   r.owed_amount,
                   c.name,
                   c.phone,
                   c.license_no,
                   vm.make || ', ' || vm.model || ', ' || vm.year AS vehicle_name,
                   r.vehicle_plate,
                   r.approved_at
            FROM reservations r
                 JOIN vehicles v ON r.vehicle_plate = v.plate_no
                 JOIN vehicle_models vm ON v.model_id = vm.id
                 NATURAL LEFT JOIN customer_info c
            WHERE NOT EXISTS(SELECT * FROM dropoff WHERE reservation_id = r.id);
        ''')

        columns = [col[0] for col in cursor.description]
        types = [col[1] for col in cursor.description]
        print(types)
        data = cursor.fetchall()

    ctx = {
        'columns': columns,
        'data': data,
        'defaults': [None] * len(columns),
        # 'types': map_db_types(types)
    }

    return render(request, 'admin/table_view.html', ctx)


def customers(request):
    # user = request.user
    # if not user.is_authenticated or not user.has_perm('app.view_customers'):
    #     return HttpResponse("<p>Not authorised to view this page</p>", status=403)

    with connection.cursor() as cursor:
        cursor.execute('''
            SELECT c.name,
                   u.email,
                   c.phone,
                   c.license_no,
                   c.address
            FROM customer_info c, auth_user u
        ''')

        columns = [col[0] for col in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]

    return render(request, 'admin/customers.html', {'customers': results})


def staff(request):
    # user = request.user
    # if not user.is_authenticated or not user.has_perm('app.view_staff'):
    #     return HttpResponse("<p>Not authorised to view this page</p>", status=403)

    with connection.cursor() as cursor:
        cursor.execute('''
        SELECT u.first_name || ' ' || u.last_name AS name,
                u.email
            FROM staff_info s, auth_user u;
        ''')

        columns = [col[0] for col in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]

    return render(request, 'admin/staff.html', {'staff': results})


def vehicles(request):
    # user = request.user
    # if not user.is_authenticated or not user.has_perm('app.view_vehicles'):
    #     return HttpResponse("<p>Not authorised to view this page</p>", status=403)

    with connection.cursor() as cursor:
        cursor.execute('''
            SELECT v.plate_no,
                v.color,
                v.mileage,
                v.status,
                vm.make|| ', ' || vm.model || ', ' || vm.year::text,
                vm.id,
                vm.images,
                vm.price_per_day,
                vm.price_per_hour
            FROM vehicles v, vehicle_models vm;
        ''')

        columns = [col[0] for col in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]

    return render(request, 'admin/vehicles.html', {'vehicles': results})


urlpatterns = [
    path('', lambda r: render(r, 'admin/home.html')),
    path('reservations', reservations),
    path('customers', customers),
    path('staff', staff),
    path('vehicles', vehicles),
    # path('login', RedirectView.as_view(url='/admin/login')),
]
