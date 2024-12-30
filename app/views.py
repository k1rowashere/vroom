from django.contrib.auth.models import User
from django.db import connection
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import path
from django.views.decorators.http import require_GET, require_POST
from django.views.generic import RedirectView

from app.utils import highlight_partial_matches


def load_global_context(request):
    context = {
        'nav_links': [
            {'name': 'Home', 'url': '/'},
            {'name': 'Catalog', 'url': '/catalog'},
            {'name': 'About', 'url': '/about'}
        ],
        'admin_nav_links': [
            {'name': 'Home', 'url': '/admin'},
            {'name': 'Customers', 'url': '/admin/customers'},
            {'name': 'Staff', 'url': '/admin/staff'},
            {'name': 'Vehicles', 'url': '/admin/vehicles'},
            {'name': 'Reservations', 'url': '/admin/reservations'}
        ],
    }
    return context


def about(request):
    return render(request, 'about.html')


def checkout(request):
    return render(request, 'checkout_personal.html')


def catalog(request):
    ctx = {'vehicle_types': [
        {'label': 'SUV', 'value': 'SUV', },
        {'label': 'Sedan', 'value': 'Sedan', },
        {'label': 'Truck', 'value': 'Truck', },
        {'label': 'Van', 'value': 'Van', },
        {'label': 'Coupe', 'value': 'Coupe', },
        {'label': 'Convertible', 'value': 'Convertible', },
        {'label': 'Wagon', 'value': 'Wagon', },
        {'label': 'Hatchback', 'value': 'Hatchback'},
    ]}

    return render(request, 'catalog.html', ctx)


def cart(request):
    context = {'cart': [{
        'display_name': 'voom voom',
        'vehicle_type': 'car',
        'image_urls': ['/static/assets/fire.webp'],
        'rating': 4.5,
        'price_per_day': 420,

    } for _ in range(1, 10)],
    }
    return render(request, 'cart.html', context)


@require_GET
def car_catalog(request):
    def sanitize_param(param, default=None):
        value = request.GET.get(param, default)
        return value if value != '' else default

    params = {
        'text_search': sanitize_param('search_term'),
        'price_min': sanitize_param('price_range_min', 0),
        'price_max': sanitize_param('price_range_max', 100000),
        'start_date': sanitize_param('reservation_start_date'),
        'end_date': sanitize_param('reservation_end_date'),
        'vehicle_type': sanitize_param('vehicle_type'),
    }

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT vm.id AS model_id,
                   vm.price_per_day AS price_per_day,
                   vm.price_per_hour AS price_per_hour,
                   vm.make AS make,
                   vm.model AS model,
                   vm.year AS year,
                   vm.rating AS rating,
                   vm.images,
                   vm.product_url AS url,
                   ARRAY_AGG(color) AS color
            FROM vehicle_models vm
                 LEFT JOIN vehicles v ON v.model_id = vm.id
            WHERE (%(vehicle_type)s IS NULL OR vm.type ILIKE %(vehicle_type)s)
              AND (%(text_search)s IS NULL OR CONCAT(vm.make, ' ', vm.model, ' ', vm.year::TEXT) ILIKE %(text_search)s)
              AND vm.price_per_hour BETWEEN %(price_min)s AND %(price_max)s
            GROUP BY vm.id
        """, {
            **params,
            'text_search': f"%{params['text_search']}%" if params['text_search'] else None,
        })
        columns = [col[0] for col in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]

    vehicles = [{
        'id': r['model_id'],
        'url': r['url'],
        'display_name': f"{r['make']} {r['model']} ({r['year']})",
        'vehicle_type': params['vehicle_type'] or 'car',  # Default to 'car' if not specified
        'image_urls': r['images'],
        'rating': float(r['rating']),
        'price_per_day': r['price_per_day'],
        'price_per_hour': r['price_per_hour'],
        'in_favorites': r['model_id'] in request.session.get('favorites', []),
    } for r in results]

    return render(request, 'parts/vehicle_result.html', {'vehicles': vehicles})


@require_GET
def active_search(request, search):
    # if len(search) < 3:
    #     return render(request, 'parts/vehicle_search_result.html', {'results': []})

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT vm.make AS make,
                vm.model AS model,
                vm.year AS year,
                similarity(vm.make || ' ' || vm.model || ' ' || vm.year::text, %(search)s) AS similarity_score
            FROM vehicle_models vm
            WHERE 
                similarity(vm.make || ' ' || vm.model || ' ' || vm.year::text, %(search)s) > 0.1
            ORDER BY similarity_score DESC;
        """, {'search': search})

        columns = [col[0] for col in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        for r in results:
            r['display_name'] = highlight_partial_matches(f"{r['make']} {r['model']} ({r['year']})", search)

    return render(request, 'parts/vehicle_search_result.html', {'results': results})


@require_POST
def login(request):
    email = request.POST.get('email')
    password = request.POST.get('password')
    user = User.objects.get(email=email)
    if user.check_password(password):
        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'failed'})


@require_POST
def register(request):
    email = request.POST.get('email')
    password = request.POST.get('password')
    user = User.objects.create_user(username=email, email=email, password=password)
    return JsonResponse({'status': 'success'})


@require_POST
def toggle_favorite(request):
    cart = request.session.get('favorites', [])
    vehicle_id = int(request.POST.get('model_id'))
    if vehicle_id in cart:
        cart.remove(vehicle_id)
        in_favorites = False
    else:
        cart.append(vehicle_id)
        in_favorites = True

    request.session['favorites'] = cart
    return render(request, 'parts/toggle_favorite.html', {'in_favorites': in_favorites, 'vehicle_id': vehicle_id})


def page(template):
    def wrapper(request, *args, **kwargs):
        context = load_global_context(request)
        return render(request, template, context)

    return wrapper


urlpatterns = [
    path('favicon.ico', RedirectView.as_view(url='/static/assets/favicon.ico', permanent=True)),
    path('', lambda r: render(r, 'home.html')),
    path('cart/', cart),
    path('catalog/', catalog),
    path('about/', about),
    path('checkout/', checkout),
    path('api/html/search_car_catalog/', car_catalog),
    path('api/html/text_search', lambda r: active_search(r, r.GET.get('search'))),
    path('api/html/toggle_cart', toggle_favorite),
    path('api/login', login),
    path('api/register', register),
]
