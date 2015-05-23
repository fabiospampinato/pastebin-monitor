#!/usr/bin/env python3

import re
import time

from pyquery import PyQuery

class Logger:

    shell_mod = {
       'PURPLE' : '\033[95m',
       'CYAN' : '\033[96m',
       'DARKCYAN' : '\033[36m',
       'BLUE' : '\033[94m',
       'GREEN' : '\033[92m',
       'YELLOW' : '\033[93m',
       'RED' : '\033[91m',
       'BOLD' : '\033[1m',
       'UNDERLINE' : '\033[4m',
       'RESET' : '\033[0m'
    }

    def log ( self, message, is_bold = False, color = False ):
        prefix = ''
        if is_bold:
            prefix += self.shell_mod['BOLD']
        if color:
            prefix += self.shell_mod[color.upper()]

        suffix = self.shell_mod['RESET']

        message = prefix + message + suffix
        print ( message )

class Crawler:

    pastebin_url = 'http://pastebin.com'
    pastes_url = pastebin_url + '/archive'

    prev_checked_ids = []
    new_checked_ids = []

    regexes = [
        r'(password|pass|pswd|passwd|pwd|pass)',     # Passwords
        r'(serial|cd-key|key|license)',              # Serials
        r'(gmail.com|hotmail.com|live.com|yahoo)',   # Emails (FIXME: Get a decent list of these)
        r'(hack|exploit|leak|usernames|)',           # 'other'
    ]

    def get_pastes ( self ):
        Logger ().log ( 'Getting pastes', True )
        page = PyQuery ( url = self.pastes_url )
        page_html = page.html ()

        if re.match ( r'Pastebin\.com - Access Denied Warning', page_html, re.IGNORECASE ):
            return False
        else:
            return page('.maintable img').next('a')

    def check_paste ( self, paste_id ):
        paste_url = self.pastebin_url + paste_id
        paste_txt = PyQuery ( url = paste_url )('#paste_code').text()

        for regex in self.regexes:

            if re.match ( regex, paste_txt, re.IGNORECASE ):
                Logger ().log ( 'Found a matching paste: ' + paste_url, True, 'CYAN' )
                self.save_result ( paste_url )
                return True
            else:
                Logger ().log ( 'Not matching paste: ' + paste_url )
                return False

    def save_result ( self, paste_url ):
        with open ( 'matching_pastes.txt', 'a' ) as matching:
            matching.write ( time.strftime ( '%Y/%m/%d %H:%M:%S' ) + ' - ' + paste_url + '\n' )

    def start ( self, refresh_rate = 30, delay = 0.1, ban_wait = 5 ):
        while True:
            pastes = self.get_pastes ()

            if pastes:
                for paste in pastes:
                    paste_id = PyQuery ( paste ).attr('href')
                    self.new_checked_ids.append ( paste_id )
                    if paste_id not in self.prev_checked_ids:
                        self.check_paste ( paste_id )
                        time.sleep ( delay )

                self.prev_checked_ids = self.new_checked_ids
                self.new_checked_ids = []

                time.sleep ( refresh_rate )
            else:
                Logger ().log ( 'Damn! It looks like you have been banned (probably temporarily)', True, 'RED' )
                for n in range ( 0, ban_wait ):
                    Logger ().log ( 'Please wait ' + str ( ban_wait - n ) + ' minute' + ( 's' if ( ban_wait - n ) > 1 else '' ) )
                    time.sleep ( 60 )

try:
    Crawler ().start ()
except KeyboardInterrupt:
    Logger ().log ( 'Bye! Hope you found what you were looking for :)', True );
