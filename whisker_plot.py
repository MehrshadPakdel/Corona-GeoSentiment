# -*- coding: utf-8 -*-
"""
Created on Tue May 19 16:28:00 2020

@author: mehrs
"""
import pandas as pd

from bokeh.models import ColumnDataSource, Whisker, FuncTickFormatter, Dash
from bokeh.plotting import figure

# import in function to avoid circular dependency
from data_visualization import create_city_count_dataframe
from data_visualization import max_log_city_count_per_day
from data_visualization import font
from data_visualization import text_color
from data_visualization import font_style
from data_visualization import title_font_size
from data_visualization import axis_label_font_size

def create_tick_date_dict(df):
    # create custom date x axis ticks by using FuncTickFormatter
    # get da pd series of unique dates and convert them to list
    df.loc[:,'date_created'] = pd.to_datetime(df.loc[:,'date_created']).copy()
    df.loc[:,'date_created'] = df.loc[:,'date_created'].dt.strftime("%d.%m").copy()
    date_range = df.loc[:,'date_created'].drop_duplicates().to_list()
    
    # create a dict with key dates and values day number of this series
    # assigned to it
    day_range_list = [x+1 for x in range(len(date_range))]
    date_tick_dict = dict(zip(day_range_list, date_range))
    
    return date_tick_dict

def whisker_sentiment(df, calc_attr):
    # filters for not negative values to better analyze the mean trends 
    df = df[df[calc_attr] != 0]
    df = df.sort_values(by=['day_range']).copy()

    calc_attr_capitalized = calc_attr.capitalize()
    # create figure
    p = figure(plot_width=400,
               plot_height=350,
               y_axis_label=calc_attr_capitalized)
    
    base, lower, upper, mean = [], [], [], []
    
    for i, date in enumerate(list(df.day_range.unique())):
        day_pol = df[df['day_range'] == date][calc_attr]
        pol_mean = day_pol.mean()
        pol_std = day_pol.std()
        lower.append(pol_mean - pol_std)
        upper.append(pol_mean + pol_std)
        base.append(date)
        mean.append(pol_mean)

    source_error = ColumnDataSource(data={'base':base,
                                          'lower':lower, 
                                          'upper':upper})
    source_mean = ColumnDataSource(data={'x':base,
                                          'y':mean})
    # plot scatter plots for each time point in series
    for i, date in enumerate(list(df.day_range.unique())):
        y = df[df['day_range'] == date][calc_attr]
        p.circle(x=date, y=y, color='teal', size=3, alpha=0.1)
        
    p.add_layout(
        Whisker(source=source_error,
                base="base",
                upper="upper",
                lower="lower",
                line_color='pink',
                line_width=5))
                
    
    dash = Dash(x="x", y="y", size=10, line_color="black", line_width=1, fill_color=None)
    p.add_glyph(source_mean, dash)
    # call create tick date dict function to convert a list of day sequence of
    # the data series to a dict containing keys as list of days and values
    # the according dates. This dict format is required for FuncTickFormatter
    # JS code to change the x labels to according dates 
    date_tick_dict = create_tick_date_dict(df)
    p.xaxis.formatter = FuncTickFormatter(code="""
    var mapping = %s;
    return mapping[tick];
    """ % date_tick_dict)
    
    # configure visual properties on a plot's title attribute    
    p.title.text = f"Mean {calc_attr_capitalized} Over Time"
    p.title.align = "center"
    p.title.text_color = text_color
    p.title.text_font_size = title_font_size
    p.title.text_font = font
    p.title.text_font_style = font_style
    
    # configure axis labels
    p.axis.axis_label_text_font_style = font_style
    p.axis.axis_label_text_font_size = axis_label_font_size
    p.axis.axis_label_text_font = font
    p.axis.axis_label_text_color = text_color
    p.axis.major_label_text_font_size = '10pt'
    p.axis.major_label_text_font = font
    p.axis.major_label_text_color = text_color
    
    p.axis.axis_line_color = text_color
    
    # turning off minor labels
    p.xaxis.minor_tick_line_color = None
    p.yaxis.minor_tick_line_color = None
    return p

def whisker_city_count(df, selection_day_range):
    
    p = figure(plot_width=820,
               plot_height=350,
               y_axis_label='Count')
    
    # not required for this function itself but for the
    # create_city_count_dataframe function as an argument. Requires kwargs 
    # adjustments of this function
    log_city_max_day, log_city_max_full_dataset = max_log_city_count_per_day(df, selection_day_range)
    
    # sort df first by day_range for correct order for subsequent iteration
    df = df.sort_values(by=['day_range'])
    
    # iterate over days in the dataset data frame and sum total city counts
    # for line plot
    city_counts = []
    dates = []
    for i, date in enumerate(list(df.day_range.unique())):
        df_day = df[df['day_range'] == date]
        df_cities = create_city_count_dataframe(df_day, log_city_max_day)
        count = df_cities.loc[:, 'tweet_count'].sum()
        city_counts.append(count)
        dates.append(date)
        
    
    # call create tick date dict function to convert a list of day sequence of
    # the data series to a dict containing keys as list of days and values
    # the according dates. This dict format is required for FuncTickFormatter
    # JS code to change the x labels to according dates 
    date_tick_dict = create_tick_date_dict(df)
    p.xaxis.formatter = FuncTickFormatter(code="""
    var mapping = %s;
    return mapping[tick];
    """ % date_tick_dict)
    
    # configure visual properties on a plot's title attribute    
    p.title.text = 'Tweet Count Over Time'
    p.title.align = "center"
    p.title.text_color = text_color
    p.title.text_font_size = title_font_size
    p.title.text_font = font
    p.title.text_font_style = font_style
    
    # configure axis labels
    p.axis.axis_label_text_font_style = font_style
    p.axis.axis_label_text_font_size = axis_label_font_size
    p.axis.axis_label_text_font = font
    p.axis.axis_label_text_color = text_color
    p.axis.major_label_text_font_size = '10pt'
    p.axis.major_label_text_font = font
    p.axis.major_label_text_color = text_color
    
    p.axis.axis_line_color = text_color
    
    # turning off minor labels
    p.xaxis.minor_tick_line_color = None
    p.yaxis.minor_tick_line_color = None
        
    # create line and circle glyphs for individual data points
    p.line(dates, city_counts, line_width=4, line_color="teal", alpha=0.6)
    p.circle(dates, city_counts, fill_color="pink", line_color="white", size=12, alpha=0.8)
    
    return p
    #output_file("whisker_count.html", title="Sum city counts")
    #show(p)
