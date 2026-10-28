from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import bcrypt
import jwt
import datetime
import os
from functools import wraps
from werkzeug.utils import secure_filename
from sqlalchemy import func

app = Flask(__name__)
CORS(app, supports_credentials=True)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:100Osman_%40@localhost/Emir_i'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'sport_secret_key_12345'

db = SQLAlchemy(app)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ================== МОДЕЛИ ==================

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(255))


class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(255))
    category = db.Column(db.String(100))
    stock = db.Column(db.Integer, default=0)


class Cart(db.Model):
    __tablename__ = 'cart'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    quantity = db.Column(db.Integer, default=1)


class Client(db.Model):
    __tablename__ = 'clients'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    phone = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    orders = db.relationship('Order', backref='client', lazy='dynamic')


class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    total = db.Column(db.Numeric(12, 2), default=0)

    items = db.relationship('OrderItem', backref='order', lazy='dynamic',
                            cascade='all, delete-orphan')


class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    product_name = db.Column(db.String(255))
    price = db.Column(db.Numeric(10, 2), nullable=False)
    quantity = db.Column(db.Integer, default=1)

    product = db.relationship('Product')


# ================== ДЕКОРАТОРЫ ==================

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Токен отсутствует'}), 401
        try:
            token = token.split(' ')[1]
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])
        except:
            return jsonify({'message': 'Токен недействителен'}), 401
        return f(current_user, *args, **kwargs)
    return decorated


# ================== ТОВАРЫ ==================

@app.route('/api/products', methods=['GET'])
def get_products():
    """
    sort       = price | name         (default name)
    order      = asc | desc           (default asc)
    price_min  = нижняя граница (включительно)
    price_max  = верхняя граница (включительно)
    price_from = только «от»
    price_to   = только «до»
    cheap      = 1  → только < 100 ₽
    category   = фильтр по категории
    """
    sort = request.args.get('sort', 'name')
    order = request.args.get('order', 'asc')
    desc = (order == 'desc')

    q = Product.query

    if request.args.get('cheap') == '1':
        q = q.filter(Product.price < 100)
    else:
        pmin = request.args.get('price_min') or request.args.get('price_from')
        pmax = request.args.get('price_max') or request.args.get('price_to')
        if pmin not in (None, ''):
            q = q.filter(Product.price >= float(pmin))
        if pmax not in (None, ''):
            q = q.filter(Product.price <= float(pmax))

    cat = request.args.get('category')
    if cat:
        q = q.filter(Product.category == cat)

    if sort == 'price':
        q = q.order_by(Product.price.desc() if desc else Product.price.asc())
    else:
        q = q.order_by(Product.name.desc() if desc else Product.name.asc())

    products = q.all()
    result = [{
        'id': p.id,
        'name': p.name,
        'price': float(p.price),
        'description': p.description,
        'image_url': p.image_url,
        'category': p.category,
        'stock': p.stock,
    } for p in products]
    return jsonify(result)


@app.route('/api/categories', methods=['GET'])
def get_categories():
    rows = db.session.query(Product.category).distinct().all()
    return jsonify(sorted([r[0] for r in rows if r[0]]))


@app.route('/api/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/api/upload', methods=['POST'])
@token_required
def upload_file(current_user):
    if 'file' not in request.files:
        return jsonify({'message': 'Нет файла'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'Файл не выбран'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        name, ext = os.path.splitext(filename)
        filename = f"{datetime.datetime.now().timestamp()}_{name}{ext}"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return jsonify({'filename': filename}), 200
    return jsonify({'message': 'Недопустимый тип файла'}), 400


# ================== КЛИЕНТЫ ==================

@app.route('/api/clients', methods=['GET'])
def get_clients():
    """
    sort  = name | total | count   (default name)
    order = asc | desc             (default asc)
    """
    sort = request.args.get('sort', 'name')
    order = request.args.get('order', 'asc')
    desc = (order == 'desc')

    total_expr = func.coalesce(func.sum(Order.total), 0)
    count_expr = func.count(Order.id)

    rows = (
        db.session.query(
            Client.id,
            Client.full_name,
            Client.email,
            Client.phone,
            count_expr.label('orders_count'),
            total_expr.label('total_spent'),
        )
        .outerjoin(Order, Order.client_id == Client.id)
        .group_by(Client.id)
    )

    if sort == 'name':
        rows = rows.order_by(Client.full_name.desc() if desc else Client.full_name.asc())
    elif sort == 'total':
        rows = rows.order_by(total_expr.desc() if desc else total_expr.asc())
    elif sort == 'count':
        rows = rows.order_by(count_expr.desc() if desc else count_expr.asc())
    else:
        return jsonify({'message': 'Неизвестный sort'}), 400

    result = [{
        'id': r.id,
        'full_name': r.full_name,
        'email': r.email,
        'phone': r.phone,
        'orders_count': r.orders_count,
        'total_spent': float(r.total_spent),
    } for r in rows]
    return jsonify(result)


@app.route('/api/clients/<int:client_id>/orders', methods=['GET'])
def get_client_orders(client_id):
    client = Client.query.get(client_id)
    if not client:
        return jsonify({'message': 'Клиент не найден'}), 404

    orders = Order.query.filter_by(client_id=client_id).order_by(Order.created_at.desc()).all()
    result = []
    for o in orders:
        items = [{
            'product_id': it.product_id,
            'product_name': it.product_name,
            'price': float(it.price),
            'quantity': it.quantity,
            'line_total': float(it.price) * it.quantity,
        } for it in o.items]
        result.append({
            'id': o.id,
            'created_at': o.created_at.isoformat() if o.created_at else None,
            'total': float(o.total),
            'items': items,
        })

    total = sum(float(o.total) for o in orders)
    return jsonify({
        'client': {
            'id': client.id,
            'full_name': client.full_name,
            'email': client.email,
            'phone': client.phone,
        },
        'orders_count': len(orders),
        'total_spent': total,
        'orders': result,
    })


# ================== АУТЕНТИФИКАЦИЯ ==================

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    full_name = data.get('full_name')
    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'Пользователь уже существует'}), 400
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    new_user = User(email=email, password_hash=hashed.decode('utf-8'), full_name=full_name)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'Регистрация успешна'}), 201


@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'message': 'Пользователь не найден'}), 404
    if bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, app.config['SECRET_KEY'])
        return jsonify({'message': 'Вход выполнен', 'token': token, 'user_id': user.id}), 200
    else:
        return jsonify({'message': 'Неверный пароль'}), 401


# ================== КОРЗИНА ==================

@app.route('/api/cart', methods=['GET'])
@token_required
def get_cart(current_user):
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()
    result = []
    total = 0
    for item in cart_items:
        product = Product.query.get(item.product_id)
        if product:
            item_total = float(product.price) * item.quantity
            total += item_total
            result.append({
                'id': item.id,
                'product_id': product.id,
                'name': product.name,
                'price': float(product.price),
                'quantity': item.quantity,
                'total': item_total,
                'image_url': product.image_url,
            })
    return jsonify({'items': result, 'total': total})


@app.route('/api/cart/add', methods=['POST'])
@token_required
def add_to_cart(current_user):
    data = request.json
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)
    cart_item = Cart.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = Cart(user_id=current_user.id, product_id=product_id, quantity=quantity)
        db.session.add(cart_item)
    db.session.commit()
    return jsonify({'message': 'Товар добавлен в корзину'}), 200


@app.route('/api/cart/remove/<int:product_id>', methods=['DELETE'])
@token_required
def remove_from_cart(current_user, product_id):
    cart_item = Cart.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if not cart_item:
        return jsonify({'message': 'Товар не найден в корзине'}), 404
    db.session.delete(cart_item)
    db.session.commit()
    return jsonify({'message': 'Товар удалён из корзины'}), 200


@app.route('/api/cart/update/<int:product_id>', methods=['PUT'])
@token_required
def update_cart_quantity(current_user, product_id):
    data = request.json
    quantity = data.get('quantity', 1)
    if quantity <= 0:
        return remove_from_cart(current_user, product_id)
    cart_item = Cart.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if not cart_item:
        return jsonify({'message': 'Товар не найден в корзине'}), 404
    cart_item.quantity = quantity
    db.session.commit()
    return jsonify({'message': 'Количество обновлено'}), 200


# ================== АДМИН: ТОВАРЫ ==================

@app.route('/api/admin/products', methods=['POST'])
@token_required
def add_product(current_user):
    data = request.json
    new_product = Product(
        name=data['name'],
        price=data['price'],
        description=data.get('description', ''),
        image_url=data.get('image_url', ''),
        category=data.get('category', ''),
        stock=data.get('stock', 0),
    )
    db.session.add(new_product)
    db.session.commit()
    return jsonify({'message': 'Товар добавлен', 'id': new_product.id}), 201


@app.route('/api/admin/products/<int:product_id>', methods=['PUT'])
@token_required
def update_product(current_user, product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'message': 'Товар не найден'}), 404
    data = request.json
    product.name = data.get('name', product.name)
    product.price = data.get('price', product.price)
    product.description = data.get('description', product.description)
    product.image_url = data.get('image_url', product.image_url)
    product.category = data.get('category', product.category)
    product.stock = data.get('stock', product.stock)
    db.session.commit()
    return jsonify({'message': 'Товар обновлён'}), 200


@app.route('/api/admin/products/<int:product_id>', methods=['DELETE'])
@token_required
def delete_product(current_user, product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'message': 'Товар не найден'}), 404
    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Товар удалён'}), 200


if __name__ == '__main__':
    app.run(debug=True, port=5000)