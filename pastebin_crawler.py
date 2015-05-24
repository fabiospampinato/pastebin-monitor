#!/usr/bin/env python3
from math import ceil
import os
import re
import time
import sys

from pyquery import PyQuery

def all_python_encodings():
     return ["ascii",
             "big5",
             "big5hkscs",
             "cp037",
             "cp424",
             "cp437",
             "cp500",
             "cp720",
             "cp737",
             "cp775",
             "cp850",
             "cp852",
             "cp855",
             "cp856",
             "cp857",
             "cp858",
             "cp860",
             "cp861",
             "cp862",
             "cp863",
             "cp864",
             "cp865",
             "cp866",
             "cp869",
             "cp874",
             "cp875",
             "cp932",
             "cp949",
             "cp950",
             "cp1006",
             "cp1026",
             "cp1140",
             "cp1250",
             "cp1251",
             "cp1252",
             "cp1253",
             "cp1254",
             "cp1255",
             "cp1256",
             "cp1257",
             "cp1258",
             "euc_jp",
             "euc_jis_2004",
             "euc_jisx0213",
             "euc_kr",
             "gb2312",
             "gbk",
             "gb18030",
             "hz",
             "iso2022_jp",
             "iso2022_jp_1",
             "iso2022_jp_2",
             "iso2022_jp_2004",
             "iso2022_jp_3",
             "iso2022_jp_ext",
             "iso2022_kr",
             "latin_1",
             "iso8859_2",
             "iso8859_3",
             "iso8859_4",
             "iso8859_5",
             "iso8859_6",
             "iso8859_7",
             "iso8859_8",
             "iso8859_9",
             "iso8859_10",
             "iso8859_13",
             "iso8859_14",
             "iso8859_15",
             "iso8859_16",
             "johab",
             "koi8_r",
             "koi8_u",
             "mac_cyrillic",
             "mac_greek",
             "mac_iceland",
             "mac_latin2",
             "mac_roman",
             "mac_turkish",
             "ptcp154",
             "shift_jis",
             "shift_jis_2004",
             "shift_jisx0213",
             "utf_32",
             "utf_32_be",
             "utf_32_le",
             "utf_16",
             "utf_16_be",
             "utf_16_le",
             "utf_7",
             "utf_8",
             "utf_8_sig"]


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
        sys.stdout.flush()

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
    OTHER_ERROR = -3

    prev_checked_ids = []
    new_checked_ids = []

    def read_regexes(self):
        try:
            with open ( self.REGEXES_FILE, 'r') as f:
                try:
                    self.regexes = [ [ field.strip() for field in line.split(',')] for line in f.readlines() if line.strip() != '' and not line.startswith('#')]

                    # In case commas exist in the regexes...merge everything.
                    for i in range(len(self.regexes)):
                        self.regexes[i] = [','.join(self.regexes[i][:-2])] + self.regexes[i][-2:]
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

        try:
            page_html = page.html ()
        except:
            worked = False
            for enc in all_python_encodings():
                try:
                    page_html = page.html(encoding=enc)
                    worked = True
                except:
                    pass
            if not worked:
                return self.OTHER_ERROR, None
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

        with open( directory + '/' + timestamp.replace('/','_').replace(':','_').replace(' ','__') + '_' + paste_id.replace('/','') + '.txt', mode='w' ) as paste:
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
                sleep_time = ceil(max(0,(refresh_time - elapsed_time)))
                if sleep_time > 0:
                    Logger().log('Waiting {:d} seconds to refresh...'.format(sleep_time), True)
                    time.sleep ( sleep_time )
            elif status == self.ACCESS_DENIED:
                Logger ().log ( 'Damn! It looks like you have been banned (probably temporarily)', True, 'YELLOW' )
                for n in range ( 0, ban_wait ):
                    Logger ().log ( 'Please wait ' + str ( ban_wait - n ) + ' minute' + ( 's' if ( ban_wait - n ) > 1 else '' ) )
                    time.sleep ( 60 )
            elif status == self.CONNECTION_FAIL:
                Logger().log ( 'Connection down. Waiting {:d} seconds and trying again'.format(connection_timeout), True, 'RED')
                time.sleep(connection_timeout)
            elif status == self.OTHER_ERROR:
                Logger().log('Unknown error. Maybe an encoding problem? Trying again.'.format(connection_timeout), True,'RED')
                time.sleep(1)

try:
    Crawler ().start ()
except KeyboardInterrupt:
    Logger ().log ( 'Bye! Hope you found what you were looking for :)', True )
