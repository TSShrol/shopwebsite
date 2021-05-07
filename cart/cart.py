from decimal import Decimal
from django.conf import settings
from shop.models import Product

class Cart(object):
    def __init__(self, request):
        #Ініціалізація обєкта корзини
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            #Зберігаємо в сесії пусту корзину
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1, update_quantity=False):
        #Додавання товару в корзину або поновлення його кількості
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0, 'price': str(product.price)}
        if update_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    def save(self):
        # Визначаємо сесію, як така, що була змінена
        self.session.modified = True

    def remove(self, product):
        # Видалення товарів із корзини
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        #Проходимо по товарам корзини і отримуємо відповідні обєкти Product
        product_ids = self.cart.keys()
        # Отримуємо обєкти моделі Product  і передаємо їх в корзину
        products = Product.objects.filter(id__in=product_ids)
        print(products)
        cart = self.cart.copy()
        for product in products:
            cart[str(product.id)]['product'] = product
        for item in cart.values():
            # print(item['product'])
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        # Повертаємо загальну кількість товарів в корзині
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        return sum(
            Decimal(item['price']) * item['quantity']
            for item in self.cart.values()
        )

    def clear(self):
        # Очищаємо корзину
        del self.session[settings.CART_SESSION_ID]
        self.save()

    def __str__(self):
        return str(self.cart)