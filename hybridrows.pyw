#!/usr/bin/env python
'''
This is an example of a RecycleView.
This is based on code from [Clicking a button of an item in RecycleView
leads to a button of another item
flashing](https://github.com/kivy/kivy/issues/6902).
Poikilos changed:
- rename MyButton to ItemRow
'''
from __future__ import print_function
import sys
import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.properties import (
    StringProperty,
    ListProperty,
    NumericProperty,
    BooleanProperty,
)
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.boxlayout import BoxLayout

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
        super().__init__(**kwargs)

    def add_data(self, itemrow):
        echo2("add_data(itemrow.key={})".format(itemrow.key))
        app = App.get_running_app()
        new_key = app.generate_key()
        app.rv_data.append({
            'key': new_key,
            'checked': False,
        })

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
        echo2("- data={}".format(app.rv_data))
        echo2("- checkbox.active={}"
              "".format(itemrow.ids.checkbox.active))
        self.checked = itemrow.ids.checkbox.active
        app.get_row(itemrow.key)['checked'] = itemrow.ids.checkbox.active
        # ^ This works (app.rv_data at the correct index changes) but
        #   upon adding a new row, the value is reset!
        # print(f'{self.right_text} checked={self.checked}')
        print(f'app.rv_data:{app.rv_data}')

    def on_checked(self, itemrow, value):
        '''
        The data source changed the value, or the checked property
        changed for some other reason, so change the checkbox.
        '''
        app = App.get_running_app()
        key_checked = None
        if "{}".format(itemrow.key) != "":
            key_checked = app.get_row(itemrow.key)['checked']
        echo2("on_checked(itemrow.key={}, {}) self.checkbox.active={}"
              " [{}]['checked']={}"
              "".format(itemrow.key, value, itemrow.ids.checkbox.active,
                        itemrow.key, key_checked))
        if itemrow.ids.checkbox.active != value:
            echo2("- itemrow.ids.checkbox.active=value")
            itemrow.ids.checkbox.active = value
        if "{}".format(itemrow.key) == "":
            echo2("- skipped (no key)")
            # Key is blank while being created, so this isn't a press,
            # but the checkbox still needs to change.
            pass
        elif app.get_row(itemrow.key)['checked'] != value:
            echo2("- app.get_row(itemrow.key)['checked']=value")
            app.get_row(itemrow.key)['checked'] = value

    def on_key(self, itemrow, value):
        echo2("on_key(({}, {}), {})"
              "".format(itemrow.key, itemrow.checked, value))
        self.ids.label.text = value


class HybridRowsApp(App):
    rv_data = ListProperty()
    next_key_i = NumericProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        '''
        mylist = []
        for i in range(3):
            mylist.append({
                'key': self.generate_key(),
                'checked': True,
            })
        self.rv_data = mylist
        '''
        for i in range(3):
            self.rv_data.append({
                'key': self.generate_key(),
                'checked': True,
            })

    def set_checked(self, key, value):
        self.rv_data[self.find_row(key)] = value

    def get_row(self, key):
        return self.rv_data[self.find_row(key)]

    def find_row(self, key):
        for i in range(len(self.rv_data)):
            if self.rv_data[i]['key'] == key:
                return i
        return -1

    def generate_key(self):
        result = self.next_key_i
        self.next_key_i += 1
        return str(result)

    def build(self):
        return Builder.load_string("""
<ItemRow>
    orientation: "horizontal"
    Button:
        text: "+"
        pos_hint: {"center_x": .5, "center_y": .5}
        size_hint_x: .1
        on_release: root.add_data(root)
    CheckBox:
        id: checkbox
        size_hint_x: .1
        active: root.checked
        on_release: root.on_checked_changed(root)
    Label:
        id: label
        text: root.key
        color: 0,0,0,1

BoxLayout:
    canvas.before:
        Color:
            rgba: 1,1,1,1
        Rectangle:
            pos: self.pos
            size: self.size
    RecycleView:
        id: rv
        viewclass: "ItemRow"
        data: app.rv_data
        RecycleGridLayout:
            cols: 1
            default_size: [0, dp(40)]
            default_size_hint: 1, None
            size_hint_x: 1
            size_hint_y: None
            height: self.minimum_height
            spacing: dp(5)
"""
)
        # returns a BoxLayout.
        # return root


if __name__ == '__main__':
    HybridRowsApp().run()
