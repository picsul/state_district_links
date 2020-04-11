from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import csv

def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None

        
def is_good_response(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200 
            and content_type is not None 
            and content_type.find('html') > -1)


def log_error(e):
    """
    It is always a good idea to log errors. 
    This function just prints them, but you can
    make it do anything.
    """
    print(e)
    
def write_zip_lists_to_file(rows, filename):
    with open(filename, "w") as f:
        writer = csv.writer(f)
        for row in rows:
            writer.writerow(row)    
    
    
    
names = ["Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware", 
 "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", 
 "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi", 
 "Missouri", "Montana", "Nebraska", "Nevada", "New, Hampshire", "New, Jersey", "New, Mexico", 
 "New, York", "North, Carolina", "North, Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", 
 "Rhode, Island", "South, Carolina", "South, Dakota", "Tennessee", "Texas", "Utah", "Vermont", 
 "Virginia", "Washington", "West, Virginia", "Wisconsin", "Wyoming"]

abbrevs = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN", "IA", 
 "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", 
 "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", 
 "VA", "WA", "WV", "WI", "WY"]

counts = []
totals = []

for i in range(0,50):
    url = "https://www.greatschools.org/schools/districts/" + "/" + names[i] + "/" + abbrevs[i]
    raw_html = simple_get(url)
    html = BeautifulSoup(raw_html, 'html.parser')

    city_district_links = html.find_all('td', class_='city-district-link')
    
    school_names = []
    links_with_text = []
    
    for district_link in city_district_links:
        link = district_link.find('a', href = True)
        try:
            school_names.append(link.text)
        except:
            pass
        if link is not None:
            if link.text: 
                links_with_text.append(link['href'])
    
    complete_links = ["https://www.greatschools.org" + link for link in links_with_text]
            
    school_links = []
        
    for link in complete_links:
        raw_html = simple_get(link)
        html = BeautifulSoup(raw_html, 'html.parser')
        final_link = html.find_all('a', class_='content')
        if len(final_link) > 0:
            school_links.append(final_link[0]['href'])
        else:
            school_links.append("NA")
    
            
    school_lists = zip(school_names, school_links)
    
    filename = names[i] + ".csv"    
                
    write_zip_lists_to_file(school_lists, filename)
    
    # add the counts and totals to the lists
    count = sum(map(lambda x : x == 'NA', school_links))
    total = len(school_links)
    
    counts.append(count)
    totals.append(total)    
    
    pct = count / len(school_links)    
    print(names[i])
    print(pct)
  
# save the missing counts and totals to a csv  
counts_lists = zip(names, counts, totals)
write_zip_lists_to_file(counts_lists, "missing_counts.csv")