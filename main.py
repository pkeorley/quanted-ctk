import tkinter
from io import BytesIO
from typing import List, Dict

import customtkinter
import requests
from PIL import ImageTk, Image
from customtkinter import CTkLabel
from pymongo import MongoClient

from client import RESTAppClient
from config import env


def _open_image_from_file(filepath: str):
    return ImageTk.PhotoImage(Image.open(filepath))


def _get_image_from_url(url: str):
    try:
        im = Image.open(BytesIO(requests.get(url).content))
        return ImageTk.PhotoImage(im)
    except Exception as e:
        print(f"Error while retrieving image from {url}: {e}")


class CommandManager(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set app geometry
        self.n = 1.3  # Scale of | weight <- Вага
        self.width = round(300 * self.n)  # Ширина
        self.height = round(250 * self.n)  # Висота
        self.geometry(f"{self.width}x{self.height}")

        # Set app settings
        self.title("Quanted Command Manager")
        self.iconbitmap("images/quanted.ico")
        self.iconphoto(False, tkinter.PhotoImage(file='images/quanted.png'))
        customtkinter.set_appearance_mode("System")
        customtkinter.set_default_color_theme("blue")
        self.resizable(False, False)

        # Connect to database
        self.cluster = MongoClient(env["MONGO_URL"])
        self.db = self.cluster.website

        # Variables
        self._colors = {"NORMAL": "#FFFFFF", "ERROR": "#FFBFBA"}

        """
        - TextBox
        - Frame
            - entry, button
        - label
        """

        # TextBox
        self.textbox = customtkinter.CTkTextbox(self, width=self.width - 20, height=self.height / 2)
        self.textbox.grid(column=0, row=0, padx=(10, 10), pady=(10, 10))

        # Frame
        self.frame = customtkinter.CTkFrame(self)
        self.frame.grid(column=0, row=1)

        # entry
        self.entry_command_name = customtkinter.CTkEntry(self.frame)
        self.entry_command_name.grid(column=0, row=0, padx=(10, 10), pady=(10, 10))

        # button
        self.add_button = customtkinter.CTkButton(self.frame, text="Додати код", command=self.add_code_to_db)
        self.add_button.grid(column=1, row=0, padx=(10, 10), pady=(10, 10))

        # label
        self.label = customtkinter.CTkLabel(self, text="$")
        self.label.grid(column=0, row=2, padx=(10, 10), pady=(10, 10))

    def add_code_to_db(self):

        command_name = self.entry_command_name.get()
        code = self.textbox.get("1.0", "end-1c")

        if not command_name:
            self._set_text_to_label("The bot command name field is empty!", type_="ERROR")
            return
        elif not code:
            self._set_text_to_label("The command code field is empty!", type_="ERROR")
            return

        data = {
            "command_name": command_name,
            "code": code
        }

        if self.db.app.count_documents({"command_name": command_name}) == 0:
            self._set_text_to_label(f"The {command_name} command was successfully added")
            self.db.app.insert_one(data)
        else:
            self._set_text_to_label(f"The command '{command_name}' already existed, so we replaced it")
            self.db.app.update_one({"command_name": command_name}, {"$set": {
                "code": code
            }})

    def _set_text_to_label(self, text, type_="NORMAL"):
        self.label.configure(text=text, text_color=self._colors[type_.upper()])
        self.label.update()


class App(customtkinter.CTk):
    def __init__(self, keys: Dict[str, str], *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Connect to database
        self.cluster = MongoClient(env["MONGO_URL"])
        self.db = self.cluster.website

        # Keys that have an int value in the database
        # TODO: Change this way of using a variable
        self.keys = keys

        # Connect to the discord bot
        self.rest = RESTAppClient()

        # Set app geometry
        self.n = 1.7  # Scale of | weight <- Вага
        self.width = round(500 * self.n)  # Ширина
        self.height = round(250 * self.n)  # Висота
        self.geometry(f"{self.width}x{self.height}")

        # Set app settings
        self.title("Quanted Admin Panel")
        self.iconbitmap("images/quanted.ico")
        self.iconphoto(False, tkinter.PhotoImage(file='images/quanted.png'))
        customtkinter.set_appearance_mode("System")
        customtkinter.set_default_color_theme("blue")
        self.resizable(False, False)

        # Load all items
        self.scrollable_frame = customtkinter.CTkScrollableFrame(self, width=self.width // 4, height=self.height)
        self.scrollable_frame.place(x=self.width - self.scrollable_frame.cget("width"), y=0)
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        # Create a label with information about the guild
        self.n1 = 15
        self.textarea_with_info = customtkinter.CTkTextbox(
            self,
            width=self.width - self.scrollable_frame.cget("width") - (self.n1 * 2),
            height=self.scrollable_frame.cget("height") - (self.n1 * 2)
        )
        self.textarea_with_info.place(x=self.n1, y=self.n1)
        self.textarea_with_info.configure(state=tkinter.DISABLED)

        # show all buttons to select a guild
        self.scrollable_frame_items = {}
        self.image_to_buttons = _open_image_from_file("images/right.png")
        # _get_image_from_url(self.rest.fetch_user(869910882434564116).make_avatar_url(size=16))

        for row, guild in enumerate(self.rest.get_all_bot_guilds()):
            self.button_to_switch_guild = customtkinter.CTkButton(
                master=self.scrollable_frame, text=guild.name,
                command=lambda gid=guild.id: self.guild_button_clicked(gid),
                image=self.image_to_buttons
            )
            self.button_to_switch_guild.grid(row=row, column=0, padx=0, pady=(10, 5))
            self.scrollable_frame_items[row] = self.button_to_switch_guild

        self.standart_title_label = customtkinter.CTkLabel(
            self.textarea_with_info,
            text="Оберіть сервер, для того щоб переглянути інформацію про нього",
            font=(18, 18)
        )
        self.standart_title_label.place(relx=0.5, rely=0.05, anchor=tkinter.CENTER)

        # Button to open sql editor
        self.settings_button = customtkinter.CTkButton(
            self.textarea_with_info,
            text="Налаштування",
            command=self.open_another_window
        )
        self.settings_button.place(
            x=self.textarea_with_info.cget("width") - self.settings_button.cget("width") - self.n1 + 5,
            y=self.textarea_with_info.cget("height") - self.settings_button.cget("height") - self.n1 + 5
        )

        # Another windows
        self.mongo_db_app = None

    def open_another_window(self):
        if self.mongo_db_app is None or not self.mongo_db_app.winfo_exists():
            self.mongo_db_app = CommandManager(self)
            self.mongo_db_app.focus()
        else:
            self.mongo_db_app.focus()

    # TODO: Map the changes
    def guild_button_clicked(self, guild_id: int):
        data = self._get_data_of_guild(guild_id)
        text = [f"• {self.keys.get(k, k)}: {v:,}" for k, v in data.items()]
        labels = self._set_text_on_textarea(text)

    def _set_text_on_textarea(self, text: List[str]) -> list[CTkLabel]:
        labels = []
        font_size = self.standart_title_label.cget("font")[0]
        for index, label in enumerate(text):
            text_on_textarea = customtkinter.CTkLabel(
                self.textarea_with_info,
                text=label,
                font=(font_size,) * 2
            )
            text_on_textarea.place(x=15, y=15 + ((index + 1) * font_size * 1.5))
            labels.append(text_on_textarea)
        return labels

    def _get_data_of_guild(self, guild_id: int):
        g = list(self.db.economic.find({"guild_id": int(guild_id)}))

        def _get_suma(key: str) -> int:
            return sum(list(map(lambda user: user.get(key, 0), g)))

        # TODO: Change the way it is used and add "init"
        return {k: _get_suma(k) for k in self.keys.keys()}


if __name__ == "__main__":
    app = App(keys={
        "coin": "Coins",
        "usd": "Dollars",
        "food": "Food",
        "win": "Wins",
        "lose": "Loses"
    })
    app.mainloop()
