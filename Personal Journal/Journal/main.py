# This code is generated using PyUIbuilder: https://pyuibuilder.com

import os
import customtkinter as ctk

BASE_DIR = os.path.dirname(os.path.abspath(__file__))



main = ctk.CTk()
main.configure(fg_color="#23272D")
main.title("Main Window")
main.geometry("700x400")

label = ctk.CTkLabel(master=main, text="Journal / or diary")
label.configure(fg_color="transparent", width=273, height=50, text_color="#fff")
label.place(x=0, y=0)

button = ctk.CTkButton(master=main, text="settings")
button.configure(fg_color="#029CFF", hover_color="#1e538d", width=61, height=40, text_color="#fff", corner_radius=5)
button.place(x=639, y=0)

accessibility_option_menu_options = ["option 1"]
accessibility_option_menu_var = ctk.StringVar(value="accessibility option menu")
accessibility_option_menu = ctk.CTkOptionMenu(main, variable=accessibility_option_menu_var, values=accessibility_option_menu_options)
accessibility_option_menu.configure(fg_color="#029CFF", text_color="#fff", corner_radius=5, button_color="#36719f", button_hover_color="#093c5e", dropdown_fg_color="#5C6266", dropdown_text_color="#fff", dropdown_hover_color="#2990E4")
accessibility_option_menu.place(x=439, y=0)

button1 = ctk.CTkButton(master=main, text="settings")
button1.configure(fg_color="#029CFF", hover_color="#1e538d", width=61, height=40, text_color="#fff", corner_radius=5)
button1.place(x=360, y=0)

button2 = ctk.CTkButton(master=main, text="settings")
button2.configure(fg_color="#029CFF", hover_color="#1e538d", width=61, height=40, text_color="#fff", corner_radius=5)
button2.place(x=280, y=0)

text = ctk.CTkTextbox(master=main)
text.configure(fg_color="#343739", width=700, height=111, text_color="#fff", corner_radius=5)
text.place(x=0, y=40)


main.mainloop()