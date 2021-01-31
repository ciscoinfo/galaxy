from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.widget import Widget


class MenuWidget(RelativeLayout):
    def on_touch_down(self, touch):
        if self.opacity == 0:
            # ne pas gérer le boutton
            return False
        # Cette fonction surcharge le comportement normal, c'est un override
        return super(RelativeLayout, self).on_touch_down(touch)