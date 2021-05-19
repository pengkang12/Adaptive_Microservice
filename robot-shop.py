import os
from locust import TaskSet, task, HttpUser, between
from random import choice
from random import randint
import time

def random_delay():
    time.sleep(1)

class WebsiteUser(HttpUser):
    wait_time = between(1, 50)
 
    def on_start(self):
        """ on_start is called when a Locust start before any task is scheduled """
        print('Starting')

    @task
    def login(self):
        credentials = {
                'name': 'user',
                'password': 'password'
                }
        res = self.client.post('/api/user/login', json=credentials, name="/api/user/login")
        #except:
        #    print("Error generated")
        print('login {}'.format(res.status_code))
    
    @task
    def load(self):
        self.client.get('/')
        user = self.client.get('/api/user/uniqueid', name="/api/user/uniqueid").json()
        uniqueid = user['uuid']
        print('User {}'.format(uniqueid))

        result = self.client.get('/api/catalogue/categories',name="/api/catalogue/categories/")
        response = self.client.get('/api/catalogue/products',name="/api/catalogue/product/")
        products = response.json() 
        for i in range(8):
            item = choice(products)
            while True:
                item = choice(products)
                if item['instock'] != 0:
                    break
                response = self.client.get('/api/catalogue/product/{}'.format(item['sku']),name="/api/catalogue/product")
                if response.status_code in [500, 502]:
                    time.sleep(2)
            # vote for item

            print("item ", item)
            if randint(1, 20) <= 1:
                response = self.client.put('/api/ratings/api/rate/{}/{}'.format(item['sku'], randint(1, 5)), name="/api/ratings/api/rate")
                if response.status_code in [500, 502]:
                    time.sleep(2)
            for i in range(20):
                response = self.client.get('/api/catalogue/product/{}'.format(item['sku']),name="/api/catalogue/product/")
                if response.status_code in [500, 502]:
                    time.sleep(2)
	
            for i in range(5): 
                response = self.client.get('/api/ratings/api/fetch/{}'.format(item['sku']),name="/api/ratings")
                if  response.status_code in [500, 502]:
                    time.sleep(2)

                response = self.client.get('/api/cart/add/{}/{}/1'.format(uniqueid, item['sku']),name="/api/cart/add")
                if response.status_code in [500, 502]:
                    time.sleep(2)
	
        response  = self.client.get('/api/cart/cart/{}'.format(uniqueid),name="/api/cart/cart")
        cart = None
        if  response.status_code in [500, 502]:
            time.sleep(3)
            response = self.client.get('/api/cart/cart/{}'.format(uniqueid),name="/api/cart/cart")
            if  response.status_code in [500, 502]:
                time.sleep(3)
                return 	
            cart = response.json() 
        cart = response.json()
        item = choice(cart['items'])
        response = self.client.get('/api/cart/update/{}/{}/2'.format(uniqueid, item['sku']),name="/api/cart/update")
        if response.status_code in [500, 502]:
            time.sleep(3)
        # country codes
        if randint(1, 8) <= 8:
            response = self.client.get('/api/shipping/codes', name="/api/shipping/codes")
            if  response.status_code in [500, 502]:
                time.sleep(3)
                return  		
            code = choice(response.json())
            city = None
            if randint(1, 2) <= 1:
                response = self.client.get('/api/shipping/cities/{}'.format(code['code']), name="/api/shipping/cites")
                if response.status_code in [500, 502]:
                    time.sleep(3)
                    city = {'uuid': 5381355, 'name': 'Olariu'}
                else:
                    city = choice(response.json())
            else:
                city = {'uuid': 5381355, 'name': 'Olariu'}
            print('code {} city {}'.format(code, city))
            response = self.client.get('/api/shipping/calc/{}'.format(city['uuid']), name="/api/shipping/calc") 
            if response.status_code in [500, 502]:
                time.sleep(3)
                shipping = {'distance': 7360, 'cost': 368.0, 'location': 'Canada Skookumchuck'}
            else:
                shipping = response.json()
        else:
            shipping = {'distance': 7360, 'cost': 368.0, 'location': 'Canada Skookumchuck'}
        print('Shipping {}'.format(shipping)) 
 	# POST
        if randint(1, 15) <= 15:
            response = self.client.post('/api/shipping/confirm/{}'.format(uniqueid), json=shipping, name="/api/shipping/confirm") 
            if response.status_code in [500, 502]:
                time.sleep(3)
                return 
            cart = response.json()
            print('Final cart {}'.format(cart))
            if randint(1, 3) <= 3:
                response = self.client.post('/api/payment/pay/{}'.format(uniqueid), json=cart, name="/api/payment/pay")
                if response.status_code in [500, 502]:
                    time.sleep(3)
                    return 
                order = response.json()
                print('Order {}'.format(order))

    @task
    def error(self):
        if 'ERROR' in os.environ and os.environ['ERROR'] == '1':
            print('Error request')
            cart = {'total': 0, 'tax': 0}
            self.client.post('/api/payment/pay/partner-57', json=cart, name='/api/payment/pay')


   
