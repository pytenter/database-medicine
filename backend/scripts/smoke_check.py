import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django

django.setup()

from rest_framework.test import APIClient

from apps.inventory.models import Inventory
from apps.sales.models import SaleOrder


def expect(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    created_order_no = None
    before_quantity = None
    after_quantity = None
    try:
        client = APIClient(HTTP_HOST='localhost')

        response = client.post('/api/auth/login/', {'username': 'sysadmin', 'password': 'Admin@123'}, format='json')
        expect(response.status_code == 200, f'sysadmin login failed: {response.status_code}')
        access = response.json()['access']
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')

        me_response = client.get('/api/auth/me/')
        expect(me_response.status_code == 200, 'current user query failed')
        expect(me_response.json()['role'] == 'system_admin', 'sysadmin role mismatch')

        users_response = client.get('/api/users/')
        expect(users_response.status_code == 200, 'user list query failed')
        expect(len(users_response.json()) >= 3, 'seed user count is too small')

        medicine_response = client.get('/api/medicines/', {'search': 'Paracetamol'})
        expect(medicine_response.status_code == 200, 'medicine fuzzy query failed')
        expect(len(medicine_response.json()) >= 1, 'medicine fuzzy query returned no rows')

        inventory_response = client.get('/api/inventory/')
        expect(inventory_response.status_code == 200, 'inventory query failed')
        expect(len(inventory_response.json()) >= 1, 'inventory query returned no rows')

        client = APIClient(HTTP_HOST='localhost')
        response = client.post('/api/auth/login/', {'username': 'sales01', 'password': 'Admin@123'}, format='json')
        expect(response.status_code == 200, f'sales login failed: {response.status_code}')
        access = response.json()['access']
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')

        before_quantity = client.get('/api/inventory/', {'search': 'MED001'}).json()[0]['quantity']
        create_sale_response = client.post(
            '/api/sales/',
            {
                'customer_name': 'Smoke Script Customer',
                'remark': 'live smoke script',
                'items': [{'medicine_id': 1, 'quantity': 1}],
            },
            format='json',
        )
        expect(create_sale_response.status_code == 201, f'sale creation failed: {create_sale_response.status_code}')
        created_order_no = create_sale_response.json()['order_no']
        after_quantity = client.get('/api/inventory/', {'search': 'MED001'}).json()[0]['quantity']
        expect(after_quantity == before_quantity - 1, 'inventory deduction failed after sale creation')

        sales_response = client.get('/api/sales/', {'search': 'Smoke Script Customer'})
        expect(sales_response.status_code == 200, 'sales search failed')
        expect(any(item['order_no'] == created_order_no for item in sales_response.json()), 'sales search did not include the created order')

        print('Smoke check passed.')
        print(f'MED001 quantity: {before_quantity} -> {after_quantity}')
        print(f'Created order: {created_order_no}')
    finally:
        if created_order_no:
            order = SaleOrder.objects.filter(order_no=created_order_no).first()
            if order:
                inventory = Inventory.objects.filter(store=order.store, medicine_id=1).first()
                if inventory and before_quantity is not None:
                    inventory.quantity = before_quantity
                    inventory.save(update_fields=['quantity', 'updated_at'])
                order.delete()
                print(f'Cleanup completed for order: {created_order_no}')


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print(f'Smoke check failed: {exc}')
        sys.exit(1)
