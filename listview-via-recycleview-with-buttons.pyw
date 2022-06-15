#!/usr/bin/env python
'''
This is an example of a RecycleView.
This is based on code from [Clicking a button of an item in RecycleView
leads to a button of another item
flashing](https://github.com/kivy/kivy/issues/6902).
Poikilos changed:
- rename MyButton to ItemRow
'''
import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.properties import (
    StringProperty,
    ListProperty,
    NumericProperty,
)
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.boxlayout import BoxLayout


class ItemRow(RecycleDataViewBehavior,BoxLayout):
    key = StringProperty()
    def __init__(self,**kwargs):
        super().__init__(**kwargs)

    def add_data(self):
        app = App.get_running_app()
        new_key = app.generate_key()
        app.rv_data.append({"key":new_key})


class MyApp(App):
    rv_data = ListProperty()
    next_key_i = NumericProperty()

    def __init__(self, **kwargs):
        mylist = list()
        for i in range(10):
            mylist.append(dict(key=self.generate_key()))
        self.rv_data = mylist
        super().__init__(**kwargs)

    def generate_key(self):
        result = self.next_key_i
        self.next_key_i += 1
        return str(result)

    def build(self):
        return Builder.load_string("""
<ItemRow>
    orientation: "horizontal"
    Label:
        text: root.key
        color: 0,0,0,1
    Button:
        text: "Press Me"
        pos_hint: {"center_x": .5, "center_y": .5}
        size_hint_x: .5
        on_press: root.add_data()

Screen:
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
            cols: 2
            default_size: [0, dp(40)]
            default_size_hint: 1, None
            size_hint_x: 1
            size_hint_y: None
            height: self.minimum_height
            spacing: dp(5)
"""
)

if __name__ == '__main__':
    MyApp().run()
