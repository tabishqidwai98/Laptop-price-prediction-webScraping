from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
import time
# Function to extract Product Title
def get_title(soup):

  try:
    # Outer Tag Object
    title = soup.find("span", attrs={"id": 'productTitle'})

    # Inner NavigatableString Object
    title_value =title.text

    #Title as a string value
    title_string = title_value.strip()

  except AttributeError:
    title_string = " "

  return title_string

# Function to extract Product Price
def get_price(soup):

  try:
    price = soup.find("span", attrs={"class":'a-price-whole'}).text.strip()

  except AttributeError:
    price = " "

  return price

# Function to extract product rating
def get_rating(soup):

  try:
    rating = soup.find("div", attrs={'id':'averageCustomerReviews_feature_div'}).find('div').find('i').string.strip()

  except AttributeError:
    rating = " "

  return rating

# Function to extract number of user reviews
def get_review_count(soup):
  try:
    review_count = soup.find('a', attrs={'id' : 'acrCustomerReviewLink'}).find('span').string.strip()

  except AttributeError:
    review_count = " "

  return review_count

# Function to extract availability status
def get_availability(soup):
  try:
    available = soup.find('div', attrs = {'id': 'availability'}).find('span').text.strip()
    
  except AttributeError:
    available = soup.find('span', attrs={'class' : 'a-size-medium a-color-success'}).text.strip()
    if not available:
      available = soup.find('span', attrs = {'id':'submit.add-to-cart-announce'}).text.strip()
      available = "In stock" if available else "Not Available"
    else:
      available = "Not Available"

  return available

# The webpage URL
def get_amazon_data(url, HEADERS): 
  # HTTP Request
  webpage = requests.get(url, headers=HEADERS)
  print(f'webpage status code: {webpage.status_code}')
  # Soup object containing all data
  soup = BeautifulSoup(webpage.content, "html.parser")
  # Fetch links as List of Tag Objects
  links = soup.find_all("a", attrs={'class':'a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal'})
  # Store the links
  links_list = []
  
  # log the links for use

  # Loop for extracting links from tag objects
  # refined the links_list removing the sponsored ads
  for link in links:
    i = link.get('href')
    if i[0:5] == 'https' or i[0:5] == '/sspa':
        continue
    else:
        links_list.append(i)
    
    #links_list.append(link.get('href'))"""


  d = {"title":[], "price":[], "rating":[], "reviews":[], "availability":[], 'links' : [] }

  # Loop for extracting product details from each link
  for link in links_list:
    try:
      print('=> visiting', f'https://www.amazon.in{link}')
      new_webpage = requests.get("https://www.amazon.in" + link, headers=HEADERS)
      
      new_soup = BeautifulSoup(new_webpage.content, "html.parser")

      # Function calls to display all necessary product information
      # link to each extracted data for use/reference
      d['title'].append(get_title(new_soup))
      d['price'].append(get_price(new_soup))
      d['rating'].append(get_rating(new_soup))
      d['reviews'].append((get_review_count(new_soup)))
      d['availability'].append(get_availability(new_soup))
      d['links'].append(f'https://www.amazon.in{link}')

    except:
      print('=> error occured')
      pass
  
  amazon_df = pd.DataFrame.from_dict(d)
  amazon_df['title'] = amazon_df['title'].replace('', np.nan)
  amazon_df = amazon_df.dropna(subset=['title'])
  return amazon_df

def collect_all(q='laptop', pos=1):
  # Headers for request
  HEADERS = ({'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36', 'Accept-Language': 'en-US, en;q=0.5'})
  results = []
  while True:
    print(f'Collecting data from amazon for {q} : {pos}')
    amazon_url = f"https://www.amazon.in/s?k={q}&page={pos}"
    print(amazon_url)
    out = get_amazon_data(amazon_url, HEADERS)
    print(out.shape)
    if len(out) > 0: #and pos<=2:
      pos+=1
      results.append(out)
      print('results updated')
    else:
      print(len(out), 'items found')
      break

  #print('total nomber of pages visited = Size of the collected data = ', len(results)) # help understanding
  return results

def save_data(data, filename):
  df = pd.concat(data)
  df.to_csv(filename, header=True, index=False)


if __name__ == '__main__': # forget the dataset
    data = collect_all()
    filename = f'laptop_{time.strftime("_%Y%m%d_%H%M")}.csv'
    save_data(data, filename)
