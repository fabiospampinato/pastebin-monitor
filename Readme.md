# Pastebin Crawler
A simple Pastebin crawler which looks for interesting things and saves them to disk. Originally forked  from [https://github.com/FabioSpampinato/Pastebin-Crawler](https://github.com/FabioSpampinato/Pastebin-Crawler)

## How it works
The tool periodically checks for new pastes and analyzes it. If they match a given pattern, their URL is stored in a .txt file, and its content in a file under a predefined directory. For instance, if the paste matches a password it is placed in 'passwords.txt' and stored under 'passwords'.
 
 The following parameters are configurable:
 
 * Refresh time (time slept between Pastebin checks, in seconds)
 * Delay (time between sequential accesses to each of Pastebin's pastes, in seconds)
 * Ban wait time (time to wait if a ban is detected, in minutes)
 * Timeout time (time to wait until a new attempt is made if connection times out due to a bad connection, in seconds)
 * Number of refreshes between flushes (number of refreshes until past Pastes are cleared from memory)

## Dependencies
* [PyQuery](https://pythonhosted.org/pyquery/)

## And...
More configurability and ease of use is coming soon! :)