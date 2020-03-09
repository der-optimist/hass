import appdaemon.plugins.hass.hassapi as hass

#
# React on new news in an rss feed
#
# Args: no args required
# 

class feed_news(hass.Hass):

    def initialize(self):
        self.listen_event(self.new_feed_entry, event = "feedreader")
        
    def new_feed_entry(self,event_name,data,kwargs):
        self.log("New feedreader entry:")
        self.log(data)
