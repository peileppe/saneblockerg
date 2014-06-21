#!/usr/bin/env python

"""
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
For a copy of the license see http://www.gnu.org

=====================================================================
author : peileppeproduction@gmail.com
www.peileppe.com

SaneBlockerG.py
https://code.google.com/p/saneblockerg/

"""

import pygame, os.path 

DIM = 40
TILES_SIZE =16
COLS, LINES = DIM*TILES_SIZE,DIM*TILES_SIZE #640 pixels
SCREENRECT = pygame.Rect(0, 0, COLS, LINES)
TEXTCOLOR = (128,128,128)
FPS = 15
list_balls = []
list_blocks = []
BLOCKED=0
class Img: pass

# key references 
KEY_UP = 273
KEY_DOWN =274
KEY_RIGHT =275
KEY_LEFT =276
K_ESCAPE = pygame.K_ESCAPE
K_q = pygame.K_q
QUIT = pygame.QUIT

main_dir = os.path.split(os.path.abspath(__file__))[0]  # Program's diretory

def load_image(file, transparent):
    "loads an image, prepares it for play"
    file = os.path.join(main_dir, 'data', file)
    try:
        surface = pygame.image.load(file)
    except pygame.error:
        raise SystemExit('Could not load image "%s" %s' %
                         (file, pygame.get_error()))
    if transparent:
        corner = surface.get_at((0, 0))
        surface.set_colorkey(corner, pygame.RLEACCEL)
    return surface.convert()

def display_text(screen, background, x, y, msg):
    instSurf = BASICFONT.render(msg, True, TEXTCOLOR)
    instRect = instSurf.get_rect()
    instRect.x, instRect.y = x, y
    screen.blit(background, instRect, instRect)    
    screen.blit(instSurf, instRect)
    return 


# ==> Block 
class Block:

    def __init__(self, image, x, y, destructible=True):
        self.image = image
        self.rect = image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.dir_vertical, self.dir_horizontal =+TILES_SIZE, +TILES_SIZE
        self.destructible=destructible
        self.ignored=False

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        return

    def erase(self, screen, background):
        screen.blit(background, self.rect, self.rect)
        return
        

# ==> Ball
class Ball(Block):

    def update(self, screen, background, objectlist):
        global BLOCKED
        """
        Check if next move will be a collision 
        if so cancel the move and go in another direction
        return the collision indice - so the destructible block could be removed from the list        
        """
        if self.ignored: # no collision the ball is now ignored 
            return -1
        self.erase(screen, background)            
        objectrects = []
        for o in objectlist: # create a list of all the object to check position with 
            objectrects.append(o.rect)
        new=Ball(Img.ball, self.rect.x, self.rect.y) # will work on a copy of self
        new.dir_vertical, new.dir_horizontal = self.dir_vertical, self.dir_horizontal # assign correct dir
        new.rect.y=self.rect.y+new.dir_vertical
        new.rect.x=self.rect.x+new.dir_horizontal
        collision_initial=new.rect.collidelist(objectrects)
        collision=collision_initial
        sane=0
        while collision!=-1: # looking in all directions until no collision are found
            if  sane==0: 
                new.dir_vertical=-new.dir_vertical # test original horizontal direction but vertical opposite
            elif sane==1:
                new.dir_horizontal=-new.dir_horizontal # test vertical opposite and horizontal opposite
            elif sane==2:
                new.dir_vertical=-new.dir_vertical # test horizontal opposite and vertical original direction 
            new.rect.y=self.rect.y+new.dir_vertical
            new.rect.x=self.rect.x+new.dir_horizontal
            collision=new.rect.collidelist(objectrects)
            sane+=1
            if sane==3:
                self.ignored=True # it doesn't move so ignore it            
                BLOCKED+=1                
                display_text(screen, background, 0, LINES-TILES_SIZE, "Blocked=[%s]" % BLOCKED)
                break
        self.dir_vertical, self.dir_horizontal = new.dir_vertical, new.dir_horizontal 
        self.rect.y+=self.dir_vertical
        self.rect.x+=self.dir_horizontal
        self.draw(screen)
        return collision_initial

# ==> Player / Avatar
class Player(Block):

    def update(self, action, screen, background, objectlist):
        """  player update 
        """ 
        if action == None: 
            return False
        self.erase(screen, background)                    
        tmp=Player(self.image, self.rect.x, self.rect.y) 
        if action==K_ESCAPE or action==K_q:
            return True #  stop the game
        elif action==KEY_UP and tmp.rect.y  > TILES_SIZE:
            tmp.rect.y -= self.dir_vertical
        elif action==KEY_DOWN and tmp.rect.y  < LINES-(TILES_SIZE*2):
            tmp.rect.y += self.dir_vertical
        elif action==KEY_RIGHT and tmp.rect.x < COLS-(TILES_SIZE*2):
            tmp.rect.x += self.dir_horizontal
        elif action==KEY_LEFT and tmp.rect.x > TILES_SIZE:
            tmp.rect.x -= self.dir_horizontal
        elif action==pygame.K_SPACE:
            self.depose(screen, background)
        elif action==pygame.K_r: # redraw
            for b2 in list_blocks:
                if b2.destructible:
                    b2.draw(screen)
        " There's a move then we check for collision "
        if tmp.rect.x != self.rect.x or tmp.rect.y!= self.rect.y:
            objectrects = []        
            for b3 in objectlist:
                objectrects.append(b3.rect)
            collision=self.rect.collidelist(objectrects)
            if collision!=-1: # a block is under 
                damagedblock=list_blocks[collision]
                damagedblock.erase(screen, background) # erase the sprite
                list_blocks.remove(damagedblock) # update the list
        self.rect.x, self.rect.y = tmp.rect.x, tmp.rect.y # actualizing the coordinates
        self.draw(screen)                    
        return False

    def depose(self, screen, background): 
        """ if space bar - will create block next to the avatar (on his right side) unless it's off-limit
        """
        if self.rect.x<COLS-(TILES_SIZE*2): 
            objectrects = []        
            for b3 in list_blocks:
                objectrects.append(b3.rect)
            tmp=Player(self.image, self.rect.x, self.rect.y) # will work on a copy of self
            tmp.rect.x+=TILES_SIZE
            collision=tmp.rect.collidelist(objectrects)
            if collision==-1:
                b1=Block(Img.SBlock, tmp.rect.x, tmp.rect.y, False) #  False means block are indestructible
                b1.draw(screen)
                list_blocks.append(b1)
        return
        
# ==> Main Loop        
def main():
    global BASICFONT
    pygame.init()
    screen = pygame.display.set_mode(SCREENRECT.size, 0)
    pygame.display.set_caption('Sane-BlockerG')    
    BASICFONT = pygame.font.Font('freesansbold.ttf', TILES_SIZE)
    clock = pygame.time.Clock()
    # Load the Images
    Img.background = load_image('backgroundh1.png', 0)
    Img.block = load_image('block.png', 0)
    Img.SBlock = load_image('block1.png', 0)
    Img.ball = load_image('ball.png', 1)
    Img.avatr= load_image('avatr.png',1)
    # display background    
    background = pygame.Surface(SCREENRECT.size)
    background.blit(Img.background, (0,0))
    screen.blit(background, (0,0))
    # create list of balls
    list_balls.append(Ball(Img.ball, TILES_SIZE*3, TILES_SIZE*3))
    list_balls.append(Ball(Img.ball, TILES_SIZE*6, TILES_SIZE*3))
    list_balls.append(Ball(Img.ball, TILES_SIZE*6, TILES_SIZE*5))
    list_balls.append(Ball(Img.ball, TILES_SIZE*6, TILES_SIZE*6))
    list_balls.append(Ball(Img.ball, TILES_SIZE*6, TILES_SIZE*7))
    list_balls.append(Ball(Img.ball, COLS-(TILES_SIZE*4),LINES-(TILES_SIZE*3)))
    # create list of blocks in the middle
    for x in range(TILES_SIZE*10, TILES_SIZE*30, TILES_SIZE*2): # TILES_SIZE*10, TILES_SIZE*30, TILES_SIZE*2
        list_blocks.append(Block(Img.block, x, TILES_SIZE*15))
        list_blocks.append(Block(Img.block, x, TILES_SIZE*17))
        list_blocks.append(Block(Img.block, x, TILES_SIZE*19))        
        list_blocks.append(Block(Img.block, x, TILES_SIZE*21))
        list_blocks.append(Block(Img.block, TILES_SIZE*4, x))
        list_blocks.append(Block(Img.block, COLS-(TILES_SIZE*5), x))        
    for x in range(0,40): # borders around the area
        list_blocks.append(Block(Img.SBlock, x*16, 0, False)) # top line 
        list_blocks.append(Block(Img.SBlock, x*16, 39*TILES_SIZE, False)) # lower line
    for y in range(1,39): # borders around the area
        list_blocks.append(Block(Img.SBlock, 0, y*16, False)) # vertical left 
        list_blocks.append(Block(Img.SBlock, 39*TILES_SIZE, y*16, False)) # vertical right
    for b in list_blocks:
        b.draw(screen)
    avatr=Player(Img.avatr, TILES_SIZE*4, LINES-(TILES_SIZE*4))
    avatr.draw(screen)
    pygame.display.flip()
    exitSignal = False
    # Main loop
    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exitSignal=True
            elif event.type == pygame.KEYDOWN: 
                action = event.key
                exitSignal=avatr.update(action, screen, background, list_blocks)                
            elif event.type == pygame.KEYUP:
                action = None
        if exitSignal: 
            pygame.quit()
            break
        for b1 in list_balls:
            collision=b1.update(screen, background, list_blocks+[avatr])
            if collision!=-1 and collision <len(list_blocks) : 
                damagedblock=list_blocks[collision]
                if damagedblock.destructible: # if undestructible we do nothing
                    damagedblock.erase(screen, background) 
                    list_blocks.remove(damagedblock) # update the list
        pygame.display.update()
    
if __name__ == '__main__':
    main()
    
