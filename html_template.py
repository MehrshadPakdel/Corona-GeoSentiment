from jinja2 import Template
from bokeh.embed import components
from bokeh.resources import INLINE, CDN

def create_html_template(layout):
    
    # bokeh components required to embed the input bokeh layout into a html
    # template using e.g. Jinja2
    s_script, s_div = components(layout)
    
    template = Template('''
    <head>
        <meta charset="utf-8">
        <title>Sentiment Analysis Corona-Crisis | Mehrshad Pakdel</title>
        {{ js_resources|safe }}
        {{ css_resources|safe }}
        {{ js_CDN_resources|safe }}
        {{ css_CDN_resources|safe }}
        {{ s_script|safe }}
        
        <style type="text/css">
            .container {
            width: 60%;
            margin-left: auto;
            margin-right: auto;
            }
            h1 {
            font-family:helvetica,verdana;
            color:#737373;
            font-size: 30px;
            font-weight: normal;
            text-transform: uppercase;
            margin-top: 1.5em;
            }
            
            h2  {
            font-family:helvetica,verdana;
            color:#ff8096;
            font-size: 20px;
            font-weight: normal;
            }
           
            p {
            font-family:helvetica,verdana;
            color:#737373;
            font-size: 16px;
            text-align: justify;
            text-justify: inter-word;
            }
            
            ul {
            font-family:helvetica,verdana;
            color:#737373;
            font-size: 16px; 
            }
            
            a {
            font-family:helvetica,verdana;
            color:teal;
            text-decoration: none; 
            font-size: 16px; 
            }
            .centerimg {
              display: block;
              margin-left: auto;
              margin-right: auto;
              width: 50%;
            }
            .centerdiv {
            margin: 0 auto;
            width: 90%;
            }
        </style>
    </head>
    <body>
        <div class="container">
        
            <h1>Twitter Geo-Sentiment Analysis<br>During Corona Crisis</h1>
            
            <h2>The Idea</h2>
            
            <p>Sentiment analysis of social media data is a powerful tool. I came 
            up with this idea to analyze twitter data using corona keywords.
            This analysis allows to create temporal and spatial snapshots of 
            the public opinion regarding topics related to the Corona-Crisis 
            such as social distancing, curfews or healthcare occupancy.
            To limit the number of languages for the sentiment analysis, I 
            first started out to analyze tweets captured in Germany.</p> 
            
            <h2>Workflow</h2>
            
            <ul>
                <li>Retrieve Corona-related tweets by using the Twitter's standard API and the <a href="http://docs.tweepy.org/en/latest/" target="_blank">Tweepy</a> library for Python</li>
                <li>Collect tweet data and save them to a SQLite database using <a href="https://docs.python.org/3/library/sqlite3.html" target="_blank">sqlite3</a></li>
                <li>Tweet text processing and sentiment analysis using <a href="https://textblob.readthedocs.io/en/dev/" target="_blank">TextBlob</a> for english and german languages</li>
                <li>Mapping user locations to geographic coordinates and creating map of germany using <a href="https://geopandas.org/" target="_blank">geopandas</a> and <a href="https://docs.bokeh.org/en/latest/" target="_blank">bokeh</a></li>
                <li>Creating interactive graphs with <a href="https://docs.bokeh.org/en/latest/" target="_blank">bokeh</a></li>
                <li>Bringing everything together and create customized html templates using <a href="https://palletsprojects.com/p/jinja/" target="_blank">Jinja2</a></li>
                <li>Have a look at the source code in the <a href="https://github.com/MehrshadPakdel/Corona-GeoSentiment" target="_blank">GitHub repository</a></li>
            </ul>
            
        <h2>The Data</h2>
        
        <div class="centerdiv">
        
            {{ s_div|safe }}
            
        </div>

        <h2>Wrap-up</h2>
        
        <p>Sentiment analysis of tweets related to the Corona-Crisis 
        revealed some interesting insights of public's opinion. We can
        visualize differences in the public's sentiment, the tweet locations
        and their quantity over time. Fluctuations in both polarity and 
        subjectivity of the tweet are observed over time. The mean 
        polarity seems to be slightly positive which might be surprising 
        considering the nature of social media. Interestingly, on 24.05.
        there is a slight trend towards a negative polarity visible.
        However, the sensitivity of this type of sentiment
        analysis is limited and probably requires more advanced natural 
        language processing approaches.</p>
        
        <h2>About</h2>
    
        <img src="./img/img.jpg" alt="Profile Picture" style="width:125px;height:125px;" class="centerimg">
        
        <p style="text-align:center;color:teal">Mehrshad Pakdel</p>
        
        <p  style="margin-bottom: 4em;">Hey there! After my PhD in biochemistry and first
        professional experience as a Consultant for Data Analytics, I am
        thrilled about data science and coding. As an aspiring data
        scientist, I am excited to learn new Python techniques and 
        frameworks. If you have questions about this project, please 
        don't hesitate to contact me via <a href="https://www.linkedin.com/in/mehrshad-pakdel/" target="_blank">LinkedIn</a>.</p>
        <br>
        <p style="text-align:center;"><a href="./notice.html" target="_blank" style="font-size: 14px;color:#737373;margin-bottom: 4em;">Legal Notice</a></p>
    </div>
    </body>''')
    
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()
    js_CDN_resources = CDN.render_js() 
    css_CDN_resources = CDN.render_css()

    html = template.render(js_resources=js_resources,
                       css_resources=css_resources,
                       js_CDN_resources=js_CDN_resources,
                       css_CDN_resources=css_CDN_resources,
                       s_script=s_script,
                       s_div=s_div)
    
    return html