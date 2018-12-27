from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import unittest


class NewVisitorTest(unittest.TestCase):
    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()

    def check_for_row_in_picks_table(self, row_text):
        table = self.browser.find_element_by_id('id_picks')
        rows = table.find_elements_by_tag_name('tr')
        self.assertIn(row_text, [row.text for row in rows])

    def test_can_enter_a_pick_set_and_view_it_later(self):
        # After years of running the playoff pool via email and Excel
        # spreadsheets, it is now managed from the cloud.

        # Chuck goes to check out its homepage.
        self.browser.get('http://localhost:8000')

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
        time.sleep(1)

        self.check_for_row_in_picks_table('Game 1: 10')
        self.check_for_row_in_picks_table('Game 2: 7')
        self.check_for_row_in_picks_table('Game 3: 3')
        self.check_for_row_in_picks_table('Game 4: -10')

        # He changes his mind and decides the visitors will win game 3
        inputbox3 = self.browser.find_element_by_id('game_3')
        inputbox3.send_keys('-3')
        inputbox3.send_keys(Keys.ENTER)
        time.sleep(1)

        # The page updates again, and now shows the new pick for game 3
        # along with the previous picks for the other games
        self.check_for_row_in_picks_table('Game 1: 10')
        self.check_for_row_in_picks_table('Game 2: 7')
        self.check_for_row_in_picks_table('Game 3: -33')
        self.check_for_row_in_picks_table('Game 4: -10')

        # Chuck sees that the site has generated a unique URL for him.

        # He visits that URL again and sees his picks are still there.
        # self.fail('Finish the test!')


if __name__ == '__main__':
    unittest.main(warnings='ignore')
