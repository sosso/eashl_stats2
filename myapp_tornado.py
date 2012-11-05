from dict2xml import dict2xml
from simplejson.decoder import JSONDecodeError
from tornado.ioloop import IOLoop
from tornado.options import define, options
from xml.sax.saxutils import escape
from youtube_tools import fetch_yt_link
import Scorecard
import Video
import dbutils
import json
import logging
import simplejson
import sys
import tornado.gen
import tornado.httpserver
import tornado.ioloop
import tornado.web

sys.path.append("/var/www/FEOYoutube/libs/")
define("port", default=8787, help="run on the given port", type=int)
define("debug", default=False, help="enable logging without supervisor", type=bool)
define("debug_level", default='info', help="debug level:  debug, info, warn, error, critical")
logger = logging.getLogger('Server')



class ScoreComputeHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        bind_id = self.get_argument('bind_id')
        logger.debug('Score compute request received: bind_id: %s', bind_id)
        Video.compute_scores(bind_id)
        dbutils.Session.remove()
        self.finish()

class ScorecardHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        bind_id = self.get_argument('bind_id')
        youtube_id = self.get_argument('youtube_id')
        try:
            scorecard = Scorecard.get_scorecard(bind_id=bind_id, youtube_id=youtube_id)
        except:
            dbutils.Session.rollback()
            scorecard = {}
        finally:
            response_format = self.get_argument('response_format', 'xml')
            logger.debug('Scorecard request received: bind_id: %s, youtube_id: %s, response_format: %s', bind_id, youtube_id, response_format)
            if response_format == 'json':
                self.content_type = 'application/json'
                self.write(json.dumps(scorecard))
            else:
                self.content_type = 'text/xml'
                self.write(dict2xml(scorecard))
        dbutils.Session.remove()
        self.finish()

class ListHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        bind_id = self.get_argument('bind_id')
        youtube_id = self.get_argument('youtube_id', '-1')
        response_format = self.get_argument('response_format', 'xml')
        time_watched = self.get_argument('time_watched', -1)
        limit = self.get_argument('limit', 50)

        logger.debug('List request received: bind_id: %s, youtube_id (just watched): %s, response_format: %s, time_watched:%s', bind_id, youtube_id, response_format, time_watched)

        try:
            if youtube_id != '-1' and youtube_id != 'Title':
                Video.mark_watched(bind_id=bind_id, youtube_id=youtube_id, time_watched=time_watched)
        except:
            dbutils.Session.rollback()
        try:
            container = Video.get_list(bind_id=bind_id, limit=int(limit))
        except:
            dbutils.Session.rollback()
            container = {}
        if response_format == 'json':
            self.content_type = 'application/json'
            self.write(json.dumps(container))
        else:
            self.content_type = 'text/xml'
            self.write(dict2xml(container))
        dbutils.Session.remove()
        self.finish()

class MarkWatchedHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        bind_id = self.get_argument('bind_id')
        youtube_id = self.get_argument('youtube_id', '-1')
        time_watched = self.get_argument('time_watched', -1)

        logger.info('Mark watch request received: bind_id: %s, youtube_id (just watched): %s, time_watched:%s', bind_id, youtube_id, time_watched)

        try:
            if youtube_id != '-1' and youtube_id != 'Title':
                Video.mark_watched(bind_id=bind_id, youtube_id=youtube_id, time_watched=time_watched)
        except:
            dbutils.Session.rollback()
        dbutils.Session.remove()
        self.finish()

class STBHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        bind_id = self.get_argument('bind_id')
        youtube_id = self.get_argument('youtube_id', '-1')
        time_watched = self.get_argument('time_watched', -1)
        logger.debug('Set-top box list request received: bind_id: %s, youtube_id: %s, time_watched: %s', bind_id, youtube_id, time_watched)

        try:
            if youtube_id != '-1' and youtube_id != 'Title':
                Video.mark_watched(bind_id=bind_id, youtube_id=youtube_id, time_watched=time_watched)
        except:
            dbutils.Session.rollback()

        try:
            container = Video.get_list(bind_id=bind_id, is_stb=True)
            playback_url = fetch_yt_link(container['nowplaying']['url'])
            playback_url = escape(playback_url + '&title=.mp4')
            container['nowplaying']['url'] = escape(container['nowplaying']['url'])
            container['nowplaying']['title'] = escape(container['nowplaying']['title'])
            container['nowplaying']['youtube_id'] = escape(container['nowplaying']['youtube_id'])
            container['nowplaying']['playback_url'] = playback_url
        except:
            dbutils.Session.rollback()
            container = []
        logger.info("timewatched: %s youtube_id:%s bind_id:%s", time_watched, youtube_id, bind_id)
#        self.content_type = 'text/xml' //HACK wtf why doesn't this work..?
        self._headers['Content-Type'] = "text/xml; charset=UTF-8"
        if container != []:
            self.write(dict2xml({'nowplaying':container['nowplaying']}))
        dbutils.Session.remove()
        self.finish()


#class ProfileHandler(tornado.web.RequestHandler):
#    @tornado.web.asynchronous
#    def get(self):
#        self.collector = Collector()
#        self.collector.start()
#        IOLoop.instance().add_timeout(datetime.timedelta(seconds=60),
#                                      self.finish_profile)
#    def finish_profile(self):
#        self.collector.stop()
#        self.finish(repr(dict(self.collector.stack_counts)))

class HelloHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
#        bind_id = self.get_argument('bind_id')
#        Video.import_urls(bind_id)
#        Video.import_all_videos()
        self.write('Hello')
        dbutils.Session.remove()
        self.finish()

class InsertLikesHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        bind_id = self.get_argument('bind_id')
        logger.debug('Insert likes request received: bind_id: %s', bind_id)
        Video.insert_fb_likes(bind_id)
        dbutils.Session.remove()
        self.finish()

class AddHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        bind_id = self.get_argument('bind_id')
        youtube_id = self.get_argument('youtube_id')
        logger.debug('Single video add request received: bind_id: %s, youtube_id: %s', bind_id, youtube_id)
        video = Video.youtube_metadata_grabber(youtube_id)
        Video.insert_video(bind_id=bind_id, video=video)
        dbutils.Session.remove()
        self.finish()

    def post(self):
        youtube_ids = self.get_argument('youtube_ids', [])
        try:
            youtube_ids = json.loads(youtube_ids)
            logger.debug('Video bulk insert (post) request received: youtube_ids: %s', simplejson.dumps(youtube_ids))
        except JSONDecodeError:
            self.write("ERROR INVALID JSON")
            logger.error('Invalid youtube id array json')
            youtube_ids = []
        self.write('Received ' + str(len(youtube_ids)) + ' guids')
        logger.info('Received %d youtube guids for insert', len(youtube_ids))
        Video.import_youtube_videos(youtube_ids)
        logger.info("Import from youtube scrape complete, finishing response")
        self.finish()

class NukeUserHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        bind_id = self.get_argument('bind_id')
        logger.debug('Nuke request received: bind_id: %s', bind_id)
        Video.nuke_user_videos(bind_id)
        dbutils.Session.remove()
        self.finish()

if __name__ == "__main__":
    dbutils.Base.metadata.create_all(dbutils.engine)
    tornado.options.parse_command_line()
    if options.debug_level == 'debug':
        logging.getLogger('Server').setLevel(logging.DEBUG)
    elif options.debug_level == 'info':
        logging.getLogger('Server').setLevel(logging.INFO)
    elif options.debug_level == 'warn':
        logging.getLogger('Server').setLevel(logging.WARN)
    elif options.debug_level == 'error':
        logging.getLogger('Server').setLevel(logging.ERROR)
    elif options.debug_level == 'critical':
        logging.getLogger('Server').setLevel(logging.CRITICAL)
    LOG_FILENAME = 'logging_' + str(options.port) + '.out'

    if options.debug:
        logging.basicConfig()
        logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG)
        logger.info('debug flag set, logging to ' + LOG_FILENAME)
        handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=(209715200 / 2), backupCount=10) #100MB file size limit
        logger.addHandler(handler)
    else:
        logger.info('debug flag not set, logging according to supervisor\'s instructions')
    app = tornado.web.Application(handlers=[(r"/scores/compute/", ScoreComputeHandler), \
                                            (r"/scores/scorecard/", ScorecardHandler), \
                                            (r"/list/", ListHandler), \
                                            (r"/hello/", HelloHandler), \
                                            (r"/video/insertfblikes/", InsertLikesHandler), \
                                            (r"/video/add/", AddHandler), \
                                            (r"/video/markwatched/", MarkWatchedHandler), \
                                            (r"/list/nuke/", NukeUserHandler), \
                                            (r"/list/stb/", STBHandler)])
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    logger.info("Server started")
    tornado.ioloop.IOLoop.instance().start()

