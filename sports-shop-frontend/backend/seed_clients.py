from app import app, db, Client, Order, OrderItem, Product
import datetime, random

# 10 клиентов с разными итоговыми суммами
# (name, email, phone, целевая_сумма_покупок, число_заказов)
CLIENTS = [
    ("Иванов Иван Иванович",   "ivanov@mail.ru",   "+79001110001",  500,  1),
    ("Петрова Анна Сергеевна", "petrova@mail.ru",  "+79001110002",  345,  1),
    ("Сидоров Олег Петрович",  "sidorov@mail.ru",  "+79001110003", 12500, 4),
    ("Кузнецова Мария Игоревна","kuznetsova@mail.ru","+79001110004", 8900, 3),
    ("Смирнов Дмитрий Алексеевич","smirnov@mail.ru","+79001110005",  2100, 2),
    ("Волкова Екатерина Олеговна","volkova@mail.ru","+79001110006",  780,  1),
    ("Морозов Артём Викторович","morozov@mail.ru", "+79001110007", 3400,  2),
    ("Новикова Ольга Андреевна","novikova@mail.ru","+79001110008",  150,  1),
    ("Фёдоров Сергей Николаевич","fedorov@mail.ru","+79001110009", 6750,  3),
    ("Лебедева Виктория Павловна","lebedeva@mail.ru","+79001110010", 1990, 1),
]

def build_order(target_total, n_orders, products):
    """Раскладывает target_total на n_orders заказов из реальных товаров."""
    # пропорционально делим сумму
    parts = []
    base = target_total / n_orders
    for i in range(n_orders - 1):
        parts.append(round(base, 2))
    parts.append(round(target_total - sum(parts), 2))  # остаток в последний

    orders_data = []
    for order_total in parts:
        items = []
        remaining = order_total
        # жадно набираем товары
        pool = products[:]      # копия
        random.shuffle(pool)
        for p in pool:
            if remaining <= 0:
                break
            price = float(p.price)
            if price <= remaining:
                qty = 1
                # можем взять несколько штук дешёвых
                if price * 2 <= remaining and random.random() < 0.4:
                    qty = 2
                items.append((p, price, qty))
                remaining = round(remaining - price * qty, 2)
        # если остались копейки — округляем до целого последним товаром
        if items and remaining > 0:
            p, price, qty = items[-1]
            # корректируем количество так, чтобы выйти на order_total
            current = sum(pr * q for _, pr, q in items)
            diff = round(order_total - current, 2)
            # добавляем "сдачу" в виде ещё одной единицы дешёвого товара
            cheapest = min(products, key=lambda x: float(x.price))
            if float(cheapest.price) <= diff + float(cheapest.price):
                qty_add = int((diff + float(cheapest.price)) // float(cheapest.price))
                if qty_add > 0:
                    items.append((cheapest, float(cheapest.price), qty_add))
        orders_data.append(items)
    return orders_data

with app.app_context():
    products = Product.query.all()
    if not products:
        print("Сначала загрузите товары (products)!")
        exit(1)

    for full_name, email, phone, target_total, n_orders in CLIENTS:
        if Client.query.filter_by(email=email).first():
            print(f"Пропуск {full_name} — уже есть")
            continue

        client = Client(full_name=full_name, email=email, phone=phone)
        db.session.add(client)
        db.session.flush()  # получаем client.id

        orders_data = build_order(target_total, n_orders, products)
        for items in orders_data:
            order = Order(client_id=client.id, total=0)
            db.session.add(order)
            db.session.flush()
            order_total = 0
            for p, price, qty in items:
                oi = OrderItem(
                    order_id=order.id,
                    product_id=p.id,
                    product_name=p.name,
                    price=price,
                    quantity=qty,
                )
                db.session.add(oi)
                order_total += price * qty
            order.total = round(order_total, 2)

    db.session.commit()
    print("Готово: клиенты и заказы добавлены")
    # проверка
    for c in Client.query.all():
        total = sum(float(o.total) for o in c.orders)
        cnt = c.orders.count()
        print(f"{c.full_name:35} | заказов: {cnt:2} | сумма: {total:8.2f} ₽")