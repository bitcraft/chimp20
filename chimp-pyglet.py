import pyglet


def load_image(filename):
    image = pyglet.resource.image(filename)
    image.anchor_x = image.width/2
    image.anchor_y = image.height/2
    return image


class GameSprite(pyglet.sprite.Sprite):
    batch = pyglet.graphics.Batch()

    def __init__(self, *args, **kwargs):
        super(GameSprite, self).__init__(*args, batch=self.batch, **kwargs)
        self.velocity = [0.0, 0.0]

    def update(self, dt):
        self.x += self.velocity[0] * dt
        self.y += self.velocity[1] * dt
        hw = self.image.width / 2
        if self.x + hw > 468 or self.x - hw < 0:
            self.velocity[0] = -self.velocity[0]


class ChimpSprite(GameSprite):
    def update(self, dt):
        if self.rotation:
            self.rotation += 300 * dt
            if self.rotation >= 360:
                self.rotation = 0
        else:
            super(ChimpSprite, self).update(dt)


game_window = pyglet.window.Window(468, 60)

pyglet.resource.path = ['data']
pyglet.resource.reindex()

chimp = ChimpSprite(img=load_image('chimp.bmp'), x=234, y=20)
fist = GameSprite(img=load_image('fist.bmp'),x=0, y=0)

chimp.velocity[0] = 200.0

update_group = [chimp, fist]


def update(dt):
    for sprite in update_group:
        sprite.update(dt)

@game_window.event
def on_draw():
    game_window.clear()
    GameSprite.batch.draw()


@game_window.event()
def on_mouse_motion(x, y, dx, dy):
    fist.x = x
    fist.y = y


@game_window.event()
def on_mouse_press(x, y, button, modifiers):
    chimp.rotation = 0.00000001

if __name__ == '__main__':
    pyglet.clock.schedule_interval(update, 1/120.0)
    pyglet.app.run()