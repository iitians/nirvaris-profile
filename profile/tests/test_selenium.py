import pdb

from datetime import date, timedelta

from django.contrib.auth.models import User
from django.core import mail
from django.core.urlresolvers import reverse
from django.test import LiveServerTestCase

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

from .commons import create_user_jack
from ..crypto import user_activation_token
from ..views import MAX_TOKEN_DAYS, AFTER_LOGIN_URL

class SeleniumTestCase(LiveServerTestCase):
    
    @classmethod
    def setUpClass(cls):
        super(SeleniumTestCase, cls).setUpClass()
        cls.browser = webdriver.Firefox()
        cls.site_url = cls.live_server_url
    
    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super(SeleniumTestCase, cls).tearDownClass() 

    def _login(self, with_email=False):
        
        jack_user = create_user_jack(active=True)

        browser = self.browser
        
        browser.get(self.site_url + reverse('login'))

        input_login = WebDriverWait(browser, 10).until( lambda browser: browser.find_element_by_xpath("//input[@id='id_email_or_username']"))

        input_password = WebDriverWait(browser, 10).until( lambda browser: browser.find_element_by_xpath("//input[@id='id_password']"))
        
        input_login.clear()
        if with_email:
            input_login.send_keys(jack_user.email)
        else:
            input_login.send_keys(jack_user.username)
    
        input_password.clear()
        input_password.send_keys('pass')
        
        submit_button = WebDriverWait(browser, 10).until( lambda browser: browser.find_element_by_xpath("//input[@type='submit']"))
        
        submit_button.click()
        
        return jack_user
    
    def _logout(self):

        browser = self.browser
        
        browser.get(self.site_url + reverse('logout'))
    
    def test_logout(self):

        jack_user = self._login()
        
        self._logout()

        self.assertIn(reverse('login'),self.browser.current_url)

    def test_change_user_password(self):

        jack_user = self._login()
        
        # pdb.set_trace()
        
        browser = self.browser
        
        browser.get(self.site_url + reverse('change-password'))

        input_current_password = WebDriverWait(browser, 10).until( lambda browser: browser.find_element_by_xpath("//input[@id='id_current_password']"))

        input_new_password = WebDriverWait(browser, 10).until( lambda browser: browser.find_element_by_xpath("//input[@id='id_new_password']"))
        
        input_confirm_new_password = WebDriverWait(browser, 10).until( lambda browser: browser.find_element_by_xpath("//input[@id='id_confirm_new_password']"))        

        #pdb.set_trace()
    
        self.assertEquals('',input_current_password.get_attribute('value'), 'user First name does not match')
        self.assertEquals('',input_new_password.get_attribute('value'), 'user Email does not match')        
        self.assertEquals('',input_confirm_new_password.get_attribute('value'), 'user username does not match') 
        
        submit_button = WebDriverWait(browser, 10).until( lambda browser: browser.find_element_by_xpath("//input[@type='submit']"))

        input_current_password.clear()
        input_current_password.send_keys('pass') 
        
        input_new_password.clear()
        input_new_password.send_keys('new_pass')
        
        input_confirm_new_password.clear()
        input_confirm_new_password.send_keys('new_pass')
        
        submit_button.click() 
        
        self.assertTrue(User.objects.filter(username=jack_user.username).exists(),'User was not registered')

        cahnged_user = User.objects.get(username=jack_user.username)
        
        self.assertTrue(cahnged_user.check_password('new_pass'),'user First name does not match')

    def test_change_user_details(self):

        jack_user = self._login()
        
        # pdb.set_trace()
        
        browser = self.browser
        
        browser.get(self.site_url + reverse('change-user-details'))

        input_name = WebDriverWait(browser, 10).until( lambda browser: browser.find_element_by_xpath("//input[@id='id_name']"))
        
        input_email = WebDriverWait(browser, 10).until( lambda browser: browser.find_element_by_xpath("//input[@id='id_email']"))
        
        input_username = WebDriverWait(browser, 10).until( lambda browser: browser.find_element_by_xpath("//input[@id='id_username']"))
        
        input_password = WebDriverWait(browser, 10).until( lambda browser: browser.find_element_by_xpath("//input[@id='id_current_password']"))

        #pdb.set_trace()
    
        self.assertEquals(jack_user.get_full_name(),input_name.get_attribute('value'), 'user First name does not match')
        self.assertEquals(jack_user.email,input_email.get_attribute('value'), 'user Email does not match')        
        self.assertEquals(jack_user.username,input_username.get_attribute('value'), 'user username does not match') 
        

        
        submit_button = WebDriverWait(browser, 10).until( lambda browser: browser.find_element_by_xpath("//input[@type='submit']"))

        input_name.clear()
        input_name.send_keys('JackD Changed Roll') 
        
        input_email.clear()
        input_email.send_keys('jackroll@awesome.com')
        
        input_username.clear()
        input_username.send_keys('jackroll')
        
        input_password.clear()
        input_password.send_keys('pass')
        
        submit_button.click() 
        
        self.assertTrue(User.objects.filter(username='jackroll').exists(),'User was not registered')

        cahnged_user = User.objects.get(username='jackroll')
        
        self.assertEquals(cahnged_user.first_name,'JackD','user First name does not match')
        self.assertEquals(cahnged_user.last_name,'Changed Roll','user Last name does not match')
        self.assertEquals(cahnged_user.email,'jackroll@awesome.com','user Email does not match')        
        self.assertEquals(cahnged_user.username,'jackroll','user username does not match')          
                
    def test_login_email(self):
        
        jack_user = self._login(with_email=True)
        
        self.assertIn(AFTER_LOGIN_URL, self.browser.current_url)

    def test_login_username(self):
        
        jack_user = self._login()

        #pdb.set_trace()
        self.assertIn(AFTER_LOGIN_URL, self.browser.current_url)
        

    def test_forgot_password(self):

        mail.outbox = []
        
        jack_user = create_user_jack(True)
        
        browser = self.browser
        
        browser.get(self.site_url + reverse('forgot-password'))

        input_name = WebDriverWait(browser, 10).until( lambda browser: browser.find_element_by_xpath("//input[@id='id_email']"))
        
        input_name.clear()
        input_name.send_keys(jack_user.email)
    
        submit_button = WebDriverWait(browser, 10).until( lambda browser: browser.find_element_by_xpath("//input[@type='submit']"))                
        
        submit_button.click()
        
        self.assertEqual(len(mail.outbox), 1,'It should sent an email')

    def test_resend_activation_email(self):

        mail.outbox = []
        
        jack_user = create_user_jack()
        
        browser = self.browser
        
        browser.get(self.site_url + reverse('resend-activation-email'))

        input_name = WebDriverWait(browser, 10).until( lambda browser: browser.find_element_by_xpath("//input[@id='id_email']"))
        
        input_name.clear()
        input_name.send_keys(jack_user.email)
    
        submit_button = WebDriverWait(browser, 10).until( lambda browser: browser.find_element_by_xpath("//input[@type='submit']"))                
        
        submit_button.click()
        
        self.assertEqual(len(mail.outbox), 1,'It should sent an email')
        
    def test_expired_activation_link(self):
        
        jack_user = create_user_jack()
        
        due_date = date.today()-timedelta(days=int(MAX_TOKEN_DAYS)+1)        
        
        activation_token = user_activation_token(jack_user.username, jack_user.email, due_date)
        
        url_to_activate =self.site_url + reverse('activation',kwargs={'token': str(activation_token)})
        
        browser = self.browser
        
        browser.get(url_to_activate)

        self.assertFalse(User.objects.get(username='jack').is_active)
            
    def test_activation_link(self):
        
        jack_user = create_user_jack()
        
        activation_token = user_activation_token(jack_user.username, jack_user.email, date.today())        
        
        url_to_activate =self.site_url + reverse('activation',kwargs={'token': str(activation_token)})
        
        browser = self.browser
        
        browser.get(url_to_activate)

        self.assertTrue(User.objects.get(username='jack').is_active)        
        
    def test_register(self):
        
        mail.outbox = []
        
        browser = self.browser
        
        browser.get(self.site_url +  reverse('register'))
        
        input_name = WebDriverWait(browser, 10).until( lambda browser: browser.find_element_by_xpath("//input[@id='id_name']"))
        
        input_email = WebDriverWait(browser, 10).until( lambda browser: browser.find_element_by_xpath("//input[@id='id_email']"))
        
        input_username = WebDriverWait(browser, 10).until( lambda browser: browser.find_element_by_xpath("//input[@id='id_username']"))
        
        input_password = WebDriverWait(browser, 10).until( lambda browser: browser.find_element_by_xpath("//input[@id='id_password']"))
        
        input_confirm_password = WebDriverWait(browser, 10).until( lambda browser: browser.find_element_by_xpath("//input[@id='id_confirm_password']"))
        
        submit_button = WebDriverWait(browser, 10).until( lambda browser: browser.find_element_by_xpath("//input[@type='submit']"))

        input_name.clear()
        input_name.send_keys('Jack Awesome Daniels') 
        
        input_email.clear()
        input_email.send_keys('jack@awesome.com')
        
        input_username.clear()
        input_username.send_keys('jack')
        
        input_password.clear()
        input_password.send_keys('pass')
        
        input_confirm_password.clear()
        input_confirm_password.send_keys('pass')
        
        submit_button.click()
        
        self.assertIn(reverse('resend-activation-email'),browser.current_url)
        
        self.assertEqual(len(mail.outbox), 1,'It should sent an email')