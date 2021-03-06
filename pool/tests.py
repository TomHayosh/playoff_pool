from django.test import TestCase
from pool.models import PickSet
from pool.views import round_1_expiration_time
from unittest import skip
import datetime


# Create your tests here.
class HomePageTest(TestCase):

    def test_uses_home_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'home.html')

    def test_only_saves_when_necessary(self):
        self.client.get('/')
        self.assertEqual(PickSet.objects.count(), 0)


class PicksViewTest(TestCase):

    def test_uses_picks_template(self):
        pick_set = PickSet.objects.create()
        response = self.client.get(f'/picks/{pick_set.id}/')
        self.assertTemplateUsed(response, 'picks.html')

    def test_displays_home_team_picks_as_default(self):
        pick_set = PickSet.objects.create(
            round_1_game_1=3,
            round_1_game_2=3,
            round_1_game_3=3,
            round_1_game_4=3,
        )

        response = self.client.get(f'/picks/{pick_set.id}/')
        self.assertContains(response, '<b>Texans')
        self.assertContains(response, '<b>Cowboys')
        self.assertContains(response, '<b>Ravens')
        self.assertContains(response, '<b>Bears')

    def test_displays_visiting_team_picks(self):
        pick_set = PickSet.objects.create(
            round_1_game_1_team=0,
            round_1_game_1=3,
            round_1_game_2_team=0,
            round_1_game_2=3,
            round_1_game_3_team=0,
            round_1_game_3=3,
            round_1_game_4_team=0,
            round_1_game_4=3,
        )

        response = self.client.get(f'/picks/{pick_set.id}/')
        self.assertContains(response, '<b>Colts')
        self.assertContains(response, '<b>Seahawks')
        self.assertContains(response, '<b>Chargers')
        self.assertContains(response, '<b>Eagles')

    def test_displays_negative_picks(self):
        other_set = PickSet.objects.create(
            round_1_game_1=-7,
            round_1_game_2=-10,
            round_1_game_3=-3,
            round_1_game_4=-14,
        )

        response = self.client.get(f'/picks/{other_set.id}/')
        self.assertContains(response, '-7')
        self.assertContains(response, '-10')
        self.assertContains(response, '-3')
        self.assertContains(response, '-14')

    def test_passses_correct_pick_set_to_template(self):
        correct_set = PickSet.objects.create(
            round_1_game_1=3,
            round_1_game_2=3,
            round_1_game_3=3,
            round_1_game_4=3,
        )
        other_set = PickSet.objects.create(
            round_1_game_1=-7,
            round_1_game_2=-7,
            round_1_game_3=-7,
            round_1_game_4=-7,
        )
        response = self.client.get(f'/picks/{correct_set.id}/')
        self.assertEqual(response.context['pick_set'], correct_set)

    @skip("Time based testing")
    def test_cannot_edit_after_games_start(self):
        # Need to set the expiration time as start_time + 5 seconds
        pick_set = PickSet.objects.create(
            round_1_game_1=-7,
            round_1_game_2=-10,
            round_1_game_3=-3,
            round_1_game_4=-14,
        )

        response = self.client.get(f'/picks/{pick_set.id}/')
        self.assertContains(response, 'edit_picks')
        # time.sleep(3)
        response = self.client.get(f'/picks/{pick_set.id}/')
        self.assertNotContains(response, 'edit_picks')


class PicksEditTest(TestCase):

    def test_uses_edit_template(self):
        pick_set = PickSet.objects.create()
        response = self.client.get(f'/picks/{pick_set.id}/edit/')
        self.assertTemplateUsed(response, 'edit.html')

    def test_passes_correct_pick_set_template(self):
        pick_set = PickSet.objects.create(
            round_1_game_1=3,
            round_1_game_2=3,
            round_1_game_3=3,
            round_1_game_4=3,
        )
        response = self.client.get(f'/picks/{pick_set.id}/edit/')
        self.assertContains(response, '<input')

    def test_shows_selected_home_teams_as_default(self):
        pick_set = PickSet.objects.create(
            round_1_game_1=3,
            round_1_game_2=3,
            round_1_game_3=3,
            round_1_game_4=3,
        )
        response = self.client.get(f'/picks/{pick_set.id}/edit/')
        self.assertContains(response, '"selected">Texans')
        self.assertContains(response, '"selected">Cowboys')
        self.assertContains(response, '"selected">Ravens')
        self.assertContains(response, '"selected">Bears')

    def test_shows_selected_visiting_teams(self):
        pick_set = PickSet.objects.create(
            round_1_game_1_team=0,
            round_1_game_1=3,
            round_1_game_2_team=0,
            round_1_game_2=3,
            round_1_game_3_team=0,
            round_1_game_3=3,
            round_1_game_4_team=0,
            round_1_game_4=3,
        )
        response = self.client.get(f'/picks/{pick_set.id}/edit/')
        self.assertContains(response, '"selected">Colts')
        self.assertContains(response, '"selected">Seahawks')
        self.assertContains(response, '"selected">Chargers')
        self.assertContains(response, '"selected">Eagles')

    @skip("Time based testing")
    def test_cannot_edit_after_games_start(self):
        # Need to set the expiration time as start_time + 5 seconds
        other_set = PickSet.objects.create(
            round_1_game_1=-7,
            round_1_game_2=-10,
            round_1_game_3=-3,
            round_1_game_4=-14,
        )

        response = self.client.get(f'/picks/{other_set.id}/edit/')
        print(response.content.decode())
        self.assertContains(response, '<input')
        # time.sleep(5)
        round_1_expiration_time = datetime.datetime(2018, 12, 28)
        response = self.client.get(f'/picks/{other_set.id}/edit/')
        self.assertNotContains(response, '<input')
        self.assertContains(response, 'Game picks are locked.')


class NewPicksTest(TestCase):

    def test_can_save_a_POST_request(self):
        data = {}
        data['game_1_pick'] = 24
        data['game_2_pick'] = 10
        data['game_3_pick'] = -14
        data['game_4_pick'] = 13
        pick_set = PickSet.objects.create(name="Test user")
        self.client.post(f'/picks/{pick_set.id}/update_picks', data)
        self.assertEqual(PickSet.objects.count(), 1)
        pick_set = PickSet.objects.first()
        self.assertEqual(pick_set.round_1_game_3, -14)

    def test_can_save_a_partial_new_pick_set(self):
        data = {}
        data['game_1_pick'] = 24
        pick_set = PickSet.objects.create(name="Test user")
        self.client.post(f'/picks/{pick_set.id}/update_picks', data)
        self.assertEqual(PickSet.objects.count(), 1)
        pick_set = PickSet.objects.first()
        self.assertEqual(pick_set.round_1_game_1, 24)
        self.assertEqual(pick_set.round_1_game_2, 0)

    def test_can_save_a_partial_update_pick_set(self):
        data = {}
        data['game_1_pick'] = 24
        pick_set = PickSet.objects.create(name="Test user")
        self.client.post(f'/picks/{pick_set.id}/update_picks', data)
        self.assertEqual(PickSet.objects.count(), 1)
        pick_set = PickSet.objects.first()
        self.assertEqual(pick_set.round_1_game_1, 24)
        self.assertEqual(pick_set.round_1_game_2, 0)
        data2 = {}
        data2['game_2_pick'] = 13
        self.client.post(f'/picks/{pick_set.id}/update_picks', data2)
        pick_set = PickSet.objects.first()
        self.assertEqual(pick_set.round_1_game_2, 13)
        self.assertEqual(pick_set.round_1_game_1, 24)

    def test_can_save_a_POST_request_to_update_picks(self):
        pick_set = PickSet.objects.create(
            round_1_game_1=3,
            round_1_game_2=3,
            round_1_game_3=3,
            round_1_game_4=3,
        )
        pick_set = PickSet.objects.first()
        self.assertEqual(pick_set.round_1_game_3, 3)
        data = {}
        data['game_1_pick'] = 24
        data['game_2_pick'] = 10
        data['game_3_pick'] = -14
        data['game_4_pick'] = 13

        self.client.post(f'/picks/{pick_set.id}/update_picks', data)
        self.assertEqual(PickSet.objects.count(), 1)
        pick_set = PickSet.objects.first()
        self.assertEqual(pick_set.round_1_game_3, -14)

    def test_redirects_after_POST(self):
        pick_set = PickSet.objects.create(
            round_1_game_1=3,
            round_1_game_2=3,
            round_1_game_3=3,
            round_1_game_4=3,
        )
        data = {}
        data['game_1_pick'] = 24
        data['game_2_pick'] = 10
        data['game_3_pick'] = -14
        data['game_4_pick'] = 13
        response = self.client.post(
            f'/picks/{pick_set.id}/update_picks',
            data
        )
        pick_set = PickSet.objects.first()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], f'/picks/{pick_set.id}/')


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
