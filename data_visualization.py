import os
from collections import Counter
import string

import pandas as pd
import geopandas as gpd
import numpy as np

from bokeh.models import (ColorBar,
                          ColumnDataSource,
                          CustomJS, 
                          GeoJSONDataSource, 
                          HoverTool,
                          LinearColorMapper, 
                          Select,
                          Div)
from bokeh.transform import transform
from bokeh.palettes import PiYG
from bokeh.plotting import figure
from bokeh.layouts import column, row
from bokeh.util.browser import view

from html_template import create_html_template

from utils import resources_dir
from utils import docs_dir

# general front style attributes for entire project
font ='Helvetica'
text_color = "#737373"
font_style = 'normal'
title_font_size = '14pt'
axis_label_font_size = '12pt'
major_label_font_size = '12pt'

def create_sentiment_data_source(df, selection_day_range):
    # create sources dict containing each ColumnDataSource 
    # Important note: this does represent each day rather a reduced selection 
    # to 6 days
    s_sources = []
    for day in selection_day_range:
        x = df.polarity[df['day_range'] == day]
        y = df.subjectivity[df['day_range'] == day]
        user = df.user_name[df['day_range'] == day]
        created = df.created[df['day_range'] == day]
        location = df.user_location_cleaned[df['day_range'] == day].apply(lambda x: string.capwords(x))
        text = df.text[df['day_range'] == day]
        
        source = ColumnDataSource(data={'s_x': x,
                                        's_y': y,
                                        'user': user,
                                        'created': created,
                                        'location': location,
                                        'tweet': text
                                        })
        s_sources.append(source) # create list of DataSource objects
    
    # assign dummy source including all unfiltered data points for JS callback
    # and 6 actual date ranges to variables
    s_source_dummy = ColumnDataSource(data={'s_x': df.polarity,
                                        's_y': df.subjectivity,
                                        'user': df.user_name,
                                        'created': df.created,
                                        'location': df.user_location_cleaned.apply(lambda x: string.capwords(x)),
                                        'tweet': df.text
                                        })
    s_source_full = ColumnDataSource(data={'s_x': df.polarity,
                                        's_y': df.subjectivity,
                                        'user': df.user_name,
                                        'created': df.created,
                                        'location': df.user_location_cleaned.apply(lambda x: string.capwords(x)),
                                        'tweet': df.text
                                        })
    
    return s_source_dummy, s_source_full, s_sources

def max_log_city_count_per_day(df, selection_day_range):
    # function is required to calculate the max count value per city for
    # each day. In this way the sizes of the circle bins can later be
    # normalized over the course of the datesof the dataset.
    
    log_city_max_day_list = []
    
    # iterate over selection day range and filter df_day accordingly to the
    # days
    for day in selection_day_range:
        df_day = df[df['day_range'] == day]
        
        # save cities to list in order to count the entries to a dict by using
        # Counter
        city_list = df_day['user_location_cleaned'].tolist()
        city_count = Counter(city_list)
        
        # create a new empty dataframe and parse the counted city dict into
        # the df
        df_cities = pd.DataFrame()
        df_cities = df_cities.append(city_count, ignore_index=True).T # T= transpose
        df_cities.columns = ['tweet_count'] # rename column
        
        # To better normalize the data for binning to generate evenly
        # distributed circle/scatter sizes, log values of the city counts are
        # calculated and appended to a list in order to get the maximum value
        # over the iterated date / day datasets
        df_cities['log_tweet_count'] = np.log(df_cities['tweet_count'])
        log_city_max_day_list.append(df_cities['log_tweet_count'].max())
    
    # save the max value of the log city count to a variable and return the
    # value for further processing
    log_city_max_day = max(log_city_max_day_list)
    
    # repeat for full dataset
    city_list = df['user_location_cleaned'].tolist()
    city_count = Counter(city_list)
    df_cities = pd.DataFrame()
    df_cities = df_cities.append(city_count, ignore_index=True).T # T= transpose
    df_cities.columns = ['tweet_count'] # rename column
    df_cities['log_tweet_count'] = np.log(df_cities['tweet_count'])
    log_city_max_full_dataset = df_cities['log_tweet_count'].max()

    return log_city_max_day, log_city_max_full_dataset

def create_city_count_dataframe(df_day, log_city_max_day):
    
    # process city count and long lat data for scatter plot
    # create new df_cities dataframe containing city name as index, city count
    # long and lat data
    city_list = df_day['user_location_cleaned'].tolist()
    city_count = Counter(city_list)
    df_cities = pd.DataFrame()
    df_cities = df_cities.append(city_count, ignore_index=True).T # T= transpose
    df_cities.columns = ['tweet_count'] # rename column
    
    # creating city dict with long and lat for subequent df mapping
    longitude_list = df_day['longitude'].tolist() 
    latitude_list = df_day['latitude'].tolist()
    city_dict_longitude = dict(zip(city_list, longitude_list))
    city_dict_latitude = dict(zip(city_list, latitude_list))
    
    # map against city_dict_longitude and city_dict_latitude to add to
    # these columns the long, lat information based on city name
    df_cities.loc[:, 'longitude'] = df_cities.index.map(city_dict_longitude)
    df_cities.loc[:, 'latitude'] = df_cities.index.map(city_dict_latitude)
    
    # normalize tweet_count for plotting by normalizing to log values of
    # tweet counts and binning to 10 categories, create evenly distributed 
    # values as bins and assign to bin labels 
    df_cities['log_tweet_count'] = np.log(df_cities['tweet_count'])
    bins = np.linspace(0, log_city_max_day, 11).tolist()
    labels = [x for x in range(1, 11)]

    df_cities['tweet_count_bins'] = pd.cut(df_cities['log_tweet_count'], bins=bins, labels=labels)
    df_cities = df_cities.fillna(1)

    return df_cities

def create_geo_data_source(df, selection_day_range):
    
    # call max_log_city_count_per_day function to get the maximum log city
    # count per day / date iterated over the selection. This is required to
    # normalize scatter bubbles not relatively over one day/date dataset but
    # rather over the whole sequence to compare if tweet numbers in a certain
    # cities have changed over the course the timeline
    (log_city_max_day,
    log_city_max_full_dataset) = max_log_city_count_per_day(df,
                                                           selection_day_range)
    
    # create sources dict containing each ColumnDataSource 
    # Important note: this does represent each day rather a reduced selection 
    # to 6 days
    g_sources = []
    for day in selection_day_range:
        df_day = df[df['day_range'] == day]
        df_cities = create_city_count_dataframe(df_day, log_city_max_day)
        
        x = df_cities.loc[:, 'latitude']
        y = df_cities.loc[:, 'longitude']     
        count = df_cities.loc[:, 'tweet_count']
        name = df_cities.index.str.capitalize()
        bins = df_cities.loc[:, 'tweet_count_bins'].astype(int).divide(20)
        
        source = ColumnDataSource(data={'g_x': x,
                                        'g_y': y,
                                        'count': count,
                                        'name': name,
                                        'bins': bins
                                        })
        g_sources.append(source) # create list of DataSource objects
    
    # create city count df by using unfiltered full df and log_city_max value
    # for the full dataset
    df_full = create_city_count_dataframe(df, log_city_max_full_dataset)
    
    # create dummy data sources for the JS bokeh callback using full dataset
    # the dummy data set is required as a placeholder and is deleted after
    # changing dataset within the JS callback
    g_source_dummy = ColumnDataSource(data={'g_x': df_full.loc[:, 'latitude'],
                                            'g_y': df_full.loc[:, 'longitude'],
                                            'count': df_full.loc[:, 'tweet_count'],
                                            'name': df_full.index.str.capitalize(),
                                            'bins': df_full.loc[:, 'tweet_count_bins'].astype(int).divide(20)
                                            })

    g_source_full = ColumnDataSource(data={'g_x': df_full.loc[:, 'latitude'],
                                            'g_y': df_full.loc[:, 'longitude'],
                                            'count': df_full.loc[:, 'tweet_count'],
                                            'name': df_full.index.str.capitalize(),
                                            'bins': df_full.loc[:, 'tweet_count_bins'].astype(int).divide(20)
                                            })
    
    return g_source_dummy, g_source_full, g_sources
    
def create_bokeh_plot(df,
                      s_source_dummy,
                      s_source_full,
                      s_sources,
                      g_source_dummy,
                      g_source_full,
                      g_sources,
                      selection_dates,
                      selection_day_range):
    
    # assign unique variables for each DataSource required for each date within
    # the data timeline
    s_source1 = s_sources[0]
    s_source2 = s_sources[1]
    s_source3 = s_sources[2]
    s_source4 = s_sources[3]
    s_source5 = s_sources[4]
    s_source6 = s_sources[5]
    g_source1 = g_sources[0]
    g_source2 = g_sources[1]
    g_source3 = g_sources[2]
    g_source4 = g_sources[3]
    g_source5 = g_sources[4]
    g_source6 = g_sources[5]
    
    # create sentiment polarity-subjectivity scatter plot
    s_p = figure(plot_width=450,
               plot_height=450,
               x_axis_label='Polarity',
               y_axis_label='Subjectivity',
               tools=["crosshair","pan","box_zoom","reset"])
    
    # adjusting title text properties of the polarity-subjectivity scatter plot  
    s_p.title.text = "Tweet Text Sentiment Analysis"
    s_p.title.align = "center"
    s_p.title.text_color = text_color
    s_p.title.text_font_size = title_font_size
    s_p.title.text_font = font
    s_p.title.text_font_style = font_style
    
    # adjusting axis properties of the polarity-subjectivity scatter plot
    s_p.axis.axis_label_text_font_style = font_style
    s_p.axis.axis_label_text_font_size = axis_label_font_size
    s_p.axis.axis_label_text_font = font
    s_p.axis.axis_label_text_color = text_color
    s_p.axis.major_label_text_font_size = major_label_font_size
    s_p.axis.major_label_text_font = font
    s_p.axis.major_label_text_color = text_color
    s_p.axis.axis_line_color = text_color
    s_p.xaxis.minor_tick_line_color = None
    s_p.yaxis.minor_tick_line_color = None

    # configure fixed axis numbers for consistent axis properties along
    # different scaled data
    s_p.y_range.start = -0.1
    s_p.y_range.end = 1.1
    s_p.x_range.start = -1.1
    s_p.x_range.end = 1.1
    
    # configure color palettes low-high for scatters resembling positive or 
    # negative sentiments
    PiYG_reverse = tuple(reversed(PiYG[5]))
    mapper = LinearColorMapper(palette=PiYG_reverse, low=-1, high=1)
    
    # add scatter points to polarity-subjectivity scatter plot 
    circle_glyph = s_p.circle(x='s_x', 
                        y='s_y',
                        source=s_source_dummy,
                        size=7, 
                        line_color='grey',
                        fill_color=transform('s_x', mapper),
                        fill_alpha=0.5,
                        hover_color ="pink")
    
    # add hover tool to polarity-subjectivity scatter plot
    s_p.add_tools(HoverTool(renderers = [circle_glyph],
                      tooltips = [("Polarity","@s_x"),
                                  ("Subjectivity","@s_y"),
                                  ("User","@user"),
                                  ("Date","@created"),
                                  ("Location","@location"),
                                  ("Tweet", "@tweet")
                                  ]))
    
    # load shapefile of germany 
    sf = gpd.read_file(os.path.join(resources_dir, 'shapefiles_ger', 'DEU_adm1.shp'))
    
    # Input GeoJSON source that contains features for plotting. This format 
    # is required for plotting shapefiles in bokeh plots
    geosource = GeoJSONDataSource(geojson = sf.to_json())
    
    # create empty map figure object
    g_p = figure(title = 'Tweet Locations',
               plot_height = 450,
               plot_width = 400,
               tools=["crosshair","pan","box_zoom","reset"])
    
    # adjusting title text properties of the geo plot
    g_p.title.text = "Tweet Locations"
    g_p.title.align = "center"
    g_p.title.text_color = text_color
    g_p.title.text_font_size = title_font_size
    g_p.title.text_font = font
    g_p.title.text_font_style = font_style
    
    # adjusting axis properties of the geo plot
    g_p.xgrid.grid_line_color = None
    g_p.ygrid.grid_line_color = None 
    g_p.xaxis.minor_tick_line_color = None
    g_p.yaxis.minor_tick_line_color = None
    g_p.xaxis.major_tick_line_color = None
    g_p.yaxis.major_tick_line_color = None
    g_p.axis.axis_label_text_color = None
    g_p.axis.major_label_text_color = None
    g_p.axis.axis_line_color = None
    
    # create patches of the german states using the geosources
    g_p.patches('xs','ys', 
                source = geosource,
                fill_color = '#ffbaba',
                line_color = '#f5f5f5',
                line_width = 1, 
                fill_alpha = 1)
    
    # geo source scatter plot of city counts
    scatter = g_p.scatter('g_x',
                          'g_y', 
                           source=g_source_dummy,
                           line_color='white',
                           fill_color='teal',
                           fill_alpha=0.5,
                           radius='bins'
                           )
    
    # create hover tool
    g_p.add_tools(HoverTool(renderers = [scatter],
                      tooltips = [("City","@name"),
                                  ("Tweets","@count"),
                                  ("Coordinates","@g_x, @g_y")
                                  ]))
    
    
    # requires to add extra quotes to the selection dates for the if queries 
    # inside the js callback syntax
    selection_dates_js = ["'" + option + "'" for option in selection_dates]

    # add custom JS callback for changing data based on date range
    callback = CustomJS(args={
      'source1': s_source_dummy, 
      'source2': s_source_full,
      'source3': s_source1,
      'source4': s_source2,
      'source5': s_source3,
      'source6': s_source4,
      'source7': s_source5,
      'source8': s_source6,
      'source9': g_source_dummy, 
      'source10': g_source_full,
      'source11': g_source1,
      'source12': g_source2,
      'source13': g_source3,
      'source14': g_source4,
      'source15': g_source5,
      'source16': g_source6}, code="""
      
        var data1 = source1.data;
        var data2 = source2.data;
        var data3 = source3.data;
        var data4 = source4.data;
        var data5 = source5.data;
        var data6 = source6.data;
        var data7 = source7.data;
        var data8 = source8.data;
        var data9 = source9.data;
        var data10 = source10.data;
        var data11 = source11.data;
        var data12 = source12.data;
        var data13 = source13.data;
        var data14 = source14.data;
        var data15 = source15.data;
        var data16 = source16.data;
        
        var f = cb_obj.value;
      
        if (f == %s) {
          for (var e in data1) delete data1[e];
          for (var g in data9) delete data9[g];
        
          data1['s_x'] = data2['s_x'];
          data1['s_y'] = data2['s_y'];
          data1['user'] = data2['user'];
          data1['created'] = data2['created'];
          data1['location'] = data2['location'];
          data1['tweet'] = data2['tweet'];
          
          data9['g_x'] = data10['g_x'];
          data9['g_y'] = data10['g_y'];
          data9['name'] = data10['name'];
          data9['count'] = data10['count'];
          data9['bins'] = data10['bins'];
        }
      
        if (f == %s) {
          for (var e in data1) delete data1[e];
          for (var g in data9) delete data9[g];
          
          data1['s_x'] = data3['s_x'];
          data1['s_y'] = data3['s_y'];
          data1['user'] = data3['user'];
          data1['created'] = data3['created'];
          data1['location'] = data3['location'];
          data1['tweet'] = data3['tweet'];
          
          data9['g_x'] = data11['g_x'];
          data9['g_y'] = data11['g_y'];
          data9['name'] = data11['name'];
          data9['count'] = data11['count'];
          data9['bins'] = data11['bins'];
        }
      
        if (f == %s) {
          for (var e in data1) delete data1[e];
          for (var g in data9) delete data9[g];
        
          data1['s_x'] = data4['s_x'];
          data1['s_y'] = data4['s_y'];
          data1['user'] = data4['user'];
          data1['created'] = data4['created'];
          data1['location'] = data4['location'];
          data1['tweet'] = data4['tweet'];
          
          data9['g_x'] = data12['g_x'];
          data9['g_y'] = data12['g_y'];
          data9['name'] = data12['name'];
          data9['count'] = data12['count'];
          data9['bins'] = data12['bins'];
        }
        
        if (f == %s) {
          for (var e in data1) delete data1[e];
          for (var g in data9) delete data9[g];
          
          data1['s_x'] = data5['s_x'];
          data1['s_y'] = data5['s_y'];
          data1['user'] = data5['user'];
          data1['created'] = data5['created'];
          data1['location'] = data5['location'];
          data1['tweet'] = data5['tweet'];
          
          data9['g_x'] = data13['g_x'];
          data9['g_y'] = data13['g_y'];
          data9['name'] = data13['name'];
          data9['count'] = data13['count'];
          data9['bins'] = data13['bins'];
        }
        
        if (f == %s) {
          for (var e in data1) delete data1[e];
          for (var g in data9) delete data9[g];
          
          data1['s_x'] = data6['s_x'];
          data1['s_y'] = data6['s_y'];
          data1['user'] = data6['user'];
          data1['created'] = data6['created'];
          data1['location'] = data6['location'];
          data1['tweet'] = data6['tweet'];
          
          data9['g_x'] = data14['g_x'];
          data9['g_y'] = data14['g_y'];
          data9['name'] = data14['name'];
          data9['count'] = data14['count'];
          data9['bins'] = data14['bins'];
        }
        
        if (f == %s) {
          for (var e in data1) delete data1[e];
          for (var g in data9) delete data9[g];
          
          data1['s_x'] = data7['s_x'];
          data1['s_y'] = data7['s_y'];
          data1['user'] = data7['user'];
          data1['created'] = data7['created'];
          data1['location'] = data7['location'];
          data1['tweet'] = data7['tweet'];
          
          data9['g_x'] = data15['g_x'];
          data9['g_y'] = data15['g_y'];
          data9['name'] = data15['name'];
          data9['count'] = data15['count'];
          data9['bins'] = data15['bins'];
        }
        
        if (f == %s) {
          for (var e in data1) delete data1[e];
          for (var g in data9) delete data9[g];
          
          data1['s_x'] = data8['s_x'];
          data1['s_y'] = data8['s_y'];
          data1['user'] = data8['user'];
          data1['created'] = data8['created'];
          data1['location'] = data8['location'];
          data1['tweet'] = data8['tweet'];
          
          data9['g_x'] = data16['g_x'];
          data9['g_y'] = data16['g_y'];
          data9['name'] = data16['name'];
          data9['count'] = data16['count'];
          data9['bins'] = data16['bins'];
        }
            
        source1.change.emit();
        source9.change.emit();
    """ % (selection_dates_js[0], 
            selection_dates_js[1], 
            selection_dates_js[2],
            selection_dates_js[3],
            selection_dates_js[4],
            selection_dates_js[5],
            selection_dates_js[6]))

    select = Select(title='Choose date from timeline:',
                    value=selection_dates[0],
                    options=selection_dates,
                    sizing_mode="stretch_width")
    
    select.js_on_change('value', callback)
    
    color_bar = ColorBar(color_mapper=mapper,
                         label_standoff = 10,
                         width=12,
                         major_label_text_font_size='14px',
                         major_label_text_font = font,
                         location=(0,0))
    s_p.add_layout(color_bar, 'right')
      
    # fixed widgets column contains select dropdown menu
    dropdown = column(select, sizing_mode="fixed", height=50, width=800)
    # placeholder div containers
    
    ph_fig_sep = Div(text="", height=50, width=20)
    ph_widget_sep = Div(text="", height=20, width=500)
    # create whisker sentiment plots for polarity and subjectivity
    from whisker_plot import whisker_sentiment, whisker_city_count
    w_pol = whisker_sentiment(df, 'polarity')
    w_sub = whisker_sentiment(df, 'subjectivity')
    w_count = whisker_city_count(df, selection_day_range)
    
    # assembling layout together
    
    layout = column(row(ph_fig_sep, ph_fig_sep, dropdown),
                    row(ph_widget_sep),
                    row(s_p, ph_fig_sep, g_p),
                    row(ph_widget_sep),
                    row(w_pol, ph_fig_sep, w_sub), 
                    row(ph_widget_sep),
                    row(w_count),
                    row(ph_widget_sep),
                    sizing_mode="stretch_both")
    
    # calling create_html_template function to assemble bokeh plots into
    # custom styled html/css templates    
    html = create_html_template(layout)
    filename = 'index.html'
    
    # generate output file as html
    with open((os.path.join(docs_dir, filename)), "w", encoding="utf-8") as f:
        f.write(html)
        
    view(filename)