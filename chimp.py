import os
os.environ['PYSDL2_DLL_PATH'] = os.path.dirname(__file__)

import sys
import sdl2
import sdl2.ext
from sdl2.ext.compat import *
from ctypes import c_uint32, c_int, byref

SDL_PRESSED = 1


def load_texture(renderer, name, colorkey=None):
    fullname = os.path.join('data', name)
    fullname = byteify(fullname, 'utf-8')
    surface = sdl2.SDL_LoadBMP(fullname)
    texture = sdl2.SDL_CreateTextureFromSurface(renderer, surface)
    flags = c_uint32()
    access = c_int()
    w = c_int()
    h = c_int()
    sdl2.SDL_QueryTexture(texture, byref(flags), byref(access),
                          byref(w), byref(h))
    rect = sdl2.SDL_Rect(0, 0, w, h)
    sdl2.SDL_FreeSurface(surface)
    return texture, rect


class Sprite:
    """ Simple Sprite
    """
    def __init__(self):
        self.texture = None
        self.rotation = 0
        self.flip = 0

    def __del__(self):
        if self.texture is not None:
            sdl2.SDL_DestroyTexture(self.texture)
        self.texture = None

    def update(self, td):
        pass


class Fist(Sprite):
    """moves a clenched fist on the screen, following the mouse
    """

    def __init__(self, renderer):
        super(Fist, self).__init__()
        self.renderer = renderer
        self.texture, self.rect = load_texture(renderer, 'fist.bmp')
        self.punching = False

    def move(self, pos):
        """Move the fist

        :param pos: x, y tuple of window coordinates
        :return: None
        """
        self.rect = sdl2.SDL_Rect(pos[0], pos[1], self.rect.w, self.rect.h)

    def set_punch(self, state):
        """returns true if the fist collides with the target"

        :param state: to punch or not to punch?
        :return: None
        """
        self.punching = bool(state)


class Chimp(Sprite):
    """moves a monkey critter across the screen. it can spin the monkey when it
    is punched.
    """
    move_speed = .25
    turn_speed = .25

    def __init__(self, renderer):
        super(Chimp, self).__init__()
        self.renderer = renderer
        self.texture, self.rect = load_texture(renderer, 'chimp.bmp')
        self.pos = [0.0, 0.0]
        self.dizzy = False
        self.area = None

    def update(self, td):
        """walk or spin, depending on the monkeys state

        :return: None
        """
        if self.dizzy:
            self.dizzy += self.turn_speed * td
            if self.dizzy >= 360:
                self.dizzy = 0
            self.rotation = int(self.dizzy)

        else:
            self.pos[0] += self.move_speed * td
            self.rect.x = int(round(self.pos[0], 0))
            overlap = sdl2.SDL_Rect()
            if not sdl2.SDL_IntersectRect(self.rect, self.area, overlap):
                self.move_speed = -self.move_speed
                #self.texture = pygame.transform.flip(self.texture, 1, 0)

    def punched(self):
        """this will cause the monkey to start spinning

        :return: None
        """
        if not self.dizzy:
            self.dizzy = True


_mouse_events = (
    sdl2.SDL_MOUSEMOTION,
    sdl2.SDL_MOUSEBUTTONDOWN,
    sdl2.SDL_MOUSEBUTTONUP)


def main():
    sdl2.ext.init()
    window = sdl2.ext.Window('Monkey Fever', size=(468, 60))
    renderer = sdl2.SDL_CreateRenderer(window.window, -1,
                                       sdl2.SDL_RENDERER_ACCELERATED)
    window.show()

    chimp = Chimp(renderer)
    w, h, = window.size
    chimp.area = sdl2.SDL_Rect(0, 0, w, h)

    fist = Fist(renderer)
    group = [chimp, fist]

    running = True
    now = sdl2.SDL_GetTicks()
    while running:
        sdl2.SDL_Delay(10)
        last_time = now
        now = sdl2.SDL_GetTicks()

        # get events
        events = sdl2.ext.get_events()
        for event in events:
            if event.type == sdl2.SDL_QUIT:
                running = False
                break

            elif event.type == sdl2.SDL_KEYDOWN:
                if event.key == sdl2.SDLK_ESCAPE:
                    pass

            elif event.type in _mouse_events:
                if event.button.button == sdl2.SDL_BUTTON_LEFT:
                    fist.set_punch(event.button.state == SDL_PRESSED)
                fist.move((event.motion.x, event.motion.y))

        # update
        dt = now - last_time
        for sprite in group:
            sprite.update(dt)

        # check collisions
        overlap = sdl2.SDL_Rect()
        if sdl2.SDL_IntersectRect(chimp.rect, fist.rect, overlap) and \
            fist.punching:
            chimp.punched()

        # render
        sdl2.SDL_SetRenderDrawColor(renderer, 255, 255, 255, 255)
        sdl2.SDL_RenderClear(renderer)
        for sprite in group:
            sdl2.SDL_RenderCopyEx(renderer, sprite.texture, None, sprite.rect,
                                  sprite.rotation, None, sprite.flip)
        sdl2.SDL_RenderPresent(renderer)

    return 0


if __name__ == "__main__":
    sys.exit(main())
