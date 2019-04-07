from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import time
import threading
import logging
import queue
import json

if os.environ.get('SKIP_PIXELS') == None:
  import board
  import neopixel

hostPort = 9000

#lumenCommand = { 'animation' : 'None' }

num_pixels = 12
if os.environ.get('SKIP_PIXELS') == None:
  pixel_pin = board.D18
  ORDER = neopixel.GRBW
  pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=1, auto_write=False,pixel_order=ORDER)

def apply_bright(color, brightness):
  outcolor = [0, 0, 0, 0]
  for i in range(len(color)):
    outcolor[i] = round(color[i] * (brightness / 255))
  return outcolor


def colorcycle(dist):
  if 0 <= dist % 768 <= 255:
    return (dist % 256, 0, 255 - dist % 256, 0)
  elif 256 <= dist % 768 <= 511:
    return (255 - dist % 256, dist % 256, 0, 0)
  elif 512 <= dist % 768 <= 767:
    return (0, 255 - dist % 256, dist % 256, 0)


logging.basicConfig(
  level=logging.DEBUG,
  format='(%(threadName)-10s) %(message)s',
)

def lumen(queue, event):
  global lumenCommand
  cycledistance = 0
  direction = 1
  logging.debug('start lumen')
  while True:
    start = time.time()
    if not queue.empty():
      lumenCommand = queue.get()
      logging.debug(lumenCommand)
      bright = lumenCommand['bright']
      color1 = apply_bright([lumenCommand['r'], lumenCommand['g'], lumenCommand['b'], lumenCommand['w']], bright)
      color2 = apply_bright([lumenCommand['r2'], lumenCommand['g2'], lumenCommand['b2'], lumenCommand['w2']], bright)
      velocity = lumenCommand['velocity']
      length = lumenCommand['length']
      distalong = 0
      #cylon
      pucklength = round(num_pixels * length / 100)
      #midward
      max_dist = round(num_pixels * length / 100)
      midcolor = [0, 0, 0, 0]
      for i in range(4):
        midcolor[i] = round((color1[i] + color2[i]) / 2)
    if event.isSet():
      logging.debug('stop lumen')
      return
    if os.environ.get('SKIP_PIXELS') == None:
      #bargraph
      if lumenCommand['animation'] == 'bargraph':
        distacross = num_pixels - round((100 - length) / 100 * num_pixels)
        for i in range(distacross, num_pixels):
          pixels[i] = color2
        for i in range(0, distacross):
          pixels[i] = color1
        pixels.show()
      #cylon
      if lumenCommand['animation'] == 'cylon':
        for i in range(distalong, distalong + pucklength):
          logging.debug(" i: " + i)
          pixels[i] = color1
        for i in range(0, distalong):
          pixels[i] = color2
        for i in range(distalong + pucklength, num_pixels):
          pixels[i] = color2
        if (distalong + pucklength + direction) > num_pixels or (distalong + direction) < 0:
          direction = direction * -1
        pixels.show()
        distalong = distalong + direction
      #rainbow
      if lumenCommand['animation'] == "rainbow":
        distacross = num_pixels - round((100 - length) / 100 * num_pixels)
        increment = 768 / distacross
        for i in range(distacross, num_pixels):
          pixels[i] = color2
        for i in range(0, distacross):
          pixels[i] = apply_bright(colorcycle(cycledistance + round(i * increment)), bright)
        pixels.show()
        cycledistance = round(cycledistance + velocity / 1.5)
        if cycledistance >= 768:
          cycledistance = cycledistance % 768
      #midward
      if lumenCommand['animation'] == "midward":
        if distalong == max_dist or distalong == 0:
          direction = direction * -1
        distalong = distalong + direction
        conjugate = num_pixels - round((num_pixels - max_dist) * (distalong / max_dist))
        print(distalong, ",", conjugate)
        if direction == 1:
          for i in range(0, distalong):
            pixels[i] = color1
          for i in range(conjugate, num_pixels):
            pixels[i] = color2
        if direction == -1:
          for i in range(distalong, max_dist):
            pixels[i] = color2
          for i in range(max_dist + 1, conjugate):
            pixels[i] = color1
        pixels[max_dist] = midcolor
      #fill
      if lumenCommand['animation'] == "fill":
        pixels.fill((lumenCommand['r'],lumenCommand['g'],lumenCommand['b'],lumenCommand['w']))
        pixels.show()
    while time.time() < (start + 2/velocity):
      time.sleep(.01)


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
  command['length'] = command.get('length', 100)
  percent = command.get('percent', None)
  if percent != None:
    command['length'] = percent
  command['bright'] = command.get('bright', 255)
  command['velocity'] = command.get('velocity', 100)
  command['r'] = int(command.get('r', 0))
  command['g'] = int(command.get('g', 0))
  command['b'] = int(command.get('b', 0))
  command['w'] = int(command.get('w', 0))
  rgbw = command.get('rgbw', None)
  if rgbw != None and len(rgbw.split(',')) == 4:
    command['r'] = int(rgbw.split(',')[0])
    command['g'] = int(rgbw.split(',')[1])
    command['b'] = int(rgbw.split(',')[2])
    command['w'] = int(rgbw.split(',')[3])
  command['r2'] = int(command.get('r2', 0))
  command['g2'] = int(command.get('g2', 0))
  command['b2'] = int(command.get('b2', 0))
  command['w2'] = int(command.get('w2', 0))
  rgbw2 = command.get('rgbw2', None)
  if rgbw2 != None and len(rgbw2.split(',')) == 4:
    command['r2'] = int(rgbw2.split(',')[0])
    command['g2'] = int(rgbw2.split(',')[1])
    command['b2'] = int(rgbw2.split(',')[2])
    command['w2'] = int(rgbw2.split(',')[3])
  return command

lumenCommand = parseCommand('{}')

myServer = HTTPServer(('', hostPort), MyServer)
logging.debug(time.asctime() + "Server Start - *:" + str(hostPort))
logging.debug(os.uname())
if os.environ.get('SKIP_PIXELS') != None:
  logging.debug("SKIP_PIXELS != None -- emulation mode...")


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

