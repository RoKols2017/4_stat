from django.test import TestCase, Client
from .models import SalesRecord
from django.urls import reverse
import io
import pandas as pd

# Create your tests here.

class SalesTests(TestCase):
    def setUp(self):
        SalesRecord.objects.create(date='2024-01-01', region='Москва', product='Товар1', quantity=10, revenue=1000)
        SalesRecord.objects.create(date='2024-01-02', region='Питер', product='Товар2', quantity=5, revenue=500)

    def test_dashboard_metrics(self):
        c = Client()
        resp = c.get(reverse('sales:dashboard'))
        self.assertContains(resp, 'Суммарная выручка: 1500')
        self.assertContains(resp, 'Количество продаж: 15')

    def test_filter_region(self):
        c = Client()
        resp = c.get(reverse('sales:dashboard'), {'region': 'Москва'})
        self.assertContains(resp, 'Москва')
        self.assertNotContains(resp, 'Питер')

    def test_upload_csv(self):
        c = Client()
        csv = 'date,region,product,quantity,revenue\n2024-01-03,Казань,Товар3,7,700\n'
        resp = c.post(reverse('sales:upload_csv'), {'file': io.StringIO(csv)}, follow=True)
        self.assertTrue(SalesRecord.objects.filter(region='Казань').exists())
