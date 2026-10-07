import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from app import app


class FlipcartTestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    # TC1 - Verify Home Page Loads
    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    # TC2 - Verify Product Search
    def test_product_search(self):
        response = self.client.get('/?q=Samsung')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Samsung Galaxy', response.data)

    # TC3 - Verify Category Filtering
    def test_category_filter(self):
        response = self.client.get('/?category=Electronics')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Wireless Headphones', response.data)

    # TC4 - Verify Price Sorting
    def test_price_sorting(self):
        response = self.client.get('/?sort=low_high')
        self.assertEqual(response.status_code, 200)

    # TC5 - Verify Product Details
    def test_product_details(self):
        response = self.client.get('/product/1')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Wireless Headphones', response.data)

    # TC6 - Verify Add Product To Cart
    def test_add_to_cart(self):
        response = self.client.post('/add_to_cart/1')
        self.assertEqual(response.status_code, 302)

        response = self.client.get('/cart')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Wireless Headphones', response.data)

    # TC7 - Verify Increase Cart Quantity
    def test_increase_cart_quantity(self):
        with self.client.session_transaction() as session:
            session['cart'] = {'1': 1}

        response = self.client.post(
            '/update_cart/1',
            data={'action': 'increase'}
        )

        self.assertEqual(response.status_code, 302)

        with self.client.session_transaction() as session:
            self.assertEqual(session['cart']['1'], 2)

    # TC8 - Verify Remove Product From Cart
    def test_remove_from_cart(self):
        with self.client.session_transaction() as session:
            session['cart'] = {'1': 1}

        response = self.client.post('/remove_from_cart/1')

        self.assertEqual(response.status_code, 302)

        with self.client.session_transaction() as session:
            self.assertNotIn('1', session['cart'])

    # TC9 - Verify Login Page Loads
    def test_login_page(self):
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)

    # TC10 - Verify Checkout And Place Order
    def test_checkout_and_place_order(self):
        with self.client.session_transaction() as session:
            session['cart'] = {'1': 1}

        response = self.client.get('/checkout')
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            '/place_order',
            data={'payment_method': 'Cash on Delivery'}
        )

        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()

