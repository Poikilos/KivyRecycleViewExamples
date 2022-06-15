# KivyRecycleViewExamples
The purpose of this repo is to track the correct way to use the Kivy RecycleView which replaces the ListView. This repo is based on rv_help by ElliotG including a Python version added for https://groups.google.com/g/kivy-users/c/P0c44_otKcI?pli=1

If you need to fix certain issues in your non-KV Python Kivy code quickly, you may want to look at the following commits:

<https://github.com/poikilos/KivyRecycleViewExamples/commit/2fc75c46ad803a2863d908c5e16a6c6487b49b02>
- Synchronize rv.data with rv_data using Python (handle a change event for a property, and in this case, set a RecycleView's data to a ListProperty).
- Set viewclass using Python.

<https://github.com/poikilos/KivyRecycleViewExamples/commit/8e7127b6ddff2509212bdf06229d29bc38de1f68>
- Synchronize the key and label text using Python.
- Set text color on a label.
