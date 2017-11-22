import pyglet
import os
import math

def start(looper):
    COLOR = (0,255,0)
    FRAMERATE = 1.0/10
    window = pyglet.window.Window(fullscreen=True, resizable=True)
    #window.set_size(1100, 750)
    batch = pyglet.graphics.Batch()
    height, width = window.get_size()
    
    print "SIZE:", height, width
    images = [pyglet.image.load(os.path.join(os.path.dirname(__file__), 'image%s.png' % (i+1))) for i in range(2)]
    
    @window.event
    def on_draw():
        window.clear()

        sprites = []
        for role, positions in looper.kinect.get_visible_user_joint_positions().iteritems():
            image = images[role - 1]
            for x, y in positions:
                if math.isnan(x) or math.isnan(y) or math.isinf(x) or math.isinf(y):
                    continue
                
                sprite = pyglet.sprite.Sprite(image, batch=batch)
                #sprite.x = float(x) / 640 * width * 3 / 4 + width / 8
                #sprite.y = (480 - float(y)) / 480 * height * 3 / 4 + height / 8
                sprite.x = x * 1.6 + 200
                sprite.y = 680 - y
                sprite.scale = 0.5
                sprites.append(sprite)

        for player in range(2):
            role = player + 1
            tracks = looper.user_tracks[role]
            for track_idx in range(3):
                track = tracks[track_idx]
                
                sprite = pyglet.sprite.Sprite(images[player], batch=batch)
                sprite.x = player * 800 + 100 + track_idx * 70
                sprite.y = 40
                
                if looper.active_tracks[role] == track_idx:
                    sprite.y += 20
                if track.is_recording:
                    sprite.y += 30
                #sprite.scale = 0.5
                sprites.append(sprite)

        #py
        batch.draw()
        pyglet.clock.schedule_interval(lambda dt: None, FRAMERATE)

    @window.event
    def on_key_press(symbol, modifiers):
        if symbol == pyglet.window.key.ESCAPE:
            print "Exiting Pyglet app"
            pyglet.app.exit()
        elif symbol == pyglet.window.key.F:
            window.set_fullscreen(not window.fullscreen)

    pyglet.app.run()
