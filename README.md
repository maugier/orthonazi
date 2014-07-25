#OrthoNazi 0.1


An IRC Bot to insult people who make orthography mistakes

##Requirements:

  - irc (http://bitbucket.org/jaraco/irc/)
  - aspell (http://http://0x80.pl/proj/aspell-python)

##Usage:

Create a bot script like so:

    #!/usr/bin/env python3

    import orthonazi

    servers = [('irc.server.com', 6667)]
    bot = orthonazi.OrthoNazi(servers, channels=["#mychannel"], delay=600, whitelist_path="./whitelist.txt")
    bot.start()

Refer to the source for more options. Without 'whitelist_path', the whitelist will be discarded between runs.
Use 'delay' to change the grace time between insult messages.

Hardcoded insults are in french, edit the main script to your desire. {0} will be expanded to the name of the offender, {1} to the offending word, and {2} to the current target, which is whoever kicked the bot last, or some generic string if it was never kicked (can be changed by the 'victim' argument when creating the bot object).

If you want ipv6 or SSL you have to pass the appropriate factory from the irc lib, like

    import irc.connection
    ...
    bot = orthonazi.OrthoNazi(servers, channels, ...,
          connect_factory = irc.connection.Factory(ipv6=true))


