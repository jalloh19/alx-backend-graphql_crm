import django_filters
from .models import Customer, Product, Order

class CustomerFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    email = django_filters.CharFilter(lookup_expr='icontains')
    createdAtGte = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    createdAtLte = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    phonePattern = django_filters.CharFilter(field_name='phone', lookup_expr='startswith')
    orderBy = django_filters.OrderingFilter(
        fields=(
            ('name', 'name'),
            ('created_at', 'createdAt'),
        )
    )

    class Meta:
        model = Customer
        fields = ['name', 'email', 'createdAtGte', 'createdAtLte', 'phonePattern', 'orderBy']

class ProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    priceGte = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    priceLte = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    stockGte = django_filters.NumberFilter(field_name='stock', lookup_expr='gte')
    stockLte = django_filters.NumberFilter(field_name='stock', lookup_expr='lte')
    orderBy = django_filters.OrderingFilter(
        fields=(
            ('name', 'name'),
            ('price', 'price'),
            ('stock', 'stock'),
        )
    )

    class Meta:
        model = Product
        fields = ['name', 'priceGte', 'priceLte', 'stockGte', 'stockLte', 'orderBy']


class OrderFilter(django_filters.FilterSet):
    totalAmountGte = django_filters.NumberFilter(field_name='total_amount', lookup_expr='gte')
    totalAmountLte = django_filters.NumberFilter(field_name='total_amount', lookup_expr='lte')
    orderDateGte = django_filters.DateTimeFilter(field_name='order_date', lookup_expr='gte')
    orderDateLte = django_filters.DateTimeFilter(field_name='order_date', lookup_expr='lte')
    customerName = django_filters.CharFilter(field_name='customer__name', lookup_expr='icontains')
    productName = django_filters.CharFilter(field_name='products__name', lookup_expr='icontains')
    productId = django_filters.NumberFilter(field_name='products__id')
    orderBy = django_filters.OrderingFilter(
        fields=(
            ('total_amount', 'totalAmount'),
            ('order_date', 'orderDate'),
        )
    )

    class Meta:
        model = Order
        fields = ['totalAmountGte', 'totalAmountLte', 'orderDateGte', 'orderDateLte', 'customerName', 'productName', 'productId', 'orderBy']
