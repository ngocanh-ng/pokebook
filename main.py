from login import LoginApp
import ttkbootstrap as ttk

root = ttk.Window(themename="minty")
app = LoginApp(root)
root.mainloop()