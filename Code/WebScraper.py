from lxml import html
import requests
import pandas as pd
import time


class WebScraper:
    """
    This class aids in retrieving review information such as the review,
    the title of the review, the date of the review and the rating of the review.
    Since each review site's html is constructed differently, site specific
    functions are required. 
    """

    def __init__(self, url = '', site = '', silent = True, url1 = '', url2 = '', increment_string1 = '',
                 increment_string2 = '',total_pages = 1, increment=10, seconds_wait = 1):
        """
        Constructor.
        url: the main url of the website to scrape for one-off webscraping
        site: the site the url is on. i.e. tripadvisor
        silent: determines whether diagnostics are to be displayed
        url1: the first part of a series of urls that doesn't change
        url2: the second part of a series of urls that doesn't change
        increment_string1: the first incremental part of the url
        increment_string2: the second incremental part of the url
        total_pages: total number of pages to increment
        increment: the amount each page should increment each time
        seconds_wait: wait time between requests

        Remark: url1, url2 are the static parts of the urls that do not change in incrementation

        Example:
        url = "https://www.tripadvisor.co.uk/Attraction_Review-g190384-d6755801-Reviews-The_House_of_Dionysus-Paphos_Paphos_District.html"
        url1 + increment_string1 + increment_string1 + increment + increment_string2 + url2= "https://www.tripadvisor.co.uk/Attraction_Review-g190384-d6755801-Reviews-or10-The_House_of_Dionysus-Paphos_Paphos_District.html"

        In the above, url is the main page (this can be left blank).
        url1 = "https://www.tripadvisor.co.uk/Attraction_Review-g190384-d6755801-Reviews"
        increment_string1 = "or"
        increment = 10 (this is how much each page increments by)
        increment_string2 = ""
        url2 = "-The_House_of_Dionysus-Paphos_Paphos_District.html"
        """

        self.url = url
        self.url1 = url1
        self.url2 = url2
        self.first_url = url1 + url2
        self.increment_string1 = increment_string1
        self.increment_string2 = increment_string2
        self.total_pages = total_pages
        self.increment = increment
        self.site = site
        self.seconds_wait = seconds_wait
        self.silent = silent

        self.supported_sites = ['tripadvisor','yelp']

    def findStars(self,x):
        """
        This function extracts the rating from the html element.
        x: string representation of the html element
        returns: int. The rating.
        """

        if self.site.lower() == 'tripadvisor':
            x2 = str(x).replace('>', ' ').split()
            if ('bubble_5"' in x2):
                return 0.5
            elif ('bubble_10"' in x2):
                return 1
            elif ('bubble_15"' in x2):
                return 1.5
            elif ('bubble_20"' in x2):
                return 2
            elif ('bubble_25"' in x2):
                return 2.5
            elif ('bubble_30"' in x2):
                return 3
            elif ('bubble_35"' in x2):
                return 3.5
            elif ('bubble_40"' in x2):
                return 4
            elif ('bubble_45"' in x2):
                return 4.5
            elif ('bubble_50"' in x2):
                return 5
            else:
                return 0
        elif self.site.lower() == 'yelp':
            x2 = str(x)
            if ('0.5 star' in x2):
                return 0.5
            elif ('1.0 star' in x2):
                return 1
            elif ('1.5 star' in x2):
                return 1.5
            elif ('2.0 star' in x2):
                return 2
            elif ('2.5 star' in x2):
                return 2.5
            elif ('3.0 star' in x2):
                return 3
            elif ('3.5 star' in x2):
                return 3.5
            elif ('4.0 star' in x2):
                return 4
            elif ('4.5 star' in x2):
                return 4.5
            elif ('5.0 star' in x2):
                return 5
            else:
                return 0

    def diagnostics(self,*args):
        '''
        This function checks that the lists given as arguments are of equal sizes
        args: An arbitrary number of lists
        silent: A boolean indicating whether diagnostic results are to be displayed
        '''

        # Check if the silent flag is False
        if not self.silent:
            print('Diagnostics: Checking if dataframes are of equal size...')
            
        [print('Size: {}'.format(len(i))) for i in args if not self.silent]

        # The first list size
        l = len(args[0])

        # For each list, check if the sizes are equal to the first list
        for i in args:
            if len(i) != l:
                if not self.silent:
                    print('Unequal Sizes!')
                return False
            
        if not self.silent:
            print('Diagnostics complete!')
            
        return True


    def scrape(self,url = ''):
        '''
        This functioni scrapes relevant review tags from a website url. If a url
        is provided, it is intended for single use of a particular web page. If it
        is not provided, get it from the object.
        url: A string url
        site: A string indicating the site name to be scraped
        silent: A boolean indicating whether diagnostic results are to be displayed
        '''
        
        # A variable to store the success of the read
        success = False

        # If a main url is not provided, get it from the object
        if not url:
            url = self.url

        # These are to store the actual review components
        reviews_array = []
        ratings_array = []
        titles_array = []
        dates_array=[]
        
        # Get the request object from the server
        page = requests.get(url)
        
        # Convert the request content to an html object
        top = html.fromstring(page.content)

        # Site specific html configuration
        if self.site.lower() == 'tripadvisor':
            
            # Get all the review containers
            reviews = top.find_class('review-container')
            
            # Loop through the review containers and get the actual reviews    
            for i in reviews:
                reviews_array.append((i.find_class('entry')[0]).text_content())

            # Within each review container is a class, the name of 
            # which determines the rating to display
            # We use the findStars function to determine the rating 
            # from the class name
            for i in reviews:
                ratings_array.append(self.findStars(html.tostring(i)))

            # Get the titles from each review container
            for i in reviews:
                titles_array.append(i.find_class('noQuotes')[0].text_content())
            
            # Get the dates from each review container
            for i in reviews:
                dates_array.append(i.find_class('ratingDate')[0].text_content())
                
            # Diagnostics
            success = self.diagnostics(ratings_array,reviews_array,dates_array,titles_array)
            
        elif self.site.lower() == 'yelp':
            #rev_class_1 = 'review-content'
            #rev_class_2 = 'p'
            #rat_class = 'biz-rating'
            #dat_class_2 = 'rating-qualifier'
            
            # Get all the review contents
            reviews = top.find_class('review-content')
            
            # Loop through the review contents and get the actual reviews                
            for i in reviews:
                reviews_array.append(i.find('p').text_content())
            
            # Set empty the titles. i.e. there are no titles for yelp
            titles_array = reviews_array.copy()
            
            # Within each review-content is a class called biz-rating, the name of 
            # which determines the rating to display
            # We use the findStars function to determine the rating from the class name
            for i in [getattr(i,'find_class')('biz-rating')[0] for i in reviews]:
                ratings_array.append(self.findStars(html.tostring(i)))   
            
            # Get the dates. When a review is updated, the word updated review is present
            # in the dates string
            for i in reviews:
                dates_array.append((i.find_class('rating-qualifier')[0].text_content()).\
                                   replace('Updated review','').lstrip().rstrip())
            
            # Diagnostics
            success = self.diagnostics(ratings_array,reviews_array,dates_array)
            
        else:
            print('The site {} is not supported'.format(self.site))
            return False

        # Convert to a dataframe
        df_review = pd.DataFrame(reviews_array, columns=['Review'])
        df_ratings = pd.DataFrame(ratings_array, columns=['Rating'])
        df_titles = pd.DataFrame(titles_array, columns=['title'])
        df_reviewdates = pd.DataFrame(dates_array, columns=['date'])
        
        # Consolidate into a single dataframe
        df_fullreview = pd.concat([df_review,df_titles,df_ratings['Rating'], df_reviewdates],axis=1)
        df_fullreview.dropna(inplace=True)
        
        # Combine review and title into a single column
        df_fullreview['fullreview'] = df_fullreview['Review'] + ' ' + df_fullreview['title']

        # Store the reviews to a member variable
        self.reviews = df_fullreview

        return df_fullreview,success
        

    def fullscraper(self):
        '''
        This function increments the site url to the next page according to update 
        criteria and scrapes that page. The full url of subsequent pages is 
        url = url1 + increment_string1 + increment + increment_string2 + url2.
        '''

        # A variable to store the success of the read
        success = False
        
        # Main data frame
        df = pd.DataFrame()
        
        # Progress output
        print('Getting reviews ' + str(0)+'/ '+str(self.total_pages))
        
        # url incrementation differs per website
        if self.site.lower() in self.supported_sites:

            # Keep trying to read the first page until the read is successful
            while not success:

                # read the first page
                df,success = self.scrape(self.first_url)
                if not success:
                    print('Error in reading - Re-reading')
                    
                # Wait for 1 second
                time.sleep(self.seconds_wait)
                    
            print('Getting reviews ' + str(1)+'/ '+str(self.total_pages))

            # now loop through each page and read it
            for i in range(1,self.total_pages):

                # whenever there is an error in reading a page, we retry
                success = False

                # compose the url of this page
                url_temp = self.url1 + self.increment_string1 + str(i*self.increment) + self.increment_string2 + self.url2

                # try to read the page until the read is successful
                while not success:
                    df_temp,success = self.scrape(url_temp)
                    if not success:
                        print('Error in reading - Re-reading')
                            
                    # Wait for 1 second
                    time.sleep(self.seconds_wait)
                
                # Build the dataframe
                df = pd.concat([df,df_temp])
                
                # Print progress
                print('Getting reviews ' + str(i+1)+'/ '+str(self.total_pages))

            print('Complete!!!')

        # Store the read information into a member variable
        self.all_reviews = df.reset_index().iloc[:,1:]
        
        return df.reset_index().iloc[:,1:]



if __name__ == '__main__':
    # Single Usage
    url = "https://www.tripadvisor.co.uk/Attraction_Review-g190384-d6755801-Reviews-The_House_of_Dionysus-Paphos_Paphos_District.html"
    site = 'tripadvisor'

    ms = WebScraper(url, site, silent = False)
    ms.scrape()
    print(ms.reviews)

    # Mutli-page Usage
    inurl1 = "https://www.tripadvisor.co.uk/Attraction_Review-g190384-d6755801-Reviews"
    inurl2 = "-The_House_of_Dionysus-Paphos_Paphos_District.html"

    ms = WebScraper(site='tripadvisor',url1=inurl1,
                          url2=inurl2,increment_string1="-or",increment_string2="",
                          total_pages=20,increment=10,silent=False)

    ms.fullscraper()
    
    print(ms.all_reviews)
