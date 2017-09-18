import os
import sys
import time
import json
import threading
import tornado.ioloop
import tornado.web
import tornado.websocket

from basescript import BaseScript

PATH = os.path.dirname(__file__)
STATIC_DIR_PATH = os.path.join(PATH, 'static')

class EchoWebSocketHandler(tornado.websocket.WebSocketHandler):
    def initialize(self, wsocks):
        self.wsocks = wsocks

    def open(self):
        self.wsocks[id(self)] = self

        # Flush on write. Don't wait to optimize n/w usage.
        self.set_nodelay(True)

    def on_close(self):
        del self.wsocks[id(self)]

class EventCounter(object):
    def __init__(self):
        self.counts = {}

    def submit_event(self, evt, count=1):
        ts = int(time.time())
        ts_counts = self.counts.get(ts, {})
        ts_counts[evt] = ts_counts.get(evt, 0) + count
        self.counts[ts] = ts_counts

    def flush_counts(self):
        ts_counts = []
        ts = int(time.time())

        for _ts in sorted(self.counts.keys()):
            if _ts >= ts: continue
            ts_counts.append((_ts, self.counts.pop(_ts)))

        return ts_counts

class KwikStatsServer(BaseScript):
    DESC = 'Stats Visualization Server'
    DEFAULT_PORT = 8888

    def __init__(self, *args, **kwargs):
        super(KwikStatsServer, self).__init__(*args, **kwargs)

        self.app = None
        self.wsocks = None

        self.counts = EventCounter()

    def make_app(self):
        wsocks = {}
        app = tornado.web.Application([
            (r"/", tornado.web.RedirectHandler, {'url': '/index.html'}),
            (r"/ws", EchoWebSocketHandler, {'wsocks': wsocks}),
            (r'/(.*)', tornado.web.StaticFileHandler, {'path': STATIC_DIR_PATH}),
        ])
        app.wsocks = wsocks
        return app

    def handle_stdin(self):
        while 1:
            line = sys.stdin.readline()
            line = line[:-1]
            if ':' not in line:
                evt = line
                count = 1
            else:
                evt, count = line.split(':', 1)
                count = int(count)
                # FIXME: handle potential parsing error here

            self.counts.submit_event(evt, count)

    def flush_counts(self):
        while 1:
            ts_counts = self.counts.flush_counts()

            for ws in self.wsocks.itervalues():
                # TODO: handle error
                for ts_count in ts_counts:
                    self.log.debug('flushing counts', counts=ts_count)
                    sys.stdout.flush()
                    ws.write_message(json.dumps(ts_count))

            # TODO: don't hardcode
            time.sleep(.25)

    def run(self):
        self.app = app = self.make_app()
        self.wsocks = app.wsocks

        app.listen(self.args.port)

        startfn = tornado.ioloop.IOLoop.current().start
        th = threading.Thread(target=startfn)
        th.daemon = True
        th.start()

        flush_th = threading.Thread(target=self.flush_counts)
        flush_th.daemon = True
        flush_th.start()

        self.handle_stdin()

    def define_args(self, parser):
        parser.add_argument('-p', '--port', default=self.DEFAULT_PORT, type=int)

def main():
    KwikStatsServer().start()

if __name__ == "__main__":
    main()
