from urllib.parse import urlparse, parse_qs

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import path


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


@login_required(login_url='/admin/login')
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
        data = cursor.fetchall()

    ctx = {
        'columns': columns,
        'data': data,
        'defaults': [None] * len(columns),
        'types': ['number', 'number', 'datetime', 'datetime', 'text', 'tel', 'text', 'text', 'text', 'checkbox'],
        'editables': [False] + [True] * (len(columns) - 1),
        'editable': True
    }
    # TODO: pending reservation filter

    return render(request, 'admin/table_view.html', ctx)


@login_required(login_url='/admin/login')
def update_reservations(request):
    pass


@login_required(login_url='/admin/login')
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


@login_required
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


@login_required(login_url='/admin/login')
def home(request):
    return render(request, 'admin/home.html')


@login_required(login_url='/admin/login')
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


def login_api(request):
    email = request.POST.get('email')
    password = request.POST.get('password')

    user = authenticate(username=email, password=password)

    if user is None:
        res = HttpResponse('<p id="login_error" class="text-red-500">Invalid Username or Password</p>', status=401)
        res["HX-Retarget"] = "#login_error"
        res["HX-Reswap"] = "outerHTML"
        return res

    login(request, user)
    res = HttpResponse('Success')

    referer = request.META.get('HTTP_REFERER')
    if referer:
        parsed_url = urlparse(referer)
        query_params = parse_qs(parsed_url.query)
        next_url = query_params.get('next', [None])[0]
    else:
        next_url = None

    res['HX-Redirect'] = next_url
    return res


urlpatterns = [
    path('', home),
    path('reservations', reservations),
    path('customers', customers),
    path('staff', staff),
    path('vehicles', vehicles),
    path('login', lambda r: render(r, 'admin/login.html')),
    path('api/update_reservations', update_reservations),
    path('api/login', login_api),
]
