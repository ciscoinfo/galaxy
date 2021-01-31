import math
import random

from kivy.core.audio import SoundLoader
from kivy.lang import Builder
from kivy.uix.relativelayout import RelativeLayout
from kivy.utils import platform
from kivy.config import Config

Config.set('graphics', 'width', '900')
Config.set('graphics', 'height', '400')

from kivy.core.window import Window
# redimmensionner la fenetre
from kivy.app import App
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Line, Quad, Triangle
from kivy.properties import *
from kivy.properties import Clock
from kivy.uix.widget import Widget

Builder.load_file("menu.kv")

def is_desktop():
    # detect if the current hardware id a desktop (not mobile)
    # It is one of: ‘win’, ‘linux’, ‘android’, ‘macosx’, ‘ios’ or ‘unknown’.
    if platform in ('linux', 'win', 'macosx'):
        return True
    else:
        return False


class MainWidget(RelativeLayout):
    from transforms import transform, transform_2D, transform_perspective, transform_perspective_v2
    from user_actions import _on_keyboard_down, _on_keyboard_up, on_touch_down, on_touch_up, _keyboard_closed

    menu_widget = ObjectProperty()
    perspective_point_x = NumericProperty(0)
    perspective_point_y = NumericProperty(0)
    menu_title = StringProperty("Galaxy")
    menu_button_title = StringProperty("Start")
    score_text = StringProperty("0")

    PERSP_Y = 0.75

    V_NB_LINES = 6
    V_LINES_SPACING = .2  # percentage in screen width

    H_NB_LINES = 10
    H_LINES_SPACING = .1  # percentage in screen width

    SPEED = 6

    SPEED_X = 15

    NB_TILES = 15
    tiles = []
    # liste de tiles
    tiles_coordinates = []
    # liste des coordonnées des tiles, sous forme de tuples

    #########################
    # en proportion de l'écran
    SHIP_WIDTH = .1
    SHIP_HEIGHT = 0.035
    SHIP_BASE_Y = 0.04

    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)
        # print(f"INIT W = {self.width} // H = {self.height}")
        self.init_vertical_lines()
        self.init_horizontal_lines()
        self.current_offset_y = 0
        self.current_offset_x = 0
        self.current_speed_x = 0
        self.current_y_loop = 0

        self.init_audio()

        self.state_game_started = False
        self.state_game_over = False

        self.init_tiles()
        self.init_ship()
        self.pre_fill_tiles_coordinates()
        self.generate_tiles_coordinates()


        if is_desktop():
            self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
            self._keyboard.bind(on_key_down=self._on_keyboard_down)
            self._keyboard.bind(on_key_up=self._on_keyboard_up)

        Clock.schedule_interval(self.update, 1.0 / 60.)

        self.sound_galaxy.play()

    """
    def on_parent(self, widget, parent):
        # apelé quand le widget est attaché à l'app'
        print(f"on_parent W = {self.width} // H = {self.height}")

    def on_size(self, *args):
        # print(f"on_size W = {self.width} // H = {self.height}")
        # self.perspective_point_x = self.width/2
        # self.perspective_point_y = self.height * PERSP_Y
        # print(f"perspective_point_x : {self.perspective_point_x}")
        # print(f"perspective_point_y : {self.perspective_point_y}")
        # self.calculate_offset()
        # self.update_vertical_lines()
        # self.update_horizontal_lines()
        pass
        """

    def init_audio(self):
        self.sound_begin = SoundLoader.load("audio/begin.wav")
        self.sound_galaxy = SoundLoader.load("audio/galaxy.wav")
        self.sound_gameover_impact = SoundLoader.load("audio/gameover_impact.wav")
        self.sound_gameover_voice = SoundLoader.load("audio/gameover_voice.wav")
        self.sound_music1 = SoundLoader.load("audio/music1.wav")
        self.sound_restart = SoundLoader.load("audio/restart.wav")

        self.sound_music1.volume = 1
        self.sound_begin.volume = .25
        self.sound_galaxy.volume = .25
        self.sound_gameover_voice.volume = .25
        self.sound_restart.volume = .25
        self.sound_gameover_impact.volume = .6

        # self.sound_music1.play()
        # self.sound_music1.stop()

    def reset_game(self):
        # self.state_game_started = True
        # self.init_tiles()
        # self.init_ship()
        self.current_offset_y = 0
        self.current_offset_x = 0
        self.current_speed_x = 0
        self.current_y_loop = 0

        self.tiles_coordinates = []
        self.pre_fill_tiles_coordinates()
        self.generate_tiles_coordinates()

        self.score_text = f"SCORE : {self.current_y_loop}"
        self.state_game_over = False

    def init_ship(self):
        with self.canvas:
            Color(0, 0, 0)
            self.ship = Triangle()

        self.ship_coordinates = [(0, 0), (0, 0), (0, 0)]

    def update_ship(self):
        #   2
        # 1   3

        center_x = self.width / 2
        base_y = self.SHIP_BASE_Y * self.height
        ship_height = self.SHIP_HEIGHT * self.height
        ship_width = self.SHIP_WIDTH * self.width

        x2 = center_x
        y2 = base_y + ship_height

        # update ship coorinates :
        self.ship_coordinates[1] = (x2, y2)

        # transform :
        x2, y2 = self.transform(x2, y2)

        # on peut écrire aussi :
        # x2, y2 = self.transform(self.ship_coordinates[1][0], self.ship_coordinates[1][1])
        # ou aussi (unpack):
        # x2, y2 = self.transform(*self.ship_coordinates[1])

        x1 = center_x - (ship_width / 2)
        y1 = base_y
        self.ship_coordinates[0] = (x1, y1)
        x1, y1 = self.transform(x1, y1)

        x3 = center_x + (ship_width / 2)
        y3 = base_y
        self.ship_coordinates[2] = (x3, y3)
        x3, y3 = self.transform(x3, y3)

        self.ship.points = [x1, y1, x2, y2, x3, y3]


    def check_ship_collision(self):
        for i in range(len(self.tiles_coordinates)):
            ti_x, ti_y = self.tiles_coordinates[i]
            if ti_y > self.current_y_loop + 1:
                # le tile est au dela des 2 premieres lignes
                return False
            if self.check_ship_collision_with_tile(ti_x, ti_y):
                return True
        return False



    def check_ship_collision_with_tile(self, ti_x, ti_y):
        xmin, ymin = self.get_tile_coordinates(ti_x, ti_y)
        xmax, ymax = self.get_tile_coordinates(ti_x + 1, ti_y + 1)

        for i in range(3):
            # recup les coord du ship
            px, py = self.ship_coordinates[i]
            if xmin <= px <= xmax and ymin <= py <= ymax:
                # on est à l'intérieur du tile' (au moins 1 point du ship)
                return True
        return False


    def init_tiles(self):
        with self.canvas:
            Color(1, 1, 1)
            for i in range(self.NB_TILES):
                self.tiles.append(Quad())
                # chaque tile est un quad (sans coordonnées)

    def pre_fill_tiles_coordinates(self):
        # 10 tiles en ligne droite
        NB_PREFILL = 10
        x_road = self.V_NB_LINES - 2 - math.ceil((self.V_NB_LINES - 2)/2)
        # print(x_road)
        for i in range(NB_PREFILL):
            self.tiles_coordinates.append([x_road, i])


    def generate_tiles_coordinates(self):
        last_y = 0
        last_x = 0

        # supprimer les coord sorties de l'écran'
        # ti_y < self.current_y_loop
        for i in range(len(self.tiles_coordinates)-1, -1, -1):
            if self.tiles_coordinates[i][1] < self.current_y_loop:
                del self.tiles_coordinates[i]

        if len(self.tiles_coordinates) > 0:
            last_coordinate = self.tiles_coordinates[-1]
            last_x = last_coordinate[0]
            last_y = last_coordinate[1]+1

        for i in range(len(self.tiles_coordinates), self.NB_TILES):

            if last_x == self.V_NB_LINES - 2:
                # collé à droite
                r = random.randint(0, 1)
            elif last_x == 0:
                # collé à gauche
                r = random.randint(1, 2)
            else:
                r = random.randint(0, 2)
                # 0 -> gauche
                # 1 -> devant
                # 2 -> droite
            self.tiles_coordinates.append((last_x, last_y))

            if r == 2:
                last_x += 1
                self.tiles_coordinates.append((last_x, last_y))
                last_y += 1
                self.tiles_coordinates.append((last_x, last_y))

            elif r == 0:
                last_x -= 1
                self.tiles_coordinates.append((last_x, last_y))
                last_y += 1
                self.tiles_coordinates.append((last_x, last_y))

            last_y += 1


    def init_vertical_lines(self):
        self.vertical_lines = []
        with self.canvas:
            Color(1, 1, 1)
            # self.line_l1 = Line(points=[100, 0, 100, 100])
            for i in range(self.V_NB_LINES):
                # new_line = Line(points=[i*self.V_LINES_SPACING, 0, i*self.V_LINES_SPACING, 100])
                # self.vertical_lines.append(new_line)
                self.vertical_lines.append(Line())
                # create tab with lines

    def init_horizontal_lines(self):
        self.horizontal_lines = []
        with self.canvas:
            Color(1, 1, 1)
            for i in range(self.H_NB_LINES):
                self.horizontal_lines.append(Line())



    def calculate_offset(self):
        self.x_road_spacing = self.V_LINES_SPACING * self.width
        total_offset = self.width - ((self.V_NB_LINES - 1) * self.x_road_spacing)
        self.mid_offset = total_offset / 2
        # calcul y_spacing
        self.y_road_spacing = self.H_LINES_SPACING * self.height

    def get_pos_x_from_index(self, index):
        # retourner la position x de la position verticale ) l'index
        pos_x = self.mid_offset + index * self.x_road_spacing + self.current_offset_x
        return pos_x

    def get_pos_y_from_index(self, index):
        # retourner la position x de la position verticale ) l'index
        pos_y = index * self.y_road_spacing - self.current_offset_y
        return pos_y

    def get_tile_coordinates(self, ti_x, ti_y):
        ti_y -= self.current_y_loop
        x = self.get_pos_x_from_index(ti_x)
        y = self.get_pos_y_from_index(ti_y)
        return x, y

    def update_tiles(self):
        for i in range(self.NB_TILES):
            # on recupere le tile
            tile = self.tiles[i]
            # et sa position (tuple)
            tile_coordinates = self.tiles_coordinates[i]
            xmin, ymin = self.get_tile_coordinates(tile_coordinates[0], tile_coordinates[1])
            xmax, ymax = self.get_tile_coordinates(tile_coordinates[0]+1, tile_coordinates[1]+1)

            # 2   3
            #
            # 1   4

            x1, y1 = self.transform(xmin, ymin)
            x2, y2 = self.transform(xmin, ymax)
            x3, y3 = self.transform(xmax, ymax)
            x4, y4 = self.transform(xmax, ymin)

            tile.points = [x1, y1, x2, y2, x3, y3, x4, y4]

    def update_vertical_lines(self):
        # Avec v_spacing

        # calcul de la largeur de l'offset = espace libre (total offset)
        # width - ( (nombre le lignes - 1) * espace entre lignes))
        # total_offset = self.width - (self.V_NB_LINES-1 * (V_LINES_SPACING * self.width) )

        # cette valeur est à diviser par 2 si on veut le delta_x avant (ou le delta_x après)
        # mid_offset = total_offset/2

        # on a donc :   mid_offset - spacings - mid_offset

        for i in range(self.V_NB_LINES):
            line_x = self.get_pos_x_from_index(i)
            x1, y1 = self.transform(line_x, 0)
            x2, y2 = self.transform(line_x, self.height)

            self.vertical_lines[i].points = [x1, y1, x2, y2]

    def update_horizontal_lines(self):

        for i in range(self.H_NB_LINES):
            line_y = self.get_pos_y_from_index(i)
            # on ajoute self.current_offset_y avec une boucle pour faire défiler
            # x1, y1 = self.transform(self.mid_offset + self.current_offset_x, line_y)
            # x2, y2 = self.transform(self.width - self.mid_offset + self.current_offset_x, line_y)

            x1, y1 = self.transform(self.get_pos_x_from_index(0), line_y)
            x2, y2 = self.transform(self.get_pos_x_from_index(self.V_NB_LINES - 1), line_y)

            self.horizontal_lines[i].points = [x1, y1, x2, y2]

    def update_score(self):
        self.score_text = f"SCORE : {self.current_y_loop}"

    ###########################################################################

    def update(self, dt):
        # print(f"dt : {dt*60}")
        time_factor = dt * 60
        self.calculate_offset()
        self.update_vertical_lines()
        self.update_horizontal_lines()
        self.update_tiles()
        self.update_ship()
        self.update_score()

        if not self.state_game_over and self.state_game_started:

            # vitesses relatives à la taille de l'écran'
            speed_y = self.SPEED * self.height / 1000
            speed_x = self.current_speed_x * self.width / 1000

            self.current_offset_y += speed_y * time_factor
            self.current_offset_x += speed_x * time_factor

            while self.current_offset_y >= self.y_road_spacing:
                self.current_offset_y -= self.y_road_spacing
                self.current_y_loop += 1
                self.generate_tiles_coordinates()


        if not self.check_ship_collision() and not self.state_game_over:
            print("GAME OVER")
            self.menu_title = "GAME OVER"
            self.menu_button_title = "RESTART"
            self.state_game_over = True
            self.menu_widget.opacity = 1

            self.sound_music1.stop()
            self.sound_gameover_impact.play()
            # self.sound_gameover_impact.seek(0)
            Clock.schedule_once(self.play_voice_game_over, 1)


    def play_voice_game_over(self, dt):
        if self.state_game_over:
            self.sound_gameover_voice.play()

    def on_menu_button_pressed(self):
        # print("Boutton clicked")

        if self.state_game_over:
            self.sound_restart.play()
            self.sound_gameover_impact.stop()
        else:
            self.sound_begin.play()

        self.sound_music1.play()

        self.reset_game()
        self.state_game_started = True
        self.menu_widget.opacity = 0

        # self.sound_gameover_impact.stop()
        # self.sound_gameover_voice.stop()


class GalaxyApp(App):
    pass


GalaxyApp().run()
