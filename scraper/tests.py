from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from unittest import skip
from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import json
import time

MAX_WAIT = 10


class NewVisitorTest(StaticLiveServerTestCase):

    def setUp(self):
        # self.browser = webdriver.Firefox()
        pass

    def tearDown(self):
        # self.browser.quit()
        pass

    def is_good_response(self, resp):
        content_type = resp.headers['Content-Type'].lower()
        return (resp.status_code == 200 and
                content_type is not None and
                content_type.find('html') > -1)

    def simple_get(self, url):
        try:
            with closing(get(url, stream=True)) as resp:
                if self.is_good_response(resp):
                    return resp.content
                else:
                    return None
        except RequestException as e:
            print('Error during requests to {0}: {1}'.format(url, str(e)))
            return None

    def test_a_nfl_page(self):
        raw_html = self.simple_get('https://www.nfl.com/')
        html = BeautifulSoup(raw_html, 'html.parser')
        content_string = html.decode_contents()
        start_location = content_string.find('__INITIAL_DATA__')
        print(start_location)
        json_start = content_string.find('{', start_location)
        print(json_start)
        json_end = content_string.find('\n', json_start)
        print(json_end)
        start_location = content_string.find('__REACT_ROOT_ID__')
        print(start_location)
        y = json.loads(content_string[json_start: json_end - 1])
        # print(json.dumps(y))
        for game in y['uiState']['scoreStripGames']:
            print(game['awayTeam']['identifier'] + ' at ' +
                  game['homeTeam']['identifier'])
            print('  Away Team:')
            for key in game['homeTeam'].keys():
                s = game['homeTeam']
                value = s[key]
                print(f'    {key}: {s[key]}')
            for key in game['awayTeam'].keys():
                s = game['awayTeam']
                value = s[key]
                print(f'    {key}: {s[key]}')
            print('  Status:')
            for key in game['status'].keys():
                status = game['status']
                value = status[key]
                print(f'    {key}: {status[key]}')
            # print(game.keys())
        # print (f'Response has {len(raw_html)} bytes.')
        game1 = y['uiState']['scoreStripGames'][0]['status']
        game4 = y['uiState']['scoreStripGames'][3]['status']
        print([k for k in game1.keys() if k in game4.keys()])
        self.assertEquals(True, True)
        '''
        self.browser.get('https://www.nfl.com/scores/2018/POST1')
        divs = self.browser.find_elements_by_class_name('rn-fnigne')
        print('There are ' + str(len(divs)) + ' divs.')
        # for div in divs:
        #     print('Next div: ' + div.text)
        el = self.browser.find_element_by_css_selector('.rmq-9622b9b7')
        divs = el.find_element_by_xpath('/div')
        print('There are ' + str(len(divs)) + ' divs.')
        # print(el.text)
        self.assertEquals(True, False)
        '''
