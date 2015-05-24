# Pastebin Crawler
A simple Pastebin crawler which looks for interesting things and saves them to disk. Originally forked  from [https://github.com/FabioSpampinato/Pastebin-Crawler](https://github.com/FabioSpampinato/Pastebin-Crawler)

## Dependencies
* [PyQuery](https://pythonhosted.org/pyquery/)
* Python 3

Make sure you use PyQuery for Python 3!

## How it works
The tool periodically checks for new pastes and analyzes them. If they match a given pattern, their URL is stored in a .txt file, and their content in a file under a predefined directory. For instance, if the paste matches a password it can be placed in 'passwords.txt' and stored under 'passwords'.
 
 The following parameters are configurable:
 
 * Refresh time (time slept between Pastebin checks, in seconds)
 * Delay (time between sequential accesses to each of Pastebin's pastes, in seconds)
 * Ban wait time (time to wait if a ban is detected, in minutes)
 * Timeout time (time to wait until a new attempt is made if connection times out due to a bad connection, in seconds)
 * Number of refreshes between flushes (number of refreshes until past Pastes are cleared from memory)
 * The regexes. See [Using your own regexes](#user-content-using-your-own-regexes)
 
## Using your own regexes
 Regexes are stored in the _regexes.txt_ file. It is trivial to modify this file and add new patterns to match.
 
 
 The format is:
 
    regex , URL logging file path/name , directory to store pasties
      
Examples:

    (password\b|pass\b|pswd\b|passwd\b|pwd\b|pass\b), passwords.txt, passwords
    (serial\b|cd-key\b|key\b|license\b),              serials.txt,   serials

**And yes, you can use commas in the regex. Just don't do it in filename or directory. Really, _don't_!**

## And...
More configurability and ease of use is coming soon! :)