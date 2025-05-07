import tkinter as tk
from tkinter import colorchooser, filedialog, ttk
import random
from PIL import Image, ImageTk
import platform
import os
import threading
import winsound

# Константи
DEFAULT_BALANCE = 1000
SYMBOLS = ['🍒', '🍋', '🍊', '🍇', '🍉', '⭐']
BG_COLOR = "#ffffff"
TEXT_COLOR = "#000000"
FONT = "Arial"

class SoundPlayer:
    @staticmethod
    def play(sound_type):
        if not hasattr(SoundPlayer, '_enabled') or SoundPlayer._enabled:
            sounds = {
                'win': [(2000, 500)],
                'lose': [(500, 500)],
                'jackpot': [(2000, 200), (1500, 200), (2000, 200), (2500, 200), (3000, 200)]
            }
            for freq, duration in sounds.get(sound_type, []):
                SoundPlayer._beep(freq, duration)

    @staticmethod
    def _beep(frequency, duration):
        try:
            if platform.system() == "Windows":
                winsound.Beep(frequency, duration)
            elif platform.system() == "Darwin":
                os.system(f'afplay -r 1 -t {duration/1000} -v 0.5 <(printf "\%0.s" {frequency}) 2>/dev/null')
            elif platform.system() == "Linux":
                os.system(f'beep -f {frequency} -l {duration} 2>/dev/null')
        except: pass

    @staticmethod
    def toggle(state):
        SoundPlayer._enabled = state

SoundPlayer._enabled = True

class CasinoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Казино")
        self.geometry("500x400")
        self.minsize(400, 300)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.balance = DEFAULT_BALANCE
        self.bg_color = BG_COLOR
        self.text_color = TEXT_COLOR
        self.bg_image_path = None
        
        self.frames = {
            "WelcomeFrame": WelcomeFrame(self, self),
            "MenuFrame": MenuFrame(self, self),
            "DonateFrame": DonateFrame(self, self),
            "WithdrawFrame": WithdrawFrame(self, self),
            "GameFrame": GameFrame(self, self),
            "BackgroundFrame": BackgroundFrame(self, self),
            "SettingsFrame": SettingsFrame(self, self)
        }
        
        for frame in self.frames.values():
            frame.grid(row=0, column=0, sticky="nsew")
        
        self.show_frame("WelcomeFrame")

    def show_frame(self, name):
        self.frames[name].tkraise()
        self.update_background()

    def update_background(self):
        for frame in self.frames.values():
            for widget in frame.winfo_children():
                try: widget.configure(bg=self.bg_color, fg=self.text_color)
                except: pass
            
            if self.bg_image_path:
                try:
                    image = Image.open(self.bg_image_path)
                    width, height = frame.winfo_width(), frame.winfo_height()
                    if width > 0 and height > 0:
                        image = image.resize((width, height), Image.LANCZOS)
                        photo = ImageTk.PhotoImage(image)
                        
                        if not hasattr(frame, 'bg_label'):
                            frame.bg_label = tk.Label(frame, image=photo)
                            frame.bg_label.image = photo
                            frame.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
                        else:
                            frame.bg_label.configure(image=photo)
                            frame.bg_label.image = photo
                        frame.bg_label.lower()
                except: self.bg_image_path = None
            else:
                frame.configure(bg=self.bg_color)
                if hasattr(frame, 'bg_label'):
                    frame.bg_label.destroy()
                    del frame.bg_label

class BaseFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.create_widgets()

    def create_widgets(self): pass

class WelcomeFrame(BaseFrame):
    def create_widgets(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        tk.Label(self, text="🎰 Ласкаво просимо до казино!", font=(FONT, 20)).grid(row=0, column=0, pady=20)
        tk.Button(self, text="Почати", font=(FONT, 14), width=15, height=2,
                 command=lambda: self.controller.show_frame("MenuFrame")).grid(row=1, column=0, pady=20)

class MenuFrame(BaseFrame):
    def create_widgets(self):
        for i in range(6): self.grid_rowconfigure(i, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        buttons = [
            ("Грати", "GameFrame"),
            ("Поповнити", "DonateFrame"),
            ("Вивести", "WithdrawFrame"),
            ("🎨 Змінити фон", "BackgroundFrame"),
            ("⚙ Налаштування", "SettingsFrame"),
            ("Вихід", "quit")
        ]
        
        tk.Label(self, text="Головне меню", font=(FONT, 20)).grid(row=0, column=0, pady=10)
        
        for i, (text, cmd) in enumerate(buttons, 1):
            if cmd == "quit":
                action = self.controller.quit
            else:
                action = lambda c=cmd: self.controller.show_frame(c)
                
            tk.Button(self, text=text, font=(FONT, 14), width=15, height=2,
                     command=action).grid(row=i, column=0, pady=5)

class SettingsFrame(BaseFrame):
    def create_widgets(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        tk.Label(self, text="Налаштування", font=(FONT, 20)).grid(row=0, column=0, pady=10)
        
        self.sound_var = tk.BooleanVar(value=SoundPlayer._enabled)
        ttk.Checkbutton(self, text="Увімкнути звук", variable=self.sound_var,
                       command=lambda: SoundPlayer.toggle(self.sound_var.get())).grid(row=1, column=0, pady=10)
        
        tk.Button(self, text="Назад", font=(FONT, 12), width=10,
                command=lambda: self.controller.show_frame("MenuFrame")).grid(row=2, column=0, pady=20)

class DonateFrame(BaseFrame):
    def create_widgets(self):
        for i in range(7): self.grid_rowconfigure(i, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        fields = [
            ("Номер картки (16 цифр):", False),
            ("CVV2 (3 цифри):", True),
            ("Термін дії (MM/YY):", False),
            ("Сума поповнення:", False)
        ]
        
        tk.Label(self, text="Поповнення балансу", font=(FONT, 16)).grid(row=0, column=0, pady=10)
        self.entries = []
        for i, (text, is_pwd) in enumerate(fields, 1):
            tk.Label(self, text=text).grid(row=i*2-1, column=0, sticky="e", padx=10)
            entry = tk.Entry(self, show="*" if is_pwd else "")
            if text == "Сума поповнення:": entry.insert(0, "100")
            entry.grid(row=i*2, column=0, sticky="ew", padx=20)
            self.entries.append(entry)
        
        tk.Button(self, text="Поповнити", font=(FONT, 12), width=15,
                command=self.donate).grid(row=9, column=0, pady=10)
        self.msg = tk.Label(self, text="", font=(FONT, 10))
        self.msg.grid(row=10, column=0)
        tk.Button(self, text="Назад", font=(FONT, 12), width=10,
                command=lambda: self.controller.show_frame("MenuFrame")).grid(row=11, column=0, pady=10)

    def donate(self):
        card, cvv, date, amount = (e.get().strip() for e in self.entries)
        try:
            amount = int(amount)
            if (len(card) == 16 and card.isdigit() and len(cvv) == 3 and cvv.isdigit() and
                len(date) == 5 and date[2] == '/' and date[:2].isdigit() and date[3:].isdigit() and amount > 0):
                self.controller.balance += amount
                self.msg.config(text=f"Баланс поповнено на {amount}. Залишок: {self.controller.balance}")
            else: self.msg.config(text="Невірні реквізити")
        except ValueError: self.msg.config(text="Сума має бути числом")

class WithdrawFrame(BaseFrame):
    def create_widgets(self):
        for i in range(5): self.grid_rowconfigure(i, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        tk.Label(self, text="Виведення коштів", font=(FONT, 16)).grid(row=0, column=0, pady=10)
        
        tk.Label(self, text="Номер картки (16 цифр):").grid(row=1, column=0, sticky="e", padx=10)
        self.card_entry = tk.Entry(self)
        self.card_entry.grid(row=2, column=0, sticky="ew", padx=20)
        
        tk.Label(self, text="Сума виводу:").grid(row=3, column=0, sticky="e", padx=10)
        self.amount_entry = tk.Entry(self)
        self.amount_entry.insert(0, "100")
        self.amount_entry.grid(row=4, column=0, sticky="ew", padx=20)
        
        tk.Button(self, text="Вивести", font=(FONT, 12), width=15,
                 command=self.withdraw).grid(row=5, column=0, pady=10)
        self.msg = tk.Label(self, text="", font=(FONT, 10))
        self.msg.grid(row=6, column=0)
        tk.Button(self, text="Назад", font=(FONT, 12), width=10,
                 command=lambda: self.controller.show_frame("MenuFrame")).grid(row=7, column=0, pady=10)

    def withdraw(self):
        card, amount = self.card_entry.get().strip(), self.amount_entry.get().strip()
        try:
            amount = int(amount)
            if len(card) == 16 and card.isdigit() and 0 < amount <= self.controller.balance:
                self.controller.balance -= amount
                self.msg.config(text=f"Виведено {amount}. Залишок: {self.controller.balance}")
            else: self.msg.config(text="Невірна картка або недостатньо грошей")
        except ValueError: self.msg.config(text="Сума має бути числом")

class GameFrame(BaseFrame):
    def create_widgets(self):
        self.spinning = False
        
        for i in range(7): self.grid_rowconfigure(i, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Слот-машина
        self.slot_frame = tk.Frame(self)
        self.slot_frame.grid(row=1, column=0, sticky="nsew", pady=10)
        for i in range(3): self.slot_frame.grid_columnconfigure(i, weight=1)
        
        self.labels = []
        for i in range(3):
            frame = tk.Frame(self.slot_frame, bg="#FF00FF", bd=3, relief=tk.RAISED)
            frame.grid(row=0, column=i, sticky="nsew", padx=5, pady=5)
            label = tk.Label(frame, text=random.choice(SYMBOLS), font=(FONT, 30), bg="#000000", fg="#FFFFFF")
            label.pack(expand=True, fill="both")
            self.labels.append(label)
        
        # Елементи керування
        tk.Label(self, text="Ставка:").grid(row=2, column=0, sticky="e", padx=10)
        self.bet_entry = tk.Entry(self)
        self.bet_entry.insert(0, "10")
        self.bet_entry.grid(row=3, column=0, sticky="ew", padx=20)
        
        self.spin_button = tk.Button(self, text="SPIN", font=(FONT, 14), width=15, height=2,
                                   command=self.animate_spin)
        self.spin_button.grid(row=4, column=0, pady=10)
        
        self.result_label = tk.Label(self, text="", font=(FONT, 12))
        self.result_label.grid(row=5, column=0)
        self.balance_label = tk.Label(self, text=f"Баланс: {self.controller.balance}", font=(FONT, 12))
        self.balance_label.grid(row=6, column=0)
        
        tk.Button(self, text="Назад", font=(FONT, 12), width=10,
                command=lambda: self.controller.show_frame("MenuFrame")).grid(row=7, column=0, pady=10)
        
        self.bind("<Configure>", lambda e: [l.config(font=(FONT, max(20, int(self.winfo_width()/20)))) for l in self.labels])

    def animate_spin(self):
        if self.spinning: return
        
        try:
            bet = int(self.bet_entry.get())
            if bet <= 0: return self.result_label.config(text="Ставка має бути > 0")
            if bet > self.controller.balance: return self.result_label.config(text="Недостатньо грошей")
        except ValueError: return self.result_label.config(text="Ставка має бути числом")

        self.spinning, self.frames, self.bet = True, 10, bet
        self.spin_button.config(state=tk.DISABLED)
        self.update_spin()

    def update_spin(self):
        if self.frames > 0:
            for label in self.labels: label.config(text=random.choice(SYMBOLS))
            self.frames -= 1
            self.after(100, self.update_spin)
        else:
            self.spinning = False
            self.spin_button.config(state=tk.NORMAL)
            final = [random.choice(SYMBOLS) for _ in range(3)]
            for i, symbol in enumerate(final): self.labels[i].config(text=symbol)
            
            if final[0] == final[1] == final[2]:
                win = int(self.bet * 1.5)
                self.controller.balance += win
                self.result_label.config(text=f"🎉 Виграш +{win} (x1.5)")
                threading.Thread(target=lambda: SoundPlayer.play('win')).start()
            elif random.randint(1, 100) == 1:
                jackpot = self.bet * 10
                self.controller.balance += jackpot
                self.result_label.config(text=f"💰 ДЖЕКПОТ! +{jackpot}")
                threading.Thread(target=lambda: SoundPlayer.play('jackpot')).start()
            else:
                self.controller.balance -= self.bet
                self.result_label.config(text=f"Програш -{self.bet}")
                threading.Thread(target=lambda: SoundPlayer.play('lose')).start()
            
            self.balance_label.config(text=f"Баланс: {self.controller.balance}")

class BackgroundFrame(BaseFrame):
    def create_widgets(self):
        for i in range(6): self.grid_rowconfigure(i, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        buttons = [
            ("Обрати колір фону", self.choose_bg_color),
            ("Обрати фонове зображення", self.choose_image),
            ("Скинути фон", self.reset_background),
            ("Обрати колір тексту", self.choose_text_color),
            ("Назад", lambda: self.controller.show_frame("MenuFrame"))
        ]
        
        tk.Label(self, text="Налаштування фону", font=(FONT, 16)).grid(row=0, column=0, pady=10)
        for i, (text, cmd) in enumerate(buttons, 1):
            tk.Button(self, text=text, font=(FONT, 12), width=20,
                    command=cmd).grid(row=i, column=0, pady=5)

    def choose_bg_color(self):
        if color := colorchooser.askcolor(title="Оберіть колір фону")[1]:
            self.controller.bg_color = color
            self.controller.bg_image_path = None
            self.controller.update_background()

    def choose_image(self):
        if path := filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")]):
            self.controller.bg_image_path = path
            self.controller.update_background()

    def reset_background(self):
        self.controller.bg_color = BG_COLOR
        self.controller.bg_image_path = None
        self.controller.update_background()

    def choose_text_color(self):
        if color := colorchooser.askcolor(title="Оберіть колір тексту")[1]:
            self.controller.text_color = color
            self.controller.update_background()

if __name__ == "__main__":
    CasinoApp().mainloop()