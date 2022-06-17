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


class ItemRow(BoxLayout):
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
            on_release=lambda this_cb: self.on_checkbox_pressed(self),
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
        Clock.schedule_once(lambda seconds: _._add_data(_), .2)

    def _add_data(self, itemrow):
        echo2("  - _add_data({})".format(itemrow))
        app = App.get_running_app()
        entry = {
            'checked': False,
            'key': app.generate_key(),
        }
        app.rv.rv_data.append(entry)

    def on_checkbox_pressed(self, itemrow):
        '''
        The checkbox changed the value, so update the data source
        (self.checked hasn't changed yet).
        '''
        app = App.get_running_app()
        echo2("on_checkbox_pressed({})".format(type(itemrow).__name__))
        echo2("- self.key={} checked={}"
              "".format(self.key, self.checked))
        echo2("- itemrow.key={} checked={}"
              "".format(itemrow.key, itemrow.checked))
        echo2("- data={}".format(app.rv.rv_data))
        self.checked = itemrow.checkbox.active
        if "{}".format(itemrow.key) == "":
            echo2("- skipped (no key)")
            return
        if app.rv.get_row(itemrow.key)['checked'] != self.checked:
            app.rv.get_row(itemrow.key)['checked'] = self.checked
        # print(f'{self.right_text} checked={self.checked}')

    def on_checked(self, itemrow, value):
        '''
        The data source changed the value, or the checked property
        changed for some other reason, so change the checkbox.
        '''
        app = App.get_running_app()
        linked_checked = None
        if "{}".format(itemrow.key) != "":
            linked_checked = app.rv.get_row(itemrow.key)['checked']
        echo2("on_checked(itemrow.key={}, {}) self.checkbox.active={}"
              " [{}]['checked']={}"
              "".format(itemrow.key, value, self.checkbox.active,
                        itemrow.key, linked_checked))
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
        linked_checked = None
        if "{}".format(itemrow.key) != "":
            linked_checked = app.rv.get_row(itemrow.key)['checked']
        echo2("on_checked(itemrow.key={}, {}) self.checkbox.active={}"
              " [{}]['checked']={}"
              "".format(itemrow.key, value, self.checkbox.active,
                        itemrow.key,
                        linked_checked))
        self.label.text = value
        '''
        if self.checkbox.active != itemrow.checked:
            self.checkbox.active = itemrow.checked
            echo1("  fixing data:{}".format(app.rv.data))
        '''


class KeyedView(RecycleView):
    rv_data = ListProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        app = App.get_running_app()
        '''
        mylist = list()
        for i in range(3):
            key = app.generate_key()
            mylist.append({
                'key': key,
                'checked': True,
            })
            echo1("* appended {}".format(key))
        self.rv_data = mylist
        '''
        for i in range(3):
            key = app.generate_key()
            self.rv_data.append({
                'key': key,
                'checked': True,
            })
            echo1("* appended {}".format(key))

        Clock.schedule_once(self.set_viewclass)
        # ^ schedule setting the viewclass

    def set_viewclass(self, seconds):
        echo2("* set_viewclass(seconds)")
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
        echo2("* on_rv_data(keyedview, data)")
        echo2("  - rv_data={}".format(data))
        self.data = self.rv_data
        # echo2("dir(self): {}".format(dir(self)))
        # self.view_adapter.make_views_dirty()
        # ^ Doesn't fix checkboxes if whole list is replaced.
        # self.view_adapter.invalidate()
        # ^ Doesn't fix checkboxes if whole list is replaced.
        echo2("  - len(self.view_adapter.views): {}"
              "".format(len(self.view_adapter.views)))
        '''
        for i in range(len(self.view_adapter.views)):
            echo2("  - setting [{}] to {}".format(i, self.data[i]))
            # self.view_adapter.items[i].checked = self.data[i]['checked']
            # ^ self.view_adapter has no attribute 'items'
            # self.view_adapter.views[i].checked = self.data[i]['checked']
            # ^ Doesn't help, since self.data is wrong (values change
            #   random each time a "+" button is clicked)!

        # app = App.get_running_app()
        for i in range(len(data)):
            if self.rv_data[i] != data[i]:
                self.rv_data[i] = data[i]
            # else avoid infinite loop
        '''
        # Clock.schedule_once(self.read_data, .1)


class ItemScreen(BoxLayout):
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

    def custom_on_size(self):
        echo2("* ItemScreen custom_on_size")
        # self.bgRect.size = (self.size[0], self.size[1])
        self.bgRect.size = (self.size[0]*2, self.size[1]*2)
        # ^ *2 is necessary to prevent size lagging behind for some
        #   reason. *2 works most of the time except rare cases when
        #   the window is resized by more than 2x in one refresh.

    def on_size(self, *args):
        # ^ must take 3 positional arguments
        # See <https://kivy.readthedocs.io/_/downloads/en/master/pdf/>
        # in section 45.1.2 "Adding behaviors".
        # on_size only occurs for ScreenManager.
        echo2("* ItemScreens was resized.")
        echo2("  args: {}".format(args))
        self.custom_on_size()


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
        self.screen = ItemScreen()
        screen = self.screen

        self.rv = KeyedView()

        rv_layout = RecycleGridLayout()
        self.rv_layout = rv_layout
        rv_layout.cols = 1
        rv_layout.default_size_hint = (1, None)

        screen.add_widget(self.rv)
        self.rv.add_widget(rv_layout)

        Clock.schedule_once(self.screen.on_size, .1)
        return screen


if __name__ == '__main__':
    HybridRowsApp().run()
