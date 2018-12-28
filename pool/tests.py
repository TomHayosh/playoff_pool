from django.test import TestCase
from pool.models import PickSet


# Create your tests here.
class HomePageTest(TestCase):

    def test_uses_home_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'home.html')

    def test_can_save_a_POST_request_for_round_1(self):
        data = {}
        data['game_1_pick'] = 24
        data['game_2_pick'] = 10
        data['game_3_pick'] = -14
        data['game_4_pick'] = 13
        response = self.client.post('/', data)

        self.assertEqual(PickSet.objects.count(), 1)
        new_pick_set = PickSet.objects.first()
        self.assertEqual(new_pick_set.round_1_game_1, 24)
        self.assertEqual(new_pick_set.round_1_game_2, 10)
        self.assertEqual(new_pick_set.round_1_game_3, -14)
        self.assertEqual(new_pick_set.round_1_game_4, 13)

        self.assertIn('24', response.content.decode())
        self.assertTemplateUsed(response, 'home.html')

    def test_only_saves_when_necessary(self):
        self.client.get('/')
        self.assertEqual(PickSet.objects.count(), 0)


class PickSetModelTest(TestCase):

    def test_saving_and_retrieving_picks(self):
        pick_set = PickSet()
        pick_set.round_1_game_1 = 10
        pick_set.round_1_game_2 = 7
        pick_set.round_1_game_3 = 3
        pick_set.round_1_game_4 = -10
        pick_set.save()
        self.assertEqual(pick_set.round_1_game_3, 3)

        pick_set.round_1_game_3 = -3
        pick_set.save()
        all_pick_sets = PickSet.objects.all()
        self.assertEqual(all_pick_sets.count(), 1)
        self.assertEqual(all_pick_sets[0].round_1_game_3, -3)
