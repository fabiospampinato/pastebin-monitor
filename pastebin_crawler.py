#!/usr/bin/env python3
import os
import re
import time

from pyquery import PyQuery

class Logger:

    shell_mod = {
        '':'',
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

    def log ( self, message, is_bold=False, color=''):
        prefix = ''
        suffix = ''

        if os.name == 'posix':
            if is_bold:
                prefix += self.shell_mod['BOLD']
            prefix += self.shell_mod[color.upper()]

            suffix = self.shell_mod['RESET']

        message = prefix + message + suffix
        print ( message )

    def error(self, err):
        self.log(err, True, 'RED')

    def fatal_error(self, err):
        self.error(err)
        exit()

class Crawler:

    PASTEBIN_URL = 'http://pastebin.com'
    PASTES_URL = PASTEBIN_URL + '/archive'
    REGEXES_FILE = 'regexes.txt'
    OK = 1
    ACCESS_DENIED = -1
    CONNECTION_FAIL = -2

    prev_checked_ids = []
    new_checked_ids = []

    def read_regexes(self):
        try:
            with open ( self.REGEXES_FILE, 'r') as f:
                try:
                    self.regexes = [ [ field.strip() for field in line.split(',')] for line in f.readlines() if line.strip() != '' and not line.startswith('#')]
                except:
                    Logger().fatal_error('Malformed regexes file. Format: regex_pattern,URL logging file, directory logging file.')
        except:
            Logger().fatal_error('{:s} not found or not acessible.'.format(self.REGEXES_FILE))


    def __init__(self):
        self.read_regexes()



    def get_pastes ( self ):
        Logger ().log ( 'Getting pastes', True )
        try:
            page = PyQuery ( url = self.PASTES_URL )
        except:
            return self.CONNECTION_FAIL,None
        page_html = page.html ()

        if re.match ( r'Pastebin\.com - Access Denied Warning', page_html, re.IGNORECASE ) or 'blocked your IP' in page_html:
            return self.ACCESS_DENIED,None
        else:
            return self.OK,page('.maintable img').next('a')

    def check_paste ( self, paste_id ):
        paste_url = self.PASTEBIN_URL + paste_id
        paste_txt = PyQuery ( url = paste_url )('#paste_code').text()

        for regex,file,directory in self.regexes:

            if re.match ( regex, paste_txt, re.IGNORECASE ):
                Logger ().log ( 'Found a matching paste: ' + paste_url + ' (' + file + ')', True, 'CYAN' )
                self.save_result ( paste_url,paste_id,file,directory )
                return True
            else:
                Logger ().log ( 'Not matching paste: ' + paste_url )
                return False


    def get_timestamp(self):
        return time.strftime('%Y/%m/%d %H:%M:%S')

    def save_result ( self, paste_url, paste_id, file, directory ):
        timestamp = self.get_timestamp()
        with open ( file, 'a' ) as matching:
            matching.write ( timestamp + ' - ' + paste_url + '\n' )

        try:
            os.mkdir(directory)
        except:
            pass

        with open( directory + '/' + timestamp.replace('/','_') + paste_id + '.txt', 'w' ) as paste:
            paste_txt = PyQuery(url=paste_url)('#paste_code').text()
            paste.write(paste_txt)


    def start ( self, refresh_time = 30, delay = 1, ban_wait = 5, flush_after_x_refreshes=100, connection_timeout=60 ):
        count = 0
        while True:
            status,pastes = self.get_pastes ()

            start_time = time.time()
            if status == self.OK:
                for paste in pastes:
                    paste_id = PyQuery ( paste ).attr('href')
                    self.new_checked_ids.append ( paste_id )
                    if paste_id not in self.prev_checked_ids:
                        self.check_paste ( paste_id )
                        time.sleep ( delay )
                    count += 1

                if count == flush_after_x_refreshes:
                    self.prev_checked_ids = self.new_checked_ids
                    count = 0
                else:
                    self.prev_checked_ids += self.new_checked_ids
                self.new_checked_ids = []

                elapsed_time = time.time() - start_time
                sleep_time = max(0,(refresh_time - elapsed_time))
                if sleep_time > 0:
                    Logger().log('Waiting {:d} seconds to refresh...'.format(refresh_time), True)
                    time.sleep ( refresh_time )
            elif status == self.ACCESS_DENIED:
                Logger ().log ( 'Damn! It looks like you have been banned (probably temporarily)', True, 'YELLOW' )
                for n in range ( 0, ban_wait ):
                    Logger ().log ( 'Please wait ' + str ( ban_wait - n ) + ' minute' + ( 's' if ( ban_wait - n ) > 1 else '' ) )
                    time.sleep ( 60 )
            elif status == self.CONNECTION_FAIL:
                Logger().log ( 'Connection down. Waiting {:s} seconds and trying again'.format(connection_timeout), True, 'RED')
                time.sleep(connection_timeout)

try:
    Crawler ().start ()
except KeyboardInterrupt:
    Logger ().log ( 'Bye! Hope you found what you were looking for :)', True )
