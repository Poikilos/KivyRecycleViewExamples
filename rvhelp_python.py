from kivy.app import App
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.properties import StringProperty, ListProperty
from kivy.clock import Clock


class ItemRow(BoxLayout):  # The viewclass definitions, and property definitions.
    left_text = StringProperty()
    right_text = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        b_left = Button(text=self.left_text, on_release=lambda x: print(f'Button {self.left_text} pressed'))
        self.add_widget(b_left)
        b_right = Button(text=self.right_text, on_release=lambda x: print(f'Button {self.right_text} pressed'))
        self.add_widget(b_right)

    def on_left_text(self, obj, v):
        self.children[1].text = v

    def on_right_text(self, obj, v):
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
        # notice the keys in the dictionary correspond to the kivy properties in the ItemRow class.
        # The data needs to be in this kind of list of dictionary formats.  The RecycleView instances the
        # widgets, and populates them with data from this list.
        Clock.schedule_once(self.set_viewclass)  # schedule setting the viewclass
        self.scroll_type = ['bars', 'content']
        self.bar_width = 10
        self.add_widget(RBL())

    def set_viewclass(self, _):
        self.viewclass = ItemRow

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
