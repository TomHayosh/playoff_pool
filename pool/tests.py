from django.test import TestCase
from pool.models import PickSet


# Create your tests here.
class HomePageTest(TestCase):

    def test_uses_home_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'home.html')

    def test_only_saves_when_necessary(self):
        self.client.get('/')
        self.assertEqual(PickSet.objects.count(), 0)


class ListViewTest(TestCase):

    def test_uses_picks_template(self):
        response = self.client.get('/picks/only-picks/')
        self.assertTemplateUsed(response, 'picks.html')

    def test_displays_all_picks(self):
        PickSet.objects.create(
            round_1_game_1=3,
            round_1_game_2=3,
            round_1_game_3=3,
            round_1_game_4=3,
        )
        PickSet.objects.create(
            round_1_game_1=-7,
            round_1_game_2=-7,
            round_1_game_3=-7,
            round_1_game_4=-7,
        )

        response = self.client.get('/picks/only-picks/')

        self.assertContains(response, '3')
        # self.assertContains(response, '7')


class NewPicksTest(TestCase):

    def test_can_save_a_POST_request(self):
        data = {}
        data['game_1_pick'] = 24
        data['game_2_pick'] = 10
        data['game_3_pick'] = -14
        data['game_4_pick'] = 13
        self.client.post('/picks/new', data)
        self.assertEqual(PickSet.objects.count(), 1)
        pick_set = PickSet.objects.first()
        self.assertEqual(pick_set.round_1_game_3, -14)

    def test_redirects_after_POST(self):
        data = {}
        data['game_1_pick'] = 24
        data['game_2_pick'] = 10
        data['game_3_pick'] = -14
        data['game_4_pick'] = 13
        response = self.client.post('/picks/new', data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/picks/only-picks/')


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
