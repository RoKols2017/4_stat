from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import SalesRecord
import pandas as pd
from django.urls import reverse
from django.db.models import Q

# Загрузка CSV
from django.views.decorators.csrf import csrf_exempt

def upload_csv(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        try:
            df = pd.read_csv(file)
            required_cols = {'date', 'region', 'product', 'quantity', 'revenue'}
            if not required_cols.issubset(df.columns):
                raise ValueError('CSV должен содержать столбцы: date, region, product, quantity, revenue')
            # Проверка типов
            df['date'] = pd.to_datetime(df['date'], errors='raise').dt.date
            df['region'] = df['region'].astype(str)
            df['product'] = df['product'].astype(str)
            df['quantity'] = df['quantity'].astype(int)
            df['revenue'] = df['revenue'].astype(float)
            # Проверка на дубли
            for _, row in df.iterrows():
                if not SalesRecord.objects.filter(date=row['date'], region=row['region'], product=row['product']).exists():
                    SalesRecord.objects.create(
                        date=row['date'],
                        region=row['region'],
                        product=row['product'],
                        quantity=row['quantity'],
                        revenue=row['revenue']
                    )
            return redirect(reverse('sales:dashboard'))
        except Exception as e:
            return render(request, 'sales/upload.html', {'error': str(e)})
    return render(request, 'sales/upload.html')

# Дашборд с аналитикой

def dashboard(request):
    # Фильтры
    qs = SalesRecord.objects.all()
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    region = request.GET.get('region')
    product = request.GET.get('product')
    if date_from:
        qs = qs.filter(date__gte=date_from)
    if date_to:
        qs = qs.filter(date__lte=date_to)
    if region:
        qs = qs.filter(region__icontains=region)
    if product:
        qs = qs.filter(product__icontains=product)
    records = qs
    total_revenue = sum(r.revenue for r in records)
    total_quantity = sum(r.quantity for r in records)
    df = pd.DataFrame(list(records.values('date', 'revenue', 'quantity')))
    if not df.empty:
        df_grouped = df.groupby('date').agg({'revenue': 'sum', 'quantity': 'sum'}).reset_index()
        dates = df_grouped['date'].astype(str).tolist()
        revenues = df_grouped['revenue'].tolist()
        quantities = df_grouped['quantity'].tolist()
    else:
        dates, revenues, quantities = [], [], []
    # Для фильтров
    all_regions = SalesRecord.objects.values_list('region', flat=True).distinct()
    all_products = SalesRecord.objects.values_list('product', flat=True).distinct()
    return render(request, 'sales/dashboard.html', {
        'records': records,
        'total_revenue': total_revenue,
        'total_quantity': total_quantity,
        'dates': dates,
        'revenues': revenues,
        'quantities': quantities,
        'date_from': date_from or '',
        'date_to': date_to or '',
        'region': region or '',
        'product': product or '',
        'all_regions': all_regions,
        'all_products': all_products,
    })

# Экспорт отчёта

def export_report(request):
    qs = SalesRecord.objects.all()
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    region = request.GET.get('region')
    product = request.GET.get('product')
    if date_from:
        qs = qs.filter(date__gte=date_from)
    if date_to:
        qs = qs.filter(date__lte=date_to)
    if region:
        qs = qs.filter(region__icontains=region)
    if product:
        qs = qs.filter(product__icontains=product)
    records = qs.values()
    df = pd.DataFrame(records)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sales_report.csv"'
    df.to_csv(path_or_buf=response, index=False)
    return response

def home(request):
    return render(request, 'home.html')

def top_products(request):
    qs = SalesRecord.objects.all()
    df = pd.DataFrame(list(qs.values('product', 'revenue')))
    top = []
    if not df.empty:
        top = df.groupby('product')['revenue'].sum().sort_values(ascending=False).head(5).reset_index().to_dict('records')
    return render(request, 'sales/top_products.html', {'top': top})

def top_regions(request):
    qs = SalesRecord.objects.all()
    df = pd.DataFrame(list(qs.values('region', 'revenue')))
    top = []
    if not df.empty:
        top = df.groupby('region')['revenue'].sum().sort_values(ascending=False).head(5).reset_index().to_dict('records')
    return render(request, 'sales/top_regions.html', {'top': top})

def avg_receipt(request):
    qs = SalesRecord.objects.all()
    total_revenue = sum(r.revenue for r in qs)
    total_quantity = sum(r.quantity for r in qs)
    avg = total_revenue / total_quantity if total_quantity else 0
    return render(request, 'sales/avg_receipt.html', {'avg': avg})

def monthly_dynamics(request):
    qs = SalesRecord.objects.all()
    df = pd.DataFrame(list(qs.values('date', 'revenue', 'quantity')))
    months, revenues, quantities = [], [], []
    if not df.empty:
        df['month'] = pd.to_datetime(df['date']).dt.to_period('M').astype(str)
        grouped = df.groupby('month').agg({'revenue': 'sum', 'quantity': 'sum'}).reset_index()
        months = grouped['month'].tolist()
        revenues = grouped['revenue'].tolist()
        quantities = grouped['quantity'].tolist()
    return render(request, 'sales/monthly_dynamics.html', {'months': months, 'revenues': revenues, 'quantities': quantities})

def pie_products(request):
    qs = SalesRecord.objects.all()
    df = pd.DataFrame(list(qs.values('product', 'revenue')))
    labels, values = [], []
    if not df.empty:
        grouped = df.groupby('product')['revenue'].sum().reset_index()
        labels = grouped['product'].tolist()
        values = grouped['revenue'].tolist()
    return render(request, 'sales/pie_products.html', {'labels': labels, 'values': values})

def pie_regions(request):
    qs = SalesRecord.objects.all()
    df = pd.DataFrame(list(qs.values('region', 'revenue')))
    labels, values = [], []
    if not df.empty:
        grouped = df.groupby('region')['revenue'].sum().reset_index()
        labels = grouped['region'].tolist()
        values = grouped['revenue'].tolist()
    return render(request, 'sales/pie_regions.html', {'labels': labels, 'values': values})
