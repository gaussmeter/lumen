from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import threading
import logging
import queue

hostName = "*"
hostPort = 9000

def lumen(queue):
  logging.debug('start lumen')
  while True:
    while not queue.empty():
      message = queue.get()
      logging.debug(message)
      if message == "stop":
        logging.debug('stop lumen')
        return

logging.basicConfig(
  level=logging.DEBUG,
  format='(%(threadName)-10s) %(message)s',
)

class MyServer(BaseHTTPRequestHandler):
  def do_GET(self):
    self.send_response(200)
    self.send_header("Content-type", "text/html")
    self.end_headers()
    self.wfile.write(bytes("ok %s" % self.path, "utf-8"))
    if self.path == "/rainbow":
      logging.debug('rainbow')
      lumenQueue.put("rainbow")
    if self.path == "/silon":
      logging.debug('silon')
      lumenQueue.put("silon")
    if self.path == "/off":
      logging.debug('off') 
      lumenQueue.put("off")

myServer = HTTPServer(('', hostPort), MyServer)
print(time.asctime(), "Server Starts - %s:%s" % (hostName, hostPort))

lumenQueue = queue.Queue()

lumenThread = threading.Thread(
  name = 'lumen',
  target = lumen,
  args = (lumenQueue,),
)
lumenThread.start()

try:
  myServer.serve_forever()
except KeyboardInterrupt:
  pass

lumenQueue.put("stop")
myServer.server_close()
print(time.asctime(), "Server Stops - %s:%s" % (hostName, hostPort))
