from kivy.app import App
from kivy.lang import Builder
from kivy.uix.recycleview import RecycleView
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import (
    StringProperty,
    ListProperty,
    BooleanProperty,
    NumericProperty,
)
from kivy.clock import Clock

kv = '''
<TwoButtons>:
# This class is used as the viewclass in the RecycleView
# The means this widget will be instanced to view one element of data from the data list.
# The RecycleView data list is a list of dictionaries.  The keys in the dictionary specify the
# attributes of the widget.
    CheckBox:
        id: checkbox
        active: root.active
        on_release: root.on_checked_changed(root)
    Button:
        text: root.right_text
        on_release: print(f'{self.text} pressed')

BoxLayout:
    orientation: 'vertical'
    Button:
        size_hint_y: None
        height: 48
        text: 'Add widget to RV list'
        on_release: rv.add()

    RV:                          # A Reycleview
        id: rv
        viewclass: 'TwoButtons'  # The view class is TwoButtons, defined above.
        data: self.rv_data_list  # the data is a list of dicts defined below in the RV class.
        scroll_type: ['bars', 'content']
        bar_width: 10
        RecycleBoxLayout:
            # This layout is used to hold the Recycle widgets
            default_size: None, dp(48)   # This sets the height of the BoxLayout that holds a TwoButtons instance.
            default_size_hint: 1, None
            size_hint_y: None
            height: self.minimum_height   # To scroll you need to set the layout height.
            orientation: 'vertical'
'''


class TwoButtons(BoxLayout):  # The viewclass definitions, and property definitions.
    index = NumericProperty()
    active = BooleanProperty()
    right_text = StringProperty()

    def on_checked_changed(self, twobuttons):
        self.active = twobuttons.ids.checkbox.active
        app = App.get_running_app()
        app.root.ids.rv.rv_data_list[self.index]['active'] = self.active
        print(f'{self.right_text} checked={self.active}')


class RV(RecycleView):
    rv_data_list = ListProperty()  # A list property is used to hold the data for the recycleview, see the kv code

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for i in range(2):
            self.rv_data_list.append({
                'index': len(self.rv_data_list),
                'active': True,
                'right_text': f'Right {i}',
            })
        # This list comprehension is used to create the data list for this simple example.
        # The data created looks like:
        # [{'left_text': 'Left 0', 'right_text': 'Right 0'}, {'left_text': 'Left 1', 'right_text': 'Right 1'},
        # {'left_text': 'Left 2', 'right_text': 'Right 2'}, {'left_text': 'Left 3'},...
        # notice the keys in the dictionary correspond to the kivy properties in the TwoButtons class.
        # The data needs to be in this kind of list of dictionary formats.  The RecycleView instances the
        # widgets, and populates them with data from this list.

        Clock.schedule_interval(self.dump_values, 1)

    def dump_values(self, passed_seconds):
        print("* dump_values data={}".format(self.data))

    def add(self):
        index = len(self.rv_data_list)
        self.rv_data_list.append({
            'index': index,
            'active': False,
            'right_text': f'Added Right {index}',
        })


class RVTwoApp(App):

    def build(self):
        root = Builder.load_string(kv)
        return root


RVTwoApp().run()
