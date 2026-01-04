import graphene
from graphene_django import DjangoObjectType
from .models import Customer, Product, Order
import re

class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = ("id", "name", "email", "phone")

class ProductType(DjangoObjectType):
    class Meta:
        model = Product

class OrderType(DjangoObjectType):
    class Meta:
        model = Order

class CreateCustomer(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String()

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    def mutate(self, info, name, email, phone=None):
        # Validate email uniqueness
        if Customer.objects.filter(email=email).exists():
            raise Exception("Email already exists")

        # Validate phone format
        if phone and not re.match(r'^\+?1?\d{9,15}$', phone) and not re.match(r'^\d{3}-\d{3}-\d{4}$', phone):
             raise Exception("Invalid phone format")

        customer = Customer(name=name, email=email, phone=phone)
        customer.save()

        return CreateCustomer(customer=customer, message="Customer created successfully")

class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()

class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    def mutate(self, info, input):
        customers_to_create = []
        errors = []
        
        # Validate all first
        for data in input:
            name = data.name
            email = data.email
            phone = data.get('phone')

            if Customer.objects.filter(email=email).exists():
                errors.append(f"Email {email} already exists")
                continue
            
            if phone and not re.match(r'^\+?1?\d{9,15}$', phone) and not re.match(r'^\d{3}-\d{3}-\d{4}$', phone):
                errors.append(f"Invalid phone format for {name}")
                continue

            customers_to_create.append(Customer(name=name, email=email, phone=phone))

        # Bulk create valid ones
        if customers_to_create:
            Customer.objects.bulk_create(customers_to_create)
            # Re-fetch to get IDs (sqlite doesn't return IDs on bulk_create usually, but let's see if we can just return the objects or query them back)
            # For simplicity and correctness with IDs, we might need to query them back or save one by one if we need IDs immediately returned and DB doesn't support it.
            # However, the requirement says "Creates customers in a single transaction".
            # Let's just return the objects we created (they might not have IDs populated depending on DB backend).
            # Actually, Django 4.0+ bulk_create sets primary keys on SQLite. We are on Django 4.2.7.
            pass

        return BulkCreateCustomers(customers=customers_to_create, errors=errors)

class CreateProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        price = graphene.Decimal(required=True)
        stock = graphene.Int()

    product = graphene.Field(ProductType)

    def mutate(self, info, name, price, stock=0):
        if price <= 0:
            raise Exception("Price must be positive")
        if stock < 0:
            raise Exception("Stock cannot be negative")

        product = Product(name=name, price=price, stock=stock)
        product.save()
        return CreateProduct(product=product)

class CreateOrder(graphene.Mutation):
    class Arguments:
        customer_id = graphene.ID(required=True)
        product_ids = graphene.List(graphene.ID, required=True)

    order = graphene.Field(OrderType)

    def mutate(self, info, customer_id, product_ids):
        try:
            customer = Customer.objects.get(pk=customer_id)
        except Customer.DoesNotExist:
            raise Exception("Invalid customer ID")

        if not product_ids:
            raise Exception("At least one product is required")

        products = Product.objects.filter(pk__in=product_ids)
        if len(products) != len(set(product_ids)):
             raise Exception("One or more product IDs are invalid")

        total_amount = sum(product.price for product in products)

        order = Order(customer=customer, total_amount=total_amount)
        order.save()
        order.products.set(products)
        
        return CreateOrder(order=order)

class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()

class Query(graphene.ObjectType):
    hello = graphene.String(default_value="Hello, GraphQL!")
    all_customers = graphene.List(CustomerType)

    def resolve_hello(self, info):
        return "Hello, GraphQL!"

    def resolve_all_customers(self, info):
        return Customer.objects.all()
