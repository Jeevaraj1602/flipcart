from flask import Flask, render_template, request, redirect, url_for, session
from data import products

app = Flask(__name__)
app.secret_key = "dev-secret-key-change-later"

# ---------- Helpers ----------
def get_cart():
    return session.get('cart', {})

def get_product(product_id):
    return next((p for p in products if p['id'] == product_id), None)

@app.context_processor
def inject_cart_count():
    cart = get_cart()
    count = sum(cart.values())
    return {'cart_count': count}

# ---------- Routes ----------
@app.route('/')
def home():
    query = request.args.get('q', '').strip().lower()
    category = request.args.get('category', 'All')
    sort = request.args.get('sort', '')

    filtered = products

    if query:
        filtered = [p for p in filtered if query in p['name'].lower()]

    if category and category != 'All':
        filtered = [p for p in filtered if p['category'] == category]

    if sort == 'low_high':
        filtered = sorted(filtered, key=lambda p: p['price'])
    elif sort == 'high_low':
        filtered = sorted(filtered, key=lambda p: p['price'], reverse=True)
    elif sort == 'rating':
        filtered = sorted(filtered, key=lambda p: p['rating'], reverse=True)

    categories = sorted(set(p['category'] for p in products))

    return render_template(
        'home.html',
        products=filtered,
        query=query,
        categories=categories,
        selected_category=category,
        selected_sort=sort
    )

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = get_product(product_id)
    return render_template('product_detail.html', product=product)

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    cart = get_cart()
    key = str(product_id)
    cart[key] = cart.get(key, 0) + 1
    session['cart'] = cart
    return redirect(url_for('cart'))

@app.route('/buy_now/<int:product_id>', methods=['POST'])
def buy_now(product_id):
    # Adds the item, then checks out ONLY this item (not the whole cart)
    cart = get_cart()
    key = str(product_id)
    cart[key] = cart.get(key, 0) + 1
    session['cart'] = cart
    session['checkout_ids'] = [key]
    return redirect(url_for('checkout'))

@app.route('/cart')
def cart():
    cart = get_cart()
    cart_items = []
    total = 0
    for pid_str, qty in cart.items():
        product = get_product(int(pid_str))
        if product:
            subtotal = product['price'] * qty
            total += subtotal
            cart_items.append({**product, 'qty': qty, 'subtotal': subtotal})
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/update_cart/<int:product_id>', methods=['POST'])
def update_cart(product_id):
    action = request.form.get('action')
    cart = get_cart()
    key = str(product_id)
    if key in cart:
        if action == 'increase':
            cart[key] += 1
        elif action == 'decrease':
            cart[key] -= 1
            if cart[key] <= 0:
                del cart[key]
    session['cart'] = cart
    return redirect(url_for('cart'))
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return redirect(url_for('home'))

    return render_template('login.html')

@app.route('/remove_from_cart/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    cart = get_cart()
    key = str(product_id)
    if key in cart:
        del cart[key]
    session['cart'] = cart
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    cart = get_cart()

    if request.method == 'POST':
        # Came from cart page with specific checkboxes selected
        selected_ids = request.form.getlist('selected_items')
    else:
        # Came from Buy Now (session has exactly 1 id) or direct GET
        selected_ids = session.get('checkout_ids', list(cart.keys()))

    cart_items = []
    total = 0
    for pid_str in selected_ids:
        qty = cart.get(pid_str)
        if not qty:
            continue
        product = get_product(int(pid_str))
        if product:
            subtotal = product['price'] * qty
            total += subtotal
            cart_items.append({**product, 'qty': qty, 'subtotal': subtotal})

    if not cart_items:
        return redirect(url_for('cart'))

    session['checkout_ids'] = selected_ids  # remember for place_order
    return render_template('checkout.html', cart_items=cart_items, total=total)

@app.route('/place_order', methods=['POST'])
def place_order():
    payment_method = request.form.get('payment_method', 'Cash on Delivery')
    checkout_ids = session.get('checkout_ids', [])
    cart = get_cart()
    # Only remove the items that were actually checked out, not the whole cart
    for pid in checkout_ids:
        cart.pop(pid, None)
    session['cart'] = cart
    session.pop('checkout_ids', None)
    return render_template('order_success.html', payment_method=payment_method)

if __name__ == '__main__':
    app.run(debug=True)