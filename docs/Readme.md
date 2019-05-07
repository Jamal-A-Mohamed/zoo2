## Create list of animals to download data for:
1. List of animals should be added to animal_list1.txt in Data directory (one per line)

## Run Scripts to download data from Wikipedia

2.   Run DownloadRam.py to download Wikipedia summary 
     * Uses [wikipedia](https://github.com/goldsmith/Wikipedia)  python library - [Documentation](https://wikipedia.readthedocs.io/en/latest/)
     * Wikipedia API - [Documentation](https://www.mediawiki.org/wiki/API:Main_page)
	
3. Run DownloadImages.py to download images using [requests](https://pypi.org/project/requests/) python library
   * [Documentation](http://python-requests.org/)
   * Change RESIZED_WIDTH parameter in DownloadImages.py to adjust image resizing dimensions if desired.
 
4. Run wikibox.py to scrap taxonomy information from wiki infobox using [BeautifulSoup](https://pypi.org/project/beautifulsoup4/)
   * [Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
 
 
 These steps should create:
  * JSON files in Data/animals/
  * Images in Static/Images/
  
## MongoDB
5. Follow instructions from https://www.mongodb.com/ to download binaries and add to path

6. Create DB data/db/ path and Launch mongod daemon
   * $ mongod --dbpath ~/data/db/ & disown
   
7. Modify database settings in DataLoader.py and run it to load animals JSON files into MongoDB database

[MongoDB Documentation](https://docs.mongodb.com/ecosystem/drivers/python/)

## Add MongoDB indexes
8. (Optional) Manually add MongoDB indexes.
   * Sample images provided in docs/indexing folder
   * [MongoDB Indexing Documentation](https://docs.mongodb.com/manual/indexes/)
   
   
## Setup Server (Sample Commands based on Debian install may not be fully accurate)
1. Install python 3.6+, and requirements
   * $ python3 -m pip install --user -r requirements.txt
2. Install on Debian using APT:
    * $ sudo apt update
    * $ sudo apt-get install apache2 apache2-base apache2-mpm-prefork apache2-utils libexpat1 ssl-cert
    * $ install git libapache2-mod-wsgi-py3
3. Setup Apache
   * Link Static to Apache static to serve static data
     * $ sudo ln -s ~/zoo/Static/ /var/www/html/Static
   * Edit Apache config
     * $ sudo vi /etc/apache2/sites-enabled/000-default.conf
4. Set up TLS/SSL 