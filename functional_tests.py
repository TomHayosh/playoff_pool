from selenium import webdriver
import unittest


class NewVisitorTest(unittest.TestCase):
    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()

    def test_can_enter_a_pick_set_and_view_it_later(self):
        # After years of running the playoff pool via email and Excel
        # spreadsheets, it is now managed from the cloud.

        # Chuck goes to check out its homepage.
        self.browser.get('http://localhost:8000')

        # He notices the page title and header mention the NFL Playoff Pool.
        self.assertIn('NFL Playoff Pool', self.browser.title)

        # He is able to create a new pick set for the first round of
        # four games.

        # He picks the home team by 21 in all four games.

        # When he hits enter, the page updates and shows the entered picks.

        # Chuck sees that the site has generated a unique URL for him.

        # He visits that URL again and sees his picks are still there.
        self.fail('Finish the test!')


if __name__ == '__main__':
    unittest.main(warnings='ignore')
