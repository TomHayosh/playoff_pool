from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.keys import Keys
from unittest import skip
import time

MAX_WAIT = 10


class NewVisitorTest(StaticLiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()

    def wait_for_row_in_picks_table(self, row_text):
        start_time = time.time()
        while True:
            try:
                table = self.browser.find_element_by_id('id_picks')
                rows = table.find_elements_by_tag_name('tr')
                self.assertIn(row_text, [row.text for row in rows])
                return
            except (AssertionError, WebDriverException) as e:
                if time.time() - start_time > MAX_WAIT:
                    raise e
                time.sleep(0.5)

    def check_for_row_in_picks_table(self, row_text):
        table = self.browser.find_element_by_id('id_picks')
        rows = table.find_elements_by_tag_name('tr')
        self.assertIn(row_text, [row.text for row in rows])

    def test_can_enter_a_pick_set_and_view_it_later(self):
        # After years of running the playoff pool via email and Excel
        # spreadsheets, it is now managed from the cloud.

        # Chuck goes to check out its homepage.
        self.browser.get(self.live_server_url)
        # self.browser.get('http://tomhayosh.pythonanywhere.com/')

        # He notices the page title and header mention the NFL Playoff Pool.
        self.assertIn('2019 NFL Playoff Pool', self.browser.title)
        header_text = self.browser.find_element_by_tag_name('h1').text
        self.assertIn('2019 NFL Playoff Pool', header_text)

        # He is able to create a new pick set for the first round of
        # four games.
        inputbox1 = self.browser.find_element_by_id('game_1')
        self.assertEqual(
            inputbox1.get_attribute('placeholder'),
            'a'
        )
        inputbox2 = self.browser.find_element_by_id('game_2')
        self.assertEqual(
            inputbox2.get_attribute('placeholder'),
            'b'
        )
        inputbox3 = self.browser.find_element_by_id('game_3')
        self.assertEqual(
            inputbox3.get_attribute('placeholder'),
            'c'
        )
        inputbox4 = self.browser.find_element_by_id('game_4')
        self.assertEqual(
            inputbox4.get_attribute('placeholder'),
            'd'
        )

        # He picks home team by 10, 7, 3, then visiting by 10.
        inputbox1.send_keys('10')
        inputbox2.send_keys('7')
        inputbox3.send_keys('3')
        inputbox4.send_keys('-10')

        # When he hits enter, the page updates and shows the entered picks.
        inputbox4.send_keys(Keys.ENTER)

        self.wait_for_row_in_picks_table('Game 1: 10')
        self.wait_for_row_in_picks_table('Game 2: 7')
        self.wait_for_row_in_picks_table('Game 3: 3')
        self.wait_for_row_in_picks_table('Game 4: -10')

        # He changes his mind and decides the visitors will win game 3
        editbutton = self.browser.find_element_by_id('edit_picks')
        editbutton.send_keys(Keys.ENTER)
        time.sleep(1)
        inputbox3 = self.browser.find_element_by_id('game_3')
        inputbox3.clear()
        inputbox3.send_keys('-3')
        inputbox3.send_keys(Keys.ENTER)

        # The page updates again, and now shows the new pick for game 3
        # along with the previous picks for the other games
        self.wait_for_row_in_picks_table('Game 1: 10')
        self.wait_for_row_in_picks_table('Game 2: 7')
        self.wait_for_row_in_picks_table('Game 3: -3')
        self.wait_for_row_in_picks_table('Game 4: -10')

    def test_user_can_submit_partial_pick_set(self):
        # Chuck knows what he wants for the first game
        self.browser.get(self.live_server_url)
        inputbox1 = self.browser.find_element_by_id('game_1')
        inputbox1.send_keys('7')
        inputbox1.send_keys(Keys.ENTER)
        self.wait_for_row_in_picks_table('Game 1: 7')

        # Later Chuck makes his pick for the second game, and sees that
        # his first pick is still there
        editbutton = self.browser.find_element_by_id('edit_picks')
        editbutton.send_keys(Keys.ENTER)
        time.sleep(1)
        inputbox2 = self.browser.find_element_by_id('game_2')
        inputbox2.send_keys('3')
        inputbox2.send_keys(Keys.ENTER)
        self.wait_for_row_in_picks_table('Game 2: 3')
        self.wait_for_row_in_picks_table('Game 1: 7')

    def test_multiple_users_can_enter_picks_at_different_urls(self):
        # Chuck sees that the site has generated a unique URL for him.
        self.browser.get(self.live_server_url)
        inputbox1 = self.browser.find_element_by_id('game_1')
        inputbox2 = self.browser.find_element_by_id('game_2')
        inputbox3 = self.browser.find_element_by_id('game_3')
        inputbox4 = self.browser.find_element_by_id('game_4')
        inputbox1.send_keys('10')
        inputbox2.send_keys('7')
        inputbox3.send_keys('3')
        inputbox4.send_keys('-10')

        # When he hits enter, the page updates and shows the entered picks.
        inputbox4.send_keys(Keys.ENTER)
        time.sleep(1)

        chuck_picks_url = self.browser.current_url
        self.assertRegex(chuck_picks_url, '/picks/.+')

        # # Use a new browser session for the next user
        self.browser.quit()
        self.browser = webdriver.Firefox()

        # Mike visits the home page and enters picks
        self.browser.get(self.live_server_url)
        page_text = self.browser.find_element_by_tag_name('body').text
        self.assertNotIn('10', page_text)
        self.assertNotIn('-3', page_text)

        # Mike enters his picks
        inputbox1 = self.browser.find_element_by_id('game_1')
        inputbox2 = self.browser.find_element_by_id('game_2')
        inputbox3 = self.browser.find_element_by_id('game_3')
        inputbox4 = self.browser.find_element_by_id('game_4')
        inputbox1.send_keys('-3')
        inputbox2.send_keys('-14')
        inputbox3.send_keys('1')
        inputbox4.send_keys('27')

        # When he hits enter, the page updates and shows the entered picks.
        inputbox4.send_keys(Keys.ENTER)
        time.sleep(1)

        mike_picks_url = self.browser.current_url
        self.assertRegex(mike_picks_url, '/picks/.+')
        self.assertNotEqual(chuck_picks_url, mike_picks_url)

    @skip
    def test_layout_and_styling(self):
        self.browser.get(self.live_server_url)

        # He visits that URL again and sees his picks are still there.
        # self.fail('Finish the test!')
