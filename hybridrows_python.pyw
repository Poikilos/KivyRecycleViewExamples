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
from kivy.uix.checkbox import CheckBox
from kivy.graphics import (
    Color,
    Rectangle,
)
from kivy.properties import (
    StringProperty,
    ListProperty,
    NumericProperty,
    BooleanProperty,
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
    echo0("{}".format(msg))


def echo2(msg):
    if verbose < 2:
        return
    echo0("{}".format(msg))


class ItemRow(RecycleDataViewBehavior, BoxLayout):
    key = StringProperty()
    checked = BooleanProperty()

    def __init__(self, **kwargs):
        # ^ kwargs=={} by default, and self.key is "" at this point.
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        echo1("building ItemRow")

        button = Button(
            text="+",
            pos_hint={"center_x": .5, "center_y": .5},
            size_hint_x=.1,
            on_release=lambda this_btn: self.add_data(self),
        )
        self.button = button
        self.add_widget(button)

        checkbox = CheckBox(
            active=self.checked,
            on_release=lambda this_cb: self.on_checked_changed(self),
            size_hint_x=.1,
        )
        # ^ If not using a lambda, the param will be this checkbox.
        self.checkbox = checkbox
        self.add_widget(checkbox)

        label = Label(color=(0, 0, 0, 1))
        self.label = label
        self.add_widget(label)

    def add_data(self, _):
        echo2("")
        echo2("add_data(itemrow) self.key:{}".format(_.key))
        Clock.schedule_once(self._add_data, .2)

    def on_checked_changed(self, itemrow):
        '''
        The checkbox changed the value, so update the data source
        (self.checked hasn't changed yet).
        '''
        app = App.get_running_app()
        echo2("on_checked_changed({})".format(type(itemrow).__name__))
        echo2("- self.key={} checked={}"
              "".format(self.key, self.checked))
        echo2("- itemrow.key={} checked={}"
              "".format(itemrow.key, itemrow.checked))
        echo2("- data={}".format(app.rv.rv_data))
        self.checked = itemrow.checkbox.active
        if "{}".format(itemrow.key) == "":
            echo2("- skipped (no key)")
            return
        app.rv.get_row(itemrow.key)['checked'] = itemrow.checked

    def on_checked(self, itemrow, value):
        '''
        The data source changed the value, or the checked property
        changed for some other reason, so change the checkbox.
        '''
        app = App.get_running_app()
        key_checked = None
        if "{}".format(itemrow.key) != "":
            key_checked = app.rv.get_row(itemrow.key)['checked']
        echo2("on_checked(itemrow.key={}, {}) self.checkbox.active={}"
              " [{}]['checked']={}"
              "".format(itemrow.key, value, self.checkbox.active,
                        itemrow.key, key_checked))
        if self.checkbox.active != value:
            echo2("- self.checkbox.active=value")
            self.checkbox.active = value
        if "{}".format(itemrow.key) == "":
            echo2("- skipped (no key)")
            # Key is blank while being created, so this isn't a press,
            # but the checkbox still needs to change.
            pass
        elif app.rv.get_row(itemrow.key)['checked'] != value:
            echo2("- app.rv.get_row(itemrow.key)['checked']=value")
            app.rv.get_row(itemrow.key)['checked'] = value

    def on_key(self, itemrow, value):
        app = App.get_running_app()
        echo2("on_key(({}, {}), {})"
              "".format(itemrow.key, itemrow.checked, value))
        key_checked = None
        if "{}".format(itemrow.key) != "":
            key_checked = app.rv.get_row(itemrow.key)['checked']
        echo2("on_checked(itemrow.key={}, {}) self.checkbox.active={}"
              " [{}]['checked']={}"
              "".format(itemrow.key, value, self.checkbox.active,
                        itemrow.key,
                        key_checked))
        self.label.text = value
        '''
        if self.checkbox.active != itemrow.checked:
            self.checkbox.active = itemrow.checked
            echo1("  fixing data:{}".format(app.rv.data))
        '''

    def _add_data(self, seconds):
        echo2("  * _add_data(seconds) self.key:{}".format(self.key))
        # ^ The key is NOT for the value being added, but clicked.
        app = App.get_running_app()
        entry = {
            'checked': False,
            'key': app.generate_key(),
        }
        app.rv.rv_data.append(entry)


class KeyedView(RecycleView):
    rv_data = ListProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.set_viewclass)

    def set_viewclass(self, _):
        echo2("* set_viewclass({})".format(_))
        self.viewclass = ItemRow

    def get_row(self, key):
        return self.rv_data[self.find_row(key)]

    def find_row(self, key):
        if not isinstance(key, str):
            raise ValueError(
                "key must be str but is {} {}"
                "".format(type(key).__name__, key)
            )
        for i in range(len(self.rv_data)):
            if self.rv_data[i]['key'] == key:
                return i
        return -1

    def on_rv_data(self, keyedview, data):
        echo2("* on_rv_data(keyedview, {})".format(data))
        app = App.get_running_app()
        app.rv.data = self.rv_data


class ItemScreen(Screen):
    '''
    A Screen *must* be inside a ScreenManager (See
    <https://kivy.org/doc/stable/
    api-kivy.uix.screenmanager.html?
    highlight=screen#kivy.uix.screenmanager.Screen>)
    '''

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

    def custom_on_size(self, _):
        # ^ _ may be seconds (See schedule_once) or itemscreens
        echo2("* ItemScreen custom_on_size")
        # self.bgRect.size = (self.size[0], self.size[1])
        self.bgRect.size = (self.size[0]*2, self.size[1]*2)
        # ^ *2 is necessary to prevent size lagging behind for some
        #   reason. *2 works most of the time except rare cases when
        #   the window is resized by more than 2x in one refresh.


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
        self.screen = ItemScreen()

    def on_size(self, itemscreens, size):
        # ^ must take 3 positional arguments
        # See <https://kivy.readthedocs.io/_/downloads/en/master/pdf/>
        # in section 45.1.2 "Adding behaviors".
        # on_size only occurs for ScreenManager.
        echo2("* on_size(itemscreens, {}).".format(size))
        self.screen.custom_on_size(itemscreens)

    def on_parent(self, itemscreens, window):
        echo1("* ItemScreens on_parent(itemscreens, window)")
        self.on_size(itemscreens, itemscreens.size)


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
        self.sm = ItemScreens()  # ScreenManager()
        self.rv = KeyedView()
        for i in range(3):
            self.rv.rv_data.append({
                'key': self.generate_key(),
                'checked': True,
            })

        rv_layout = RecycleGridLayout()
        self.rv_layout = rv_layout
        rv_layout.cols = 1
        rv_layout.default_size_hint = (1, None)

        self.sm.add_widget(self.sm.screen)
        self.sm.screen.add_widget(self.rv)
        self.rv.add_widget(rv_layout)

        Clock.schedule_once(self.sm.screen.custom_on_size, .1)
        return self.sm


if __name__ == '__main__':
    HybridRowsApp().run()
