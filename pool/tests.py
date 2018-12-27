from django.test import TestCase


# Create your tests here.
class HomePageTest(TestCase):

    def test_uses_home_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'home.html')

    def test_can_save_a_POST_request(self):
        response = self.client.post('/', data={'game_1_pick': '24'})
        self.assertIn('24', response.content.decode())
        self.assertTemplateUsed(response, 'home.html')
