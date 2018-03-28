#!/usr/bin/env python
import os, pygame, math, time
from pygame.compat import xrange_


WIDTH=800
HEIGHT=600
ORIGIN_X = WIDTH / 2
ORIGIN_Y = HEIGHT / 2
RADIUS=200
NUM_NODES=6
INCR = 360 / NUM_NODES
BUCKET_WIDTH=64
BUCKET_HEIGHT=128
BG_RED   = 48
BG_GREEN = 144
BG_BLUE  = 199
ACTIVE = (153, 198, 142)
REPLICA = (128,0,0)

def show (image):
    screen = pygame.display.get_surface()
    screen.fill ((255, 255, 255))
    screen.blit (image, (0, 0))
    # initialize font; must be called after 'pygame.init()' to avoid 'Font not Initialized' error
    myfont = pygame.font.SysFont("monospace", 75)

    # render text
    label = myfont.render("Some text!", 1, (100,100,200))
    screen.blit(label, (100, 100))
    pygame.display.flip ()
    time.sleep(0.25)

    while 1:
        event = pygame.event.wait ()
        if event.type == pygame.QUIT:
            raise SystemExit


    event = pygame.event.poll ()
    if event.type == pygame.QUIT:
        raise SystemExit


def drawvBucket(pixels, state,x,y):
    pixels[x, y] = state
    pixels[x, y+1] = state
    pixels[x+1, y] = state
    pixels[x+1, y+1] = state


def drawNode(node,surface,pixels):
    angle  = (node * INCR) + 180
    centre_x = int(RADIUS*math.sin(math.radians(angle))) + ORIGIN_X
    centre_y =  int(RADIUS*math.cos(math.radians(angle))) + ORIGIN_Y
    x = centre_x - (BUCKET_WIDTH / 2)
    y = centre_y - (BUCKET_HEIGHT / 2)
    pygame.draw.rect(surface, (255, 204, 102), (x, y, BUCKET_WIDTH, BUCKET_HEIGHT))
    for vb in range(0,512):
        if vb > 255:
            state=ACTIVE
        else:
            state=REPLICA
        vb_x = x + ((4 * vb) % BUCKET_WIDTH)
        vb_y = y + ((4 * vb) / BUCKET_WIDTH) * 4
        drawvBucket(pixels,state,vb_x,vb_y)

def fillBackground(surface):
    # Create the PixelArray.
    ar = pygame.PixelArray (surface)
    # Do some easy gradient effect.
    for y in xrange_ (HEIGHT):
        r = 255 - ((255 - BG_RED) * y / HEIGHT)
        g = 255 - ((255 - BG_GREEN) * y / HEIGHT)
        b = 255 - ((255 - BG_BLUE) * y / HEIGHT)
        ar[:,y] = (r, g, b)
    del ar

def main():
    pygame.init ()

    pygame.display.set_mode ((WIDTH, HEIGHT))
    surface = pygame.Surface ((WIDTH, HEIGHT))

    pygame.display.flip ()

    fillBackground(surface)
    ar = pygame.PixelArray (surface)

    for i in range(0,NUM_NODES):
        # ar = pygame.PixelArray (surface)
        drawNode(i,surface,ar)
    del ar
    show (surface)



   
if __name__ == '__main__':
    main()

