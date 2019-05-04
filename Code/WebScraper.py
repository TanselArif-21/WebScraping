from lxml import html
import requests
import pandas as pd
import time


class WebScraper:

    def __init__(self, url = '', site = '', silent = True, url1 = '', url2 = '', increment_string1 = '',
                 increment_string2 = '',total_pages = 1, increment=10, output_file = ''):
        self.url = url
        self.url1 = url1
        self.url2 = url2
        self.first_url = url1 + url2
        self.increment_string1 = increment_string1
        self.increment_string2 = increment_string2
        self.total_pages = total_pages
        self.increment = increment
        self.output_file = output_file
        self.site = site
        self.silent = silent

    def findStars(self,x):
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
        
        if not self.silent:
            print('Diagnostics: Checking if dataframes are of equal size...')
            
        [print('Size: {}'.format(len(i))) for i in args if not self.silent]
        
        l = len(args[0])
        
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
        This functioni scrapes relevant review tags from a website url
        url: A string url
        site: A string indicating the site name to be scraped
        silent: A boolean indicating whether diagnostic results are to be displayed
        '''
        # A variable to store the success of the read
        success = False

        if not url:
            url = self.url

        # Get the request object from the server
        page = requests.get(url)
        
        # Convert the request content to an html object
        top = html.fromstring(page.content)
        
        # These are the class names
        rev_class_1 = ''
        rev_class_2 = ''
        rat_class = ''
        title_class = ''
        dat_class = ''
        dat_class_2 = ''
        
        if self.site.lower() == 'tripadvisor':
            
            # Get all the innerBubble classes which contain the reviews as well as 
            # any responses to these reviews
            reviews = top.find_class('review-container')
            
            # This is to store the actual reviews
            reviews_array = []

            # Loop through the reviews    
            for i in reviews:
                reviews_array.append((i.find_class('entry')[0]).text_content())

            # Within each review container is a class, the name of 
            # which determines the rating to display
            # We use the findStars function to determine the rating 
            # from the class name
            ratings_array = []
            for i in reviews:
                ratings_array.append(self.findStars(html.tostring(i)))

            # Get the titles
            titles_array = []
            for i in reviews:
                titles_array.append(i.find_class('noQuotes')[0].text_content())
            
            # Get the dates
            dates_array=[]
            for i in reviews:
                dates_array.append(i.find_class('ratingDate')[0].text_content())
                
            # Diagnostics
            success = self.diagnostics(ratings_array,reviews_array,dates_array,titles_array)
            
        elif self.site.lower() == 'yelp':
            #rev_class_1 = 'review-content'
            #rev_class_2 = 'p'
            #rat_class = 'biz-rating'
            #dat_class_2 = 'rating-qualifier'
            
            # Get all the innerBubble classes which contain the reviews as well as 
            # any responses to these reviews
            reviews = top.find_class('review-content')
            
            # Loop through the reviews
            reviews_array = []
                
            for i in reviews:
                reviews_array.append(i.find('p').text_content())
            
            # Set empty the titles
            titles_array = reviews_array.copy()
            
            # Within each review-content is a class called biz-rating, the name of 
            # which determines the rating to display
            # We use the findStars function to determine the rating from the class name
            ratings_array = []

            for i in [getattr(i,'find_class')('biz-rating')[0] for i in reviews]:
                ratings_array.append(self.findStars(html.tostring(i)))   
            
            # Get the dates. When a review is updated, the word updated review is present
            # in the dates string
            dates_array=[]
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
        
        # Consolidate into a dataframe
        df_fullreview = pd.concat([df_review,df_titles,df_ratings['Rating'],\
                                   df_reviewdates],axis=1)
        df_fullreview.dropna(inplace=True)
        
        # Combine review and title into a single column
        df_fullreview['fullreview'] = df_fullreview['Review'] + ' ' + df_fullreview['title']

        self.reviews = df_fullreview

        return df_fullreview,success
        

    def fullscraper(self):
        '''
        This function increments the site url to the next page according to update 
        criteria and scrapes that page. The full url of subsequent pages is 
        url = url1 + increment_string1 + url2 + increment_string2. 
        In cases of error in reading information, attempts are made to re-read data.
        first_url: A string url. The main url page
        url1, url2: The static parts of the urls that do not change in incrementation
        increment_string1, increment_string2: The parts of the url that change
        total_pages: The number of total pages. Integer
        output_file: The file name to output. If empty string, it doesn't save a file
        site: A string indicating the site name to be scraped
        '''
        success = False
        
        # Main data frame
        df = pd.DataFrame()
        
        # Progress output
        print('Getting reviews ' + str(0)+'/ '+str(self.total_pages))
        
        # url incrementation differs per website
        if self.site.lower() in ['tripadvisor','yelp']:
            while not success:
                df,success = self.scrape(self.first_url)
                if not success:
                    print('Error in reading - Re-reading')
                    
                # Wait for 1 second
                time.sleep(1)
                    
            print('Getting reviews ' + str(1)+'/ '+str(self.total_pages))
            
            for i in range(1,self.total_pages):
                success = False
                url_temp = self.url1 + self.increment_string1 + str(i*self.increment) +\
                self.increment_string2 + self.url2
                
                if (i%10 == 0) or (i == self.total_pages):
                    while not success:
                        df_temp,success = self.scrape(url_temp)
                        if not success:
                            print('Error in reading - Re-reading')
                            
                        # Wait for 1 second
                        time.sleep(1)
                else:
                    while not success:
                        df_temp,success = self.scrape(url_temp)
                        if not success:
                            print('Error in reading - Re-reading')
                            
                        # Wait for 1 second
                        time.sleep(1)
                
                # Build the dataframe
                df = pd.concat([df,df_temp])
                
                # Print progress
                print('Getting reviews ' + str(i+1)+'/ '+str(self.total_pages))
            print('Complete!!!')

        self.all_reviews = df.reset_index().iloc[:,1:]
        
        return df.reset_index().iloc[:,1:]



if __name__ == '__main__':
    # Single Usage
    url = "https://www.tripadvisor.co.uk/Restaurant_Review-g186338-d2570383-Reviews-Cafe_in_the_Crypt-London_England.html"
    site = 'tripadvisor'

    ms = WebScraper(url, site, silent = False)
    ms.scrape()
    print(ms.reviews)

    # Mutli-page Usage
    inurl1 = "https://www.tripadvisor.co.uk/Restaurant_Review-g186338-d2570383-Reviews"
    inurl2 = "-Cafe_in_the_Crypt-London_England.html"

    ms = WebScraper(site='tripadvisor',url1=inurl1,
                          url2=inurl2,increment_string1="-or",increment_string2="",
                          total_pages=20,increment=10,output_file='testing.csv',silent=False)

    ms.fullscraper()
    
    print(ms.all_reviews)
