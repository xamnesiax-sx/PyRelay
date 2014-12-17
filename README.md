PyRelay
=======

A small project created to circumvent annoying outbound port filtering; set up a relay on a trusted network with an unrestricted outbound firewall, then set up the client behind the restrictive firewall, connect to the local client using whichever TCP streaming program you need to use (such as SSH), fill in the info and your connection will be tunnelled through the internet of the relay network. Ports can be bootstrapped aswell, for example, your connection is tunnelled through port 80 to the relay; you can specify the IP and port you want your data to be sent to on the target server.
