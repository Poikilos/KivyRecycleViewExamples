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
# from kivy.lang import Builder
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
        # RecycleDataViewBehavior.__init__(**kwargs)
        # BoxLayout.__init__(**kwargs)
        # ^ doesn't help, because __init__ is never called
        self.orientation = "horizontal"
        print("    - building ItemRow")

        label = Label(color=(0, 0, 0, 1))
        self.label = label
        self.add_widget(label)

        button = Button(
            text="Press me",
            pos_hint={"center_x": .5, "center_y": .5},
            size_hint_x=.5,
            on_press=self.add_data,
        )
        self.button = button
        self.add_widget(button)

    def on_key(self, itemrow, value):
        self.label.text = self.key

    def add_data(self, button):
        app = App.get_running_app()
        new_key = app.generate_key()
        entry = {
            'key': new_key,
        }
        self.key = new_key
        app.rv.data.append(entry)


class KeyedView(RecycleView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.set_viewclass)

    def set_viewclass(self, _):
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
        # self.bind(on_size=self.custom_on_size)
        # ^ fails silently
        # self.on_size = self.custom_on_size
        # ^ fails silently
        self.bgColor = Color(1, 1, 1, 1, mode='rgba')
        self.bgRect = Rectangle()
        # TODO: The following works now (on_size only occurs for
        #   ScreenManager, so look there for the event though):
        self.canvas.before.add(self.bgColor)
        self.canvas.before.add(self.bgRect)


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
        # self.add_widget(screen)
        # self.bind(on_size=self.on_size_change)
        # ^ "AttributeError: 'ItemScreens' object has no attribute
        #   'on_size'. Did you mean: 'on_size_change'?"
        #   so renamed on_size_change to on_size

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

    # def custom_on_size(self):
    #     # This doesn't work. It also doesn't work if named on_size
    #     # or on_resize despite documentation at
    #     # <https://kivy.readthedocs.io/_/downloads/en/master/pdf/>
    #     # in section 45.1.2 "Adding behaviors".
    #     self.screen.custom_on_size()

    def fix_size(self, *args):
        # Make the bgRect behave before resize (doesn't work in build
        # since the Window size isn't finalized by then, so this method
        # has to be scheduled.
        echo1("* App fix_size")
        echo1("  args: {}".format(args))
        self.sm.on_size()

        echo1("* adding more test data")
        key = self.generate_key()
        # self.sm.screen.rv_data.append({'key':key})
        # ^ Appending to self.sm.screen.rv_data has no effect
        #   (but does during build)!
        echo1("* adding bad test data")
        self.rv.data.append({'key':"bad"})
        echo1("len(self.rv.data): {}".format(len(self.rv.data)))

    def build(self):
        sm = ItemScreens()  # ScreenManager()
        self.sm = sm
        screen = sm.screen
        self.screen = screen
        # self.bind(on_size=screen.custom_on_size)
        # ^ fails silently
        # self.on_size=self.custom_on_size
        # ^ fails silently

        echo1("  * building Screen manually in App")
        '''
        with screen.canvas:
            Color(1, 1, 1, 1, mode='rgba')
            Rectangle(pos=screen.pos, size=screen.size)
        '''
        # bgColor = Color(1, 1, 1, 1, mode='rgba')
        # screen.canvas.add(bgColor)
        # bgRect.bind(size=screen.size.setter('size'))
        # ^ AttributeError:
        #   'kivy.graphics.vertex_instructions.Rectangle' object has no
        #   attribute 'bind'
        # bgRect = Rectangle(pos=screen.pos, size_hint=(1.0, 1.0))
        # ^ doesn't help
        # screen.canvas.before.add(bgColor)
        # bgRect.size is a tuple, so try making it into a list property:

        # bgRect = Rectangle(pos=screen.pos, size=screen.size)
        # screen.size = ListProperty(screen.size)
        # ^ "ValueError: ItemScreen.size must be a list or a tuple type"
        #   so:

        # bgRect = Rectangle()
        # screen.bgRect = bgRect
        # print("type(bgRect.size):{}".format(type(bgRect.size).__name__))

        # screen.bind(width=screen.setter('width'))
        # ^ fails silently

        # screen.canvas.before.add(bgRect)
        # ^ commented since nothing seems to work to make the rect match
        #   the size of the container :(

        # rv = KeyedView(viewclass=ItemRow)
        # ^ accepts viewclass or view_adapter
        # ^ doesn't work: the form is blank; type(rv.viewclass) NoneType
        rv = KeyedView()
        # type(rv.viewclass) is NoneType regardless of what is passed
        #   to the constructor.
        echo0("type(rv.viewclass): {}"
              "".format(type(rv.viewclass).__name__))
        self.rv = rv
        # rv.viewclass = "ItemRow"
        # ^ doesn't work (the form is blank)
        # rv.viewclass = ItemRow
        # ^ doesn't work (the form is blank)

        # See <kivy.org/doc/stable/api-kivy.uix.recycleview.views.html>:
        '''
        "The view module handles converting the data to a view using
        the adapter class which is then displayed by the layout. A
        view can be any Widget based class. However, inheriting from
        RecycleDataViewBehavior adds methods for converting the data
        to a view."
        '''
        #
        # rv.recycleview = ItemRow
        # ^ doesn't work (the form is blank)
        # itemrow = ItemRow()
        # self.rv.attach_recycleview(itemrow)
        # ^ "AttributeError: 'KeyedView' object has no attribute
        #   'attach_recycleview'"
        #   (site above says "Associates a RecycleViewBehavior with
        #   this instance. It is stored in recycleview.")


        echo1("* adding test data")
        '''
        mylist = list()
        for i in range(10):
            key = self.generate_key()
            mylist.append(dict(key=key))
            print("* appended {}".format(key))
        self.sm.screen.rv_data = mylist
        '''
        key = self.generate_key()
        self.sm.screen.rv_data.append({'key':key})

        rv.data = screen.rv_data
        rv_layout = RecycleGridLayout()
        self.rv_layout = rv_layout
        rv_layout.cols = 2
        # rv_layout.default_size = [0, dp(40)]
        rv_layout.default_size_hint = (1, None)
        # rv_layout.height = screen.minimum_height
        # ^ AttributeError: 'ItemScreen' object has no attribute
        #   'minimum_height'
        # rv_layout.height = sm.minimum_height
        # ^ AttributeError: 'ScreenManager' object has no attribute
        #   'minimum_height'
        # rv_layout.height = self.minimum_height
        # ^ AttributeError: 'HybridRowsApp' object has no attribute
        #   'minimum_height'
        # rv_layout.spacing = dp(5)

        sm.add_widget(screen)
        screen.add_widget(rv)
        rv.add_widget(rv_layout)

        Clock.schedule_once(self.fix_size, .1)
        return sm
        # return Builder.load_string(kv)


if __name__ == '__main__':
    HybridRowsApp().run()
