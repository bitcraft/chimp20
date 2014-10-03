import os
os.environ['PYSDL2_DLL_PATH'] = os.path.dirname(__file__)

import sys
import time
import sdl2
import sdl2.ext
from sdl2.ext.compat import *
from ctypes import c_uint32, c_int, byref

SDL_PRESSED = 1


def load_texture(renderer, name, colorkey=None):
    fullname = os.path.join('data', name)
    fullname = byteify(fullname, 'utf-8')
    surface = sdl2.SDL_LoadBMP(fullname)

    """
    i'm not sure how to extract the pixel format, so instead:
    - force pixel format to a known format without
    - set the colorkey
    -
    """
    #fmt = sdl2.SDL_PixelFormat(sdl2.SDL_PIXELFORMAT_RGBA8888)
    #surface = sdl2.SDL_ConvertSurface(_surface, fmt, 0)
    #sdl2.SDL_FreeSurface(_surface)
    #colorkey = sdl2.SDL_MapRGB(fmt, 255, 0, 0)
    #sdl2.SDL_SetColorKey(surface, 1, colorkey)

    texture = sdl2.SDL_CreateTextureFromSurface(renderer, surface)
    sdl2.SDL_FreeSurface(surface)
    sdl2.SDL_SetTextureBlendMode(texture, sdl2.SDL_BLENDMODE_BLEND)
    flags = c_uint32()
    access = c_int()
    w = c_int()
    h = c_int()
    sdl2.SDL_QueryTexture(texture, byref(flags), byref(access),
                          byref(w), byref(h))
    rect = sdl2.SDL_Rect(0, 0, w, h)

    return texture, rect


class Sprite(object):
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

    def update(self, dt):
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
        """set state of the fist

        :param state: to punch or not to punch?
        :return: None
        """
        self.punching = bool(state)


class Chimp(Sprite):
    """moves a monkey critter across the screen. it can spin the monkey when it
    is punched.
    """
    move_speed = 250
    turn_speed = 250

    def __init__(self, renderer):
        super(Chimp, self).__init__()
        self.renderer = renderer
        self.texture, self.rect = load_texture(renderer, 'chimp.bmp')
        self.pos = [0.0, 0.0]
        self.dizzy = False
        self.area = None

    def update(self, dt):
        """walk or spin, depending on the monkeys state

        :return: None
        """
        if self.dizzy:
            self.dizzy += self.turn_speed * dt
            if self.dizzy >= 360:
                self.dizzy = 0
            self.rotation = int(round(self.dizzy, 0))

        else:
            self.pos[0] += self.move_speed * dt
            self.rect.x = int(round(self.pos[0], 0))
            overlap = sdl2.SDL_Rect()
            if sdl2.SDL_IntersectRect(self.rect, self.area, overlap) and \
                overlap.w < self.rect.w:
                self.move_speed = -self.move_speed
                self.flip = self.move_speed < 1

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
    renderer = sdl2.SDL_CreateRenderer(window.window, -1, 0)
    window.show()

    chimp = Chimp(renderer)
    w, h, = window.size
    chimp.area = sdl2.SDL_Rect(0, 0, w, h)

    fist = Fist(renderer)
    group = [chimp, fist]

    running = True
    now = time.time()
    render_timer = 0
    event = sdl2.SDL_Event()

    get_time = time.time
    poll_event = sdl2.SDL_PollEvent
    set_render_draw_color = sdl2.SDL_SetRenderDrawColor
    render_clear = sdl2.SDL_RenderClear
    render_copy = sdl2.SDL_RenderCopy
    render_copy_ex = sdl2.SDL_RenderCopyEx
    render_present = sdl2.SDL_RenderPresent

    while running:
        last_time = now
        now = get_time()

        # get events
        while poll_event(event):
            if event.type == sdl2.SDL_QUIT:
                running = False
                break

            elif event.type == sdl2.SDL_KEYDOWN:
                if event.key == sdl2.SDLK_ESCAPE:
                    running = False
                    break

            elif event.type in _mouse_events:
                if event.button.button == sdl2.SDL_BUTTON_LEFT:
                    fist.set_punch(event.button.state == SDL_PRESSED)
                fist.move((event.motion.x, event.motion.y))

        # update
        dt = now - last_time
        for sprite in group:
            sprite.update(dt)

        # check collisions
        if fist.punching:
            overlap = sdl2.SDL_Rect()
            if sdl2.SDL_IntersectRect(chimp.rect, fist.rect, overlap):
                chimp.punched()

        # draw the scene
        render_timer += dt
        if render_timer >= .0167:
            render_timer -= .0167
            set_render_draw_color(renderer, 255, 255, 255, 255)
            render_clear(renderer)
            for sprite in group:
                render_copy_ex(renderer, sprite.texture, None,
                                      sprite.rect, sprite.rotation, None,
                                      sprite.flip)

            render_present(renderer)

    sdl2.SDL_DestroyRenderer(renderer)
    sdl2.SDL_DestroyWindow(window.window)
    sdl2.SDL_Quit()

    return 0


if __name__ == "__main__":
    sys.exit(main())
