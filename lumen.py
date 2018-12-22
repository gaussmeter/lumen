from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import time
import threading
import logging
import queue
import json

logging.basicConfig(
  level=logging.DEBUG,
  format='(%(threadName)-10s) %(message)s',
)

logging.debug(os.uname())

if os.uname()[4] != "x86_64":
  import board
  import neopixel

hostPort = 9000

lumenCommand = { 'animation' : 'None' } 
num_pixels = 12
if os.uname()[4] != "x86_64":
  pixel_pin = board.D18
  ORDER = neopixel.GRBW
  pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.2, auto_write=False,pixel_order=ORDER)

def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        r = g = b = 0
    elif pos < 85:
        r = int(pos * 3)
        g = int(255 - pos*3)
        b = 0
    elif pos < 170:
        pos -= 85
        r = int(255 - pos*3)
        g = 0
        b = int(pos*3)
    else:
        pos -= 170
        r = 0
        g = int(pos*3)
        b = int(255 - pos*3)
    return (r, g, b) if ORDER == neopixel.RGB or ORDER == neopixel.GRB else (r, g, b, 0)

def lumen(queue, event):
  global lumenCommand
  logging.debug('start lumen')
  while True:
    while not queue.empty():
      lumenCommand = queue.get()
      logging.debug(lumenCommand)
    if event.isSet():
      logging.debug('stop lumen')
      return
    time.sleep(.01)
    #rainbow
    if os.uname()[4] != "x86_64":
      if lumenCommand['animation'] == "rainbow":
        for j in range(255):
          for i in range(num_pixels):
            pixel_index = (i * 255 // num_pixels) + j
            pixels[i] = wheel(pixel_index & 255)
          pixels.show()
      #fill
      if lumenCommand['animation'] == "fill":
        pixels.fill((lumenCommand['r'],lumenCommand['g'],lumenCommand['b'],lumenCommand['w']))
        pixels.show()


class MyServer(BaseHTTPRequestHandler):
  def do_GET(self):
    global lumenCommand
    if self.path == "/lumen": 
      self.send_response(200)
      self.send_header("Content-type", "json")
      self.end_headers()
      self.wfile.write(bytes(json.dumps(lumenCommand), "utf-8"))
    else:
      self.send_response(302)
      self.send_header("Location", "/lumen")
      self.end_headers()

  def do_PUT(self):
    if self.path == "/lumen":
      length = self.headers['Content-Length']
      lumenCommand = parseCommand(self.rfile.read(int(length)).decode("utf-8")) 
      if lumenCommand != None:
        self.send_response(200)
        self.send_header("Content-type", "json")
        self.end_headers()
        self.wfile.write(bytes('{"response":"ok"}', "utf-8"))
        lumenQueue.put(lumenCommand)
      else:
        self.send_response(400)
        self.send_header("Content-type", "json")
        self.end_headers()
        self.wfile.write(bytes('{"response":"fail"}', "utf-8"))
    else:
      self.send_response(404)
      self.end_headers()

def parseCommand(payload):
  command = {}
  try:
    command = json.loads(payload)
  except:
    return None
  command['animation'] = command.get('animation', 'fill')
  command['r'] = command.get('r', 0)
  command['g'] = command.get('g', 0)
  command['b'] = command.get('b', 0)
  command['w'] = command.get('w', 0)
  return command

myServer = HTTPServer(('', hostPort), MyServer)
print(time.asctime(), "Server Starts - *:%s" % (hostPort))

lumenQueue = queue.Queue()
lumenQueue.put(lumenCommand)
lumenQuit = threading.Event()

lumenThread = threading.Thread(
  name = 'lumen',
  target = lumen,
  args = (lumenQueue,lumenQuit,),
)
lumenThread.start()



try:
  myServer.serve_forever()
except KeyboardInterrupt:
  pass

lumenQuit.set()
myServer.server_close()
print(time.asctime(), "Server Stops - *:%s" % (hostPort))

