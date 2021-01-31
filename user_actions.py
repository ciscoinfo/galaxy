from kivy.uix.relativelayout import RelativeLayout


def _keyboard_closed(self):
    self._keyboard.unbind(on_key_down=self._on_keyboard_down)
    self._keyboard.unbind(on_key_up=self._on_keyboard_up)
    self._keyboard = None

def on_touch_down(self, touch):

    if not self.state_game_over and self.state_game_started:
        # evenement lorsqu'on appuie
        if touch.x < self.width / 2:
            # print("<===")
            self.current_speed_x = self.SPEED_X
            # self.current_offset_x -= self.x_road_spacing
        else:
            # print("===>")
            # self.current_offset_x += self.x_road_spacing
            self.current_speed_x = -self.SPEED_X

        # Cette fonction surcharge le comportement normal, c'est un override
    return super(RelativeLayout, self).on_touch_down(touch)


def on_touch_up(self, touch):
    # evenement lorsqu'on relache
    # print("relacher")
    self.current_speed_x = 0


def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
    if keycode[1] == 'left':
        self.current_speed_x = self.SPEED_X
    elif keycode[1] == 'right':
        self.current_speed_x = -self.SPEED_X
    return True


def _on_keyboard_up(self, keyboard, keycode):
    self.current_speed_x = 0
    # print("relacher")