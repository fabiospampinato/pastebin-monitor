#!/usr/bin/env python3

import time
from pyquery import PyQuery

term_color = {
   "PURPLE" : '\033[95m',
   "CYAN" : '\033[96m',
   "DARKCYAN" : '\033[36m',
   "BLUE" : '\033[94m',
   "GREEN" : '\033[92m',
   "YELLOW" : '\033[93m',
   "RED" : '\033[91m',
   "BOLD" : '\033[1m',
   "UNDERLINE" : '\033[4m',
   "END" : '\033[0m'
}

password_keys = [ "password", "Password", "pass", "Pass", "pswd", "Pswd", "passwd", "Passwd" ]
password_assign = [ " =", "=", " :", ":" ]

pastebin_url = "http://pastebin.com"
pastebin_archive = pastebin_url + "/archive"

def info_msg ( message, is_bold = False, color = False ):
	message = "-" + message
	if is_bold:
		message = term_color["BOLD"] + message + term_color["END"]
	if color:
		message = term_color[color] + message + term_color["END"]
	print ( message )

def get_pastes ():
	info_msg ( "Getting pastes", True )
	return PyQuery ( url=pastebin_archive )(".maintable img").next("a")

def check_paste ( paste_id ):
	paste_url = pastebin_url + paste_id
	content = PyQuery ( url=paste_url )("#paste_code").text()
	for key in password_keys:
		for assign in password_assign:
			if key + assign in content:
				info_msg ("This paste contains 'password': " + paste_url, True, "RED" )
				save_result ( paste_url )
				return
	info_msg ( "This paste doesn't contain 'password': " + paste_url )

def save_result ( paste_url ):
	clipboard = open ( "interesting_pastes.txt", "a" )
	clipboard.write ( time.strftime("%Y/%m/%d %H:%M:%S") + " - " + paste_url + "\n" )
	clipboard.close()

def main ( intervall ):
	start_id = "NOSTARTID"
	next_start_id = ""
	while True:
		pastes = get_pastes()
		counter = 1
		for paste in pastes:
			paste_id = PyQuery ( paste ).attr("href")
			if counter == 1:
				next_start_id = paste_id
			if paste_id == start_id:
				break
			check_paste ( paste_id )
			counter += 1
		start_id = next_start_id
		time.sleep(intervall)

main(1)




