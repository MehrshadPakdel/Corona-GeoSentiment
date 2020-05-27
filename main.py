from data_loader import load_tweets_from_db

from data_processing import add_coordinates_to_location
from data_processing import sentiment_analysis
from data_processing import filter_day_range

from data_visualization import create_sentiment_data_source
from data_visualization import create_geo_data_source
from data_visualization import create_bokeh_plot

if __name__ == '__main__':
    df = load_tweets_from_db()
    
    df = add_coordinates_to_location(df)
    
    df = sentiment_analysis(df)

    df, selection_day_range, selection_dates = filter_day_range(df)
    
    s_source_dummy, s_source_full, s_sources = create_sentiment_data_source(df, selection_day_range)
    
    g_source_dummy, g_source_full, g_sources = create_geo_data_source(df, selection_day_range)
    
    create_bokeh_plot(df,
                      s_source_dummy,
                      s_source_full,
                      s_sources,
                      g_source_dummy,
                      g_source_full,
                      g_sources,
                      selection_dates,
                      selection_day_range)
    
    