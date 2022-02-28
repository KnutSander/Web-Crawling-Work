#!usr/bin/env python3

#-------------------------------------------------------------------------------
# Imports and global variables.
#-------------------------------------------------------------------------------

import sys, requests, validators, time, csv
from bs4 import BeautifulSoup as bs

#-------------------------------------------------------------------------------
# Crawling Class and Routines.
#-------------------------------------------------------------------------------

class ImageCrawlAndLabel:

    def __init__(self, url):
        # List of visited and not visited urls
        self.visUrls = []
        self.notVisUrls = []

        # Save the url, so only urls on the domain and site are gathered
        self.baseUrl = url

        # Store the images in a dictonary, based on their sport
        self.imageLinks = {}

        
    # Returns the main content part of the given url
    # Specifically constructed for The Independent website
    # This disregards any links in headers, footers, etc.
    def getContentSoup(self, url):
        # Get the website content, turn it into soup and extract frameInner/main content
        html = requests.get(url).text
        soup = bs(html, 'html.parser')
        return soup.find(id='frameInner')


    # Gets the images from the soup and labels them based on the url
    def getImages(self, url, soup):
        # Label the images based on their alt text or maybe article title, both?

        # Get the type of sport from the url by trimming it
        # Remove the base url, split on / character
        baseRemoved = url.replace(self.baseUrl, '')
        splitList = baseRemoved.split("/")
        
        # If the list is longer than 2, it means there's a sub-sport section
        # I.e. motorsport/formula-1, so grab the last one before the page name
        if len(splitList) > 2:
            sportType = splitList[1]
        else:
            sportType = splitList[0]

        # Get all the image links from the soup
        images = soup.find_all('img')

        # Loop to put the image links into the dictonary
        for im in images:
            src = im.get('src')
            # Make sure src link is a valid link
            if src and src.startswith("https"):
                if sportType in self.imageLinks:
                    self.imageLinks[sportType].append(src)
                else:
                    self.imageLinks[sportType] = [src]
    
    def getRelatedLinks(self, soup):
        # Extracts every link in the soup
        links = soup.find_all('a')
        
        for link in links:
            path = link.get('href')
            # Make sure the path is under the same domain as the base
            # Also make sure it exists
            if path and path.startswith("/sport/"):
                # Don't add the path if it is in the list to be explored
                # Don't add it if it's been explored already
                if path not in self.visUrls and path not in self.notVisUrls:
                    self.notVisUrls.append(path)

                    
    # Main crawling function that calls everything else
    def crawl(self, url):
        # Get the soup, the main webpage content
        soup = self.getContentSoup(url)

        # Extract all the images from the url
        self.getImages(url, soup)

        # Extract any page links
        self.getRelatedLinks(soup)
        
    
    # Main function that runs the crawling
    def start(self):
        # Get the urls on the base page
        content = self.getContentSoup(self.baseUrl)
        self.getRelatedLinks(content)

        # Set depth to limit crawl depth
        count = 0
        depth = 10
        
        # Main loop, ends either when the list of urls is empty
        # or when the count reaches the depth
        while self.notVisUrls:
            print("Iteration " + str(count))
            url = self.notVisUrls.pop(0)

            # Need to format the link, as it doesn't contain the base
            url = url.replace("/sport/", "")
            url = self.baseUrl + url

            # Crawl the link
            self.crawl(url)

            count += 1
            if count >= depth:
                break

            # Sleep for a second to crawl less aggressivly
            time.sleep(0.5)

        self.outputResult()


    # Prints the image links to a file
    def outputResult(self):
        # Define headers
        fieldnames = ['sport', 'links']
        
        # Open csv file that will hold the results
        with open('result.csv', 'w') as f:

            # Iterate through the dictonary
            for sport, images in self.imageLinks.items():
                f.write(sport + "\n")

                # Iterate through the image links
                for link in images:
                    f.write(link + "\n")

                # Add space after the sport is finished
                f.write("\n")
            

    def testing(self):
        # csv header
        fieldnames = ['name', 'area', 'country_code2', 'country_code3']

        # csv data
        rows = [
            {'name': 'Albania',
             'area': 28748,
             'country_code2': 'AL',
             'country_code3': 'ALB'},
            {'name': 'Algeria',
             'area': 2381741,
             'country_code2': 'DZ',
             'country_code3': 'DZA'},
            {'name': 'American Samoa',
             'area': 199,
             'country_code2': 'AS',
             'country_code3': 'ASM'}
        ]

        with open('countries.csv', 'w', encoding='UTF8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)


# Disregard pictures on the base page
# Extract the content div only, with id frameInner
        
#-------------------------------------------------------------------------------
# Code execution.
#-------------------------------------------------------------------------------

url = "https://www.independent.co.uk/sport/"

# Validate url, just in case
if validators.url(url):
    icl = ImageCrawlAndLabel(url).start()
else:
    print("Url not valid, please provide a valid url")
