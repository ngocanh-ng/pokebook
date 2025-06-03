from login import LoginApp
from pokebook_app import PokebookApp
import ttkbootstrap as ttk

root = ttk.Window(themename="minty")
app = LoginApp(root)
root.mainloop()