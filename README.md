# Overview

qfracture is a Qt based front end exposing a fracture project. The interface
allows for data browsing and searching as well as data interaction.

For full details on fracture please see: 

https://github.com/mikemalinowski/fracture


# Browsing

qFracture displays a browsing panel which allows you to navigate data in a 
natural way - which is particularly useful if your data is file based. 

![alt text](https://github.com/mikemalinowski/qfracture/blob/master/docs/qfracture_browse.png?raw=true)

Right clicking a _Data Asset_ exposes the functionality bound to that data. 


# Searching

Within qFracture you can perform searches against your dataset. Fracture is 
 very quick at resolving searches - so this can be a preferable mechanism
 when interacting with data if you have a reasonable idea of what you're looking
 for. 
 
When no search entries are present this view will show any _Data Elements_ which
you have marked as being favourites - allowing them to be accessed very quickly
with no overhead. 


# Setting up a Project


The qFracture UI offers a wizard to make it easy to setup a new fracture 
project. This guides you through the process of defining the data structure 
location, the plugin locations and where you want to save your project file.

![alt text](https://github.com/mikemalinowski/qfracture/blob/master/docs/qfracture_wizard.png?raw=true)

It will also initiate a short scan of your data location. Depending on how
big your data set this can take a little time. 

Upon completion your data set is entirely searchable.


## System Tray


The qFracture Ui only performs a deep scan during the first time setup. Beyond
that, each location is re-scanned as you traverse those locations through the
browser panel.

If you want time based scans to occur you can trigger the __System Tray__ 
application (which is launchable from the _Settings_ tab). The system tray
allows you to specify an interval time (in seconds), and enable or disable
timed scans. 

This approach allows the scanning to occur in a completely different process
to any qFracture instances which can aid performance, especially if you're 
running qFracture from within environments such as Maya or Max etc. 


# Collaboration

I am always open to collaboration, so if you spot bugs lets me know, or if
you would like to contribute or get involved just shout!


# Compatibility

Launchpad has been tested under Python 2.7 and Python 3.7 on Windows and Ubuntu.
