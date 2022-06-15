#!/usr/bin/env python
'''
This is an imperative version of code from
[Clicking a button of an item in RecycleView
leads to a button of another item
flashing](https://github.com/kivy/kivy/issues/6902) (except renamed
MyButton to ItemRow)

Changes:
- uses imperative code rather than KV.
- assigns a key to each row (for synchronizing with a data source).

Known issues:
- (main issue) The window is blank since assigning viewclass fails.
  The constructor for ItemRow is never called (see comments).
- Binding the data to rv_data ListProperty doesn't work (see comments).
- Binding the bgRect size to the Screen or ScreenManager size doesn't
  work (see comments).
'''
from __future__ import print_function
import sys
import kivy
from kivy.app import App
from kivy.uix.screenmanager import (
    ScreenManager,
    Screen,
)
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import (
    Color,
    Rectangle,
)
from kivy.properties import (
    StringProperty,
    ListProperty,
    NumericProperty,
)
from kivy.uix.recycleview import RecycleView
from kivy.uix.recyclegridlayout import RecycleGridLayout
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock

verbose = 2

# NOTE: When using kivy, args get erased :(
#   (len is 1: only the py* file is in sys.argv).
for argI in range(1, len(sys.argv)):
    arg = sys.argv[argI]
    if arg.startswith("--"):
        if arg == "--verbose":
            verbose = 1
        elif arg == "--debug":
            verbose = 2


def echo0(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def echo1(msg):
    if verbose < 1:
        return
    echo0("[verbose] {}".format(msg))


def echo2(msg):
    if verbose < 2:
        return
    echo0("[debug] {}".format(msg))


class ItemRow(RecycleDataViewBehavior, BoxLayout):
    key = StringProperty()

    def __init__(self, **kwargs):
        # ^ kwargs=={} by default, and self.key is "" at this point.
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        echo1("    - building ItemRow")
        label = Label(color=(0, 0, 0, 1))
        self.label = label
        self.add_widget(label)

        button = Button(
            text="Press me",
            pos_hint={"center_x": .5, "center_y": .5},
            size_hint_x=.5,
            on_release=self.add_data,
        )
        self.button = button
        self.add_widget(button)

    def add_data(self, _):
        echo2("* add_data")
        Clock.schedule_once(self._add_data, .2)

    def on_key(self, itemrow, value):
        self.label.text = value

    def _add_data(self, button):
        app = App.get_running_app()
        new_key = app.generate_key()
        entry = {
            'key': new_key,
        }
        self.key = new_key
        app.sm.screen.rv_data.append(entry)


class KeyedView(RecycleView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.set_viewclass)

    def set_viewclass(self, _):
        echo2("* set_viewclass")
        self.viewclass = ItemRow

class ItemScreen(Screen):
    '''
    A Screen *must* be inside a ScreenManager (See
    <https://kivy.org/doc/stable/
    api-kivy.uix.screenmanager.html?
    highlight=screen#kivy.uix.screenmanager.Screen>)
    '''
    rv_data = ListProperty()

    def __init__(self, **kwargs):
        # NOTE: build is only for App.
        super().__init__(**kwargs)
        echo1("* ItemScreen init")
        self.bgColor = Color(1, 1, 1, 1, mode='rgba')
        self.bgRect = Rectangle()
        self.canvas.before.add(self.bgColor)
        self.canvas.before.add(self.bgRect)
        # ^ NOTE: Change rect size to screen,
        #   but on_size only occurs for ScreenManager not Screen.

    def custom_on_size(self):
        echo2("* ItemScreen custom_on_size")
        # self.bgRect.size = (self.size[0], self.size[1])
        self.bgRect.size = (self.size[0]*2, self.size[1]*2)
        # ^ *2 is necessary to prevent size lagging behind for some
        #   reason. *2 works most of the time except rare cases when
        #   the window is resized by more than 2x in one refresh.

    def on_rv_data(self, *args):
        echo2("* on_rv_data {}".format(args))
        app = App.get_running_app()
        app.rv.data = self.rv_data


class ItemScreens(ScreenManager):
    '''
    A Screen *must* be inside a ScreenManager (See
    <https://kivy.org/doc/stable/
    api-kivy.uix.screenmanager.html?
    highlight=screen#kivy.uix.screenmanager.Screen>)
    '''
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print("* ItemScreens init")
        screen = ItemScreen()
        self.screen = screen

    def on_size(self, *args):
        # ^ must take 3 positional arguments
        # See <https://kivy.readthedocs.io/_/downloads/en/master/pdf/>
        # in section 45.1.2 "Adding behaviors".
        # on_size only occurs for ScreenManager.
        echo2("* ItemScreens was resized.")
        echo2("  args: {}".format(args))
        self.screen.custom_on_size()

    def on_parent(self, *args):
        echo1("* ItemScreens on_parent")
        echo1("  args: {}".format(args))
        self.on_size()


class HybridRowsApp(App):
    next_key_i = NumericProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def generate_key(self):
        result = str(self.next_key_i)
        echo2("* generate_key {}".format(result))
        self.next_key_i += 1
        return result

    def build(self):
        sm = ItemScreens()  # ScreenManager()
        self.sm = sm
        screen = sm.screen
        self.screen = screen

        rv = KeyedView()
        self.rv = rv

        key = self.generate_key()
        self.sm.screen.rv_data.append({'key':key})

        rv.data = screen.rv_data
        rv_layout = RecycleGridLayout()
        self.rv_layout = rv_layout
        rv_layout.cols = 2
        rv_layout.default_size_hint = (1, None)

        sm.add_widget(screen)
        screen.add_widget(rv)
        rv.add_widget(rv_layout)

        Clock.schedule_once(self.sm.on_size, .1)
        return sm


if __name__ == '__main__':
    HybridRowsApp().run()
