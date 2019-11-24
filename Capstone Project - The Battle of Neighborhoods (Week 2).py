#!/usr/bin/env python
# coding: utf-8

# In[1]:


#Download and execute all the libraries

import numpy as np # library to handle data in a vectorized manner

import pandas as pd # library for data analsysis
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

import json # library to handle JSON files

get_ipython().system("conda install -c conda-forge geopy --yes # uncomment this line if you haven't completed the Foursquare API lab")
from geopy.geocoders import Nominatim # convert an address into latitude and longitude values

import requests # library to handle requests
from pandas.io.json import json_normalize # tranform JSON file into a pandas dataframe

# Matplotlib and associated plotting modules
import matplotlib.cm as cm
import matplotlib.colors as colors

# import k-means from clustering stage
from sklearn.cluster import KMeans

#!conda install -c conda-forge folium=0.5.0 --yes # uncomment this line if you haven't completed the Foursquare API lab
import folium # map rendering library

print('Libraries imported.')


# In[2]:


#Importing the dataset 
get_ipython().system("wget -q -O 'newyork_data.json' https://cocl.us/new_york_dataset")
print('Data downloaded!')


# In[6]:


#Load data
with open('newyork_data.json') as json_data:
    newyork_data = json.load(json_data)


# In[7]:


#Define the dataframe columns
column_names = ['Borough', 'Neighborhood', 'Latitude', 'Longitude'] 

# instantiate the dataframe
neighborhoods = pd.DataFrame(columns=column_names)


# In[9]:


#Empty dataframe
neighborhoods


# In[11]:


#Define a list of the neighborhoods
neighborhoods_data = newyork_data['features']

#Put data into the dataframe
for data in neighborhoods_data:
    borough = neighborhood_name = data['properties']['borough'] 
    neighborhood_name = data['properties']['name']
        
    neighborhood_latlon = data['geometry']['coordinates']
    neighborhood_lat = neighborhood_latlon[1]
    neighborhood_lon = neighborhood_latlon[0]
    
    neighborhoods = neighborhoods.append({'Borough': borough,
                                          'Neighborhood': neighborhood_name,
                                          'Latitude': neighborhood_lat,
                                          'Longitude': neighborhood_lon}, ignore_index=True)


# In[12]:


#Examine the results
neighborhoods.head()


# In[13]:


print('The dataframe has {} boroughs and {} neighborhoods.'.format(
        len(neighborhoods['Borough'].unique()),
        neighborhoods.shape[0]
    )
)


# In[14]:


#Use geopy library to get the latitude and longitude values of New York City.
address = 'New York City, NY'

geolocator = Nominatim(user_agent="ny_explorer")
location = geolocator.geocode(address)
latitude = location.latitude
longitude = location.longitude
print('The geograpical coordinate of New York City are {}, {}.'.format(latitude, longitude))


# In[15]:


# create map of New York using latitude and longitude values
map_newyork = folium.Map(location=[latitude, longitude], zoom_start=10)

# add markers to map
for lat, lng, borough, neighborhood in zip(neighborhoods['Latitude'], neighborhoods['Longitude'], neighborhoods['Borough'], neighborhoods['Neighborhood']):
    label = '{}, {}'.format(neighborhood, borough)
    label = folium.Popup(label, parse_html=True)
    folium.CircleMarker(
        [lat, lng],
        radius=5,
        popup=label,
        color='blue',
        fill=True,
        fill_color='#3186cc',
        fill_opacity=0.7,
        parse_html=False).add_to(map_newyork)  
    
map_newyork


# In[16]:


#Filter out the neighborhoods in Manhattan.
manhattan_data = neighborhoods[neighborhoods['Borough'] == 'Manhattan'].reset_index(drop=True)
manhattan_data.head()


# In[ ]:


#Get the geographical coordinates of Manhattan.
address = 'Manhattan, NY'

geolocator = Nominatim(user_agent="ny_explorer")
location = geolocator.geocode(address)
latitude = location.latitude
longitude = location.longitude
print('The geograpical coordinate of Manhattan are {}, {}.'.format(latitude, longitude))


# In[17]:


#Visualize Manhattan the neighborhoods
# create map of Manhattan using latitude and longitude values
map_manhattan = folium.Map(location=[latitude, longitude], zoom_start=11)

# add markers to map
for lat, lng, label in zip(manhattan_data['Latitude'], manhattan_data['Longitude'], manhattan_data['Neighborhood']):
    label = folium.Popup(label, parse_html=True)
    folium.CircleMarker(
        [lat, lng],
        radius=5,
        popup=label,
        color='blue',
        fill=True,
        fill_color='#3186cc',
        fill_opacity=0.7,
        parse_html=False).add_to(map_manhattan)  
    
map_manhattan


# In[18]:


#Explore the neighborhoods using Foursquare API
CLIENT_ID = 'VVOKMVVYGLAFRQCX4ALWCCQJCYYGSZCMTGB2G52IBVI1H5YJ' # your Foursquare ID
CLIENT_SECRET = 'JOX1HBCWQEFPLCOKOHMEF5MN4JWJ15OAL25ZGODYVSVYD5V3' # your Foursquare Secret
VERSION = '20180605' # Foursquare API version

print('Your credentails:')
print('CLIENT_ID: ' + CLIENT_ID)
print('CLIENT_SECRET:' + CLIENT_SECRET)


# In[19]:


#Get the neighborhood's latitude and longitude values.
neighborhood_latitude = manhattan_data.loc[0, 'Latitude'] # neighborhood latitude value
neighborhood_longitude = manhattan_data.loc[0, 'Longitude'] # neighborhood longitude value

neighborhood_name = manhattan_data.loc[0, 'Neighborhood'] # neighborhood name

print('Latitude and longitude values of {} are {}, {}.'.format(neighborhood_name, 
                                                               neighborhood_latitude, 
                                                               neighborhood_longitude))


# In[20]:


#Get top 100 venues of each neighborhood
def getNearbyVenues(names, latitudes, longitudes, radius=500):
    
    venues_list=[]
    for name, lat, lng in zip(names, latitudes, longitudes):
        print(name)
            
        # create the API request URL
        url = 'https://api.foursquare.com/v2/venues/explore?&client_id={}&client_secret={}&v={}&ll={},{}&radius={}&limit={}'.format(
            CLIENT_ID, 
            CLIENT_SECRET, 
            VERSION, 
            lat, 
            lng, 
            radius, 
            LIMIT)
            
        # make the GET request
        results = requests.get(url).json()["response"]['groups'][0]['items']
        
        # return only relevant information for each nearby venue
        venues_list.append([(
            name, 
            lat, 
            lng, 
            v['venue']['name'], 
            v['venue']['location']['lat'], 
            v['venue']['location']['lng'],  
            v['venue']['categories'][0]['name']) for v in results])

    nearby_venues = pd.DataFrame([item for venue_list in venues_list for item in venue_list])
    nearby_venues.columns = ['Neighborhood', 
                  'Neighborhood Latitude', 
                  'Neighborhood Longitude', 
                  'Venue', 
                  'Venue Latitude', 
                  'Venue Longitude', 
                  'Venue Category']
    
    return(nearby_venues)


# In[22]:


LIMIT = 100 # limit of number of venues returned by Foursquare API
radius = 500

manhattan_venues = getNearbyVenues(names=manhattan_data['Neighborhood'],
                                   latitudes=manhattan_data['Latitude'],
                                   longitudes=manhattan_data['Longitude']
                                  )


# In[23]:


print(manhattan_venues.shape)
manhattan_venues.head()


# In[24]:


#Check the number of venues returned to each neighborhood
manhattan_venues['Venue Category'].head()
manhattan_venues.groupby('Neighborhood').count()


# In[25]:


#Check the number of unique categories returned
print('There are {} uniques categories.'.format(len(manhattan_venues['Venue Category'].unique())))


# In[26]:


manhattan_venues['Venue Category'].unique()


# In[27]:


#The following venue categories will be considered when choosing the land.
#Doctor's Office, Medical Center
#School, High School, General College & University
#Pharmacy, Drugstore
#Supermarket, Grocery Store
#Clothing Store
#Bus Station, Bus Stop, Bus Line, Metro Station
#Department Store, Discount Store, Shopping Mall, Convenience Store, Electronics Store
#Bank
#Gas Station
#Gym, Gym / Fitness Center, Weight Loss Center


# In[28]:


#Assigning values for each venue category based on the importance
#Doctor's Office, Medical Center - 10
#School, High School, General College & University - 9
#Pharmacy, Drugstore - 8
#Supermarket, Grocery Store - 7
#Clothing Store - 6
#Bus Station, Bus Stop, Bus Line, Metro Station - 5 
#Department Store, Discount Store, Shopping Mall, Convenience Store, Electronics Store - 4
#Bank - 3
#Gas Station - 2
#Gym, Gym / Fitness Center, Weight Loss Center - 1


# In[29]:


#Assign values for each category and display them in a new column named 'Values'
d = {"Doctor's Office":10, 'Medical Center':10, 'School':9, 'High School':9, 'General College & University':9, 'Pharmacy':8, 'Drugstore':8, 'Supermarket':7, 'Grocery Store':7, 'Clothing Store':6, 'Bus Station':5, 'Bus Stop':5, 'Bus Line':5, 'Metro Station':5, 'Department Store':4, 'Discount Store':4, 'Shopping Mall':4, 'Convenience Store':4, 'Electronics Store':4, 'Bank':3, 'Gas Station':2, 'Gym':1, 'Gym / Fitness Center':1, 'Weight Loss Center':1}
manhattan_venues['Value'] = manhattan_venues['Venue Category'].map(d)
manhattan_venues.head()


# In[30]:


#Check the unique neighborhoods
manhattan_neighborhoods = manhattan_venues['Neighborhood'].unique()
manhattan_neighborhoods

#Calculate the marks scores by each neighborhood

Marble_Hill = manhattan_venues[manhattan_venues.Neighborhood == 'Marble Hill']
Marble_Hill = Marble_Hill['Value'].sum()
print('Marble Hill = ',(Marble_Hill))

Chinatown = manhattan_venues[manhattan_venues.Neighborhood == 'Chinatown']
Chinatown = Chinatown['Value'].sum()
print('Chinatown = ',(Chinatown))

Washington_Heights = manhattan_venues[manhattan_venues.Neighborhood == 'Washington Heights']
Washington_Heights = Washington_Heights['Value'].sum()
print('Washington Heights = ',(Washington_Heights))

Inwood = manhattan_venues[manhattan_venues.Neighborhood == 'Inwood']
Inwood = Inwood['Value'].sum()
print('Inwood = ',(Inwood))

Hamilton_Heights = manhattan_venues[manhattan_venues.Neighborhood == 'Hamilton Heights']
Hamilton_Heights = Hamilton_Heights['Value'].sum()
print('Hamilton_Heights = ',(Hamilton_Heights))

Manhattanville = manhattan_venues[manhattan_venues.Neighborhood == 'Manhattanville']
Manhattanville = Manhattanville['Value'].sum()
print('Manhattanville = ',(Manhattanville))

Central_Harlem = manhattan_venues[manhattan_venues.Neighborhood == 'Central Harlem']
Central_Harlem = Central_Harlem['Value'].sum()
print('Central Harlem = ',(Central_Harlem))

East_Harlem = manhattan_venues[manhattan_venues.Neighborhood == 'East Harlem']
East_Harlem = East_Harlem['Value'].sum()
print('East Harlem = ',(East_Harlem))

Upper_East_Side = manhattan_venues[manhattan_venues.Neighborhood == 'Upper East Side']
Upper_East_Side = Upper_East_Side['Value'].sum()
print('Upper East Side = ',(Upper_East_Side))

Yorkville = manhattan_venues[manhattan_venues.Neighborhood == 'Yorkville']
Yorkville = Yorkville['Value'].sum()
print('Yorkville = ',(Yorkville))

Lenox_Hill = manhattan_venues[manhattan_venues.Neighborhood == 'Lenox Hill']
Lenox_Hill = Lenox_Hill['Value'].sum()
print('Lenox Hill = ',(Lenox_Hill))

Roosevelt_Island = manhattan_venues[manhattan_venues.Neighborhood == 'Roosevelt Island']
Roosevelt_Island = Roosevelt_Island['Value'].sum()
print('Roosevelt Island = ',(Roosevelt_Island))

Upper_West_Side = manhattan_venues[manhattan_venues.Neighborhood == 'Upper West Side']
Upper_West_Side = Upper_West_Side['Value'].sum()
print('Upper West Side = ',(Upper_West_Side))

Lincoln_Square = manhattan_venues[manhattan_venues.Neighborhood == 'Lincoln Square']
Lincoln_Square = Lincoln_Square['Value'].sum()
print('Lincoln_Square = ',(Lincoln_Square))

Clinton = manhattan_venues[manhattan_venues.Neighborhood == 'Clinton']
Clinton = Clinton['Value'].sum()
print('Clinton = ',(Clinton))

Midtown = manhattan_venues[manhattan_venues.Neighborhood == 'Midtown']
Midtown = Midtown['Value'].sum()
print('Midtown = ',(Midtown))

Murray_Hill = manhattan_venues[manhattan_venues.Neighborhood == 'Murray Hill']
Murray_Hill = Murray_Hill['Value'].sum()
print('Murray Hill = ',(Murray_Hill))

Chelsea = manhattan_venues[manhattan_venues.Neighborhood == 'Chelsea']
Chelsea = Chelsea['Value'].sum()
print('Chelsea = ',(Chelsea))

Greenwich_Village = manhattan_venues[manhattan_venues.Neighborhood == 'Greenwich Village']
Greenwich_Village = Greenwich_Village['Value'].sum()
print('Greenwich Village = ',(Greenwich_Village))

East_Village = manhattan_venues[manhattan_venues.Neighborhood == 'East Village']
East_Village = East_Village['Value'].sum()
print('East Village = ',(East_Village))

Lower_East_Side = manhattan_venues[manhattan_venues.Neighborhood == 'Lower East Side']
Lower_East_Side = Lower_East_Side['Value'].sum()
print('Lower East Side = ',(Lower_East_Side))

Tribeca = manhattan_venues[manhattan_venues.Neighborhood == 'Tribeca']
Tribeca = Tribeca['Value'].sum()
print('Tribeca = ',(Tribeca))

Little_Italy = manhattan_venues[manhattan_venues.Neighborhood == 'Little Italy']
Little_Italy = Little_Italy['Value'].sum()
print('Little Italy = ',(Little_Italy))

Soho = manhattan_venues[manhattan_venues.Neighborhood == 'Soho']
Soho = Soho['Value'].sum()
print('Soho = ',(Soho))

West_Village = manhattan_venues[manhattan_venues.Neighborhood == 'West_Village']
West_Village = West_Village['Value'].sum()
print('West Village = ',(West_Village))

Manhattan_Valley = manhattan_venues[manhattan_venues.Neighborhood == 'Manhattan_Valley']
Manhattan_Valley = Manhattan_Valley['Value'].sum()
print('Manhattan Valley = ',(Manhattan_Valley))

Morningside_Heights = manhattan_venues[manhattan_venues.Neighborhood == 'Morningside Heights']
Morningside_Heights = Morningside_Heights['Value'].sum()
print('Morningside Heights = ',(Morningside_Heights))

Gramercy = manhattan_venues[manhattan_venues.Neighborhood == 'Gramercy']
Gramercy = Gramercy['Value'].sum()
print('Gramercy = ',(Gramercy))

Battery_Park_City = manhattan_venues[manhattan_venues.Neighborhood == 'Battery Park City']
Battery_Park_City = Battery_Park_City['Value'].sum()
print('Battery Park City = ',(Battery_Park_City))

Financial_District = manhattan_venues[manhattan_venues.Neighborhood == 'Financial District']
Financial_District = Financial_District['Value'].sum()
print('Financial District = ',(Financial_District))

Carnegie_Hill = manhattan_venues[manhattan_venues.Neighborhood == 'Carnegie Hill']
Carnegie_Hill = Carnegie_Hill['Value'].sum()
print('Carnegie Hill = ',(Carnegie_Hill))

Noho = manhattan_venues[manhattan_venues.Neighborhood == 'Noho']
Noho = Noho['Value'].sum()
print('Noho = ',(Noho))

Civic_Center = manhattan_venues[manhattan_venues.Neighborhood == 'Civic Center']
Civic_Center = Civic_Center['Value'].sum()
print('Civic Center = ',(Civic_Center))

Midtown_South = manhattan_venues[manhattan_venues.Neighborhood == 'Midtown South']
Midtown_South = Midtown_South['Value'].sum()
print('Midtown South = ',(Midtown_South))

Sutton_Place = manhattan_venues[manhattan_venues.Neighborhood == 'Sutton Place']
Sutton_Place = Sutton_Place['Value'].sum()
print('Sutton Place = ',(Sutton_Place))

Turtle_Bay = manhattan_venues[manhattan_venues.Neighborhood == 'Turtle Bay']
Turtle_Bay = Turtle_Bay['Value'].sum()
print('Turtle Bay = ',(Turtle_Bay))

Tudor_City = manhattan_venues[manhattan_venues.Neighborhood == 'Tudor City']
Tudor_City = Tudor_City['Value'].sum()
print('Tudor City = ',(Tudor_City))

Stuyvesant_Town = manhattan_venues[manhattan_venues.Neighborhood == 'Stuyvesant Town']
Stuyvesant_Town = Stuyvesant_Town['Value'].sum()
print('Stuyvesant Town = ',(Stuyvesant_Town))

Flatiron = manhattan_venues[manhattan_venues.Neighborhood == 'Flatiron']
Flatiron = Flatiron['Value'].sum()
print('Flatiron = ',(Flatiron))

Hudson_Yards = manhattan_venues[manhattan_venues.Neighborhood == 'Hudson Yards']
Hudson_Yards = Hudson_Yards['Value'].sum()
print('Hudson Yards = ',(Hudson_Yards))
# In[34]:


#CONCLUSION

#As per the marks, it can be said that the Neighborhood: 'Soho' has the best facilities (essential facilities) out of all the neighborhoods located in Manhattan.For more insights, please refer to the report submitted along with this.

#Thank you.

