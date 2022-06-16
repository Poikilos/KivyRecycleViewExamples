from kivy.app import App
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.properties import (
    StringProperty,
    ListProperty,
    BooleanProperty,
)

from kivy.clock import Clock


class TwoButtons(BoxLayout):  # The viewclass definitions, and property definitions.
    active = BooleanProperty()
    right_text = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        b_left = CheckBox(active=self.active, on_release=lambda x: print(f'{self.right_text} checked={x.active}'))
        self.add_widget(b_left)
        b_right = Button(text=self.right_text, on_release=lambda x: print(f'{self.right_text} pressed'))
        self.add_widget(b_right)

    def on_active(self, obj, v):
        print("on_left_text({}, {})".format(obj, v))
        self.children[1].text = v

    def on_right_text(self, obj, v):
        print("on_right_text({}, {})".format(obj, v))
        self.children[0].text = v


class RBL(RecycleBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.default_size = (None, 48)
        self.default_size_hint = (1, None)
        self.size_hint_y = None
        self.orientation = 'vertical'

    def on_minimum_height(self, obj, v):
        self.height = self.minimum_height


class RV(RecycleView):
    rv_data_list = ListProperty()  # A list property is used to hold the data for the recycleview, see the kv code

    def on_rv_data_list(self, *args):
        self.data = self.rv_data_list

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.rv_data_list = [{'left_text': f'Left {i}', 'right_text': f'Right {i}'} for i in range(2)]
        # This list comprehension is used to create the data list for this simple example.
        # The data created looks like:
        # [{'left_text': 'Left 0', 'right_text': 'Right 0'}, {'left_text': 'Left 1', 'right_text': 'Right 1'},
        # {'left_text': 'Left 2', 'right_text': 'Right 2'}, {'left_text': 'Left 3'},...
        # notice the keys in the dictionary correspond to the kivy properties in the TwoButtons class.
        # The data needs to be in this kind of list of dictionary formats.  The RecycleView instances the
        # widgets, and populates them with data from this list.
        Clock.schedule_once(self.set_viewclass)  # schedule setting the viewclass
        self.scroll_type = ['bars', 'content']
        self.bar_width = 10
        self.add_widget(RBL())

    def set_viewclass(self, _):
        self.viewclass = TwoButtons

    def add(self, *args):
        l = len(self.rv_data_list)
        self.rv_data_list.extend(
            [{'left_text': f'Added Left {i}', 'right_text': f'Added Right {i}'} for i in range(l, l + 1)])


class RootWidget(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.rv = RV()    # the RecycleView
        button = Button(size_hint_y=None, height=48, text='Add Widget to RV list',
                        on_release=self.rv.add)
        self.add_widget(button)
        self.add_widget(self.rv)


class RVTwoApp(App):
    def build(self):
        return RootWidget()


RVTwoApp().run()
