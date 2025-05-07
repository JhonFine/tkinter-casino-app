import tkinter as tk
from tkinter import colorchooser, filedialog
import random
from PIL import Image, ImageTk
import platform
import os
import threading
import winsound

# Глобальні змінні
balance = 100
symbols = ['🍒', '🍋', '🍊', '🍇', '🍉', '⭐']

class SoundPlayer:
    @staticmethod
    def play_win():
        SoundPlayer._play_sound(2000, 500)

    @staticmethod
    def play_lose():
        SoundPlayer._play_sound(500, 500)

    @staticmethod
    def play_jackpot():
        for freq in [2000, 1500, 2000, 2500, 3000]:
            SoundPlayer._play_sound(freq, 200)

    @staticmethod
    def _play_sound(frequency, duration):
        system = platform.system()
        try:
            if system == "Windows":
                winsound.Beep(frequency, duration)
            elif system == "Darwin":
                os.system(f'afplay -r 1 -t {duration/1000} -v 0.5 <(printf "\%0.s" {frequency}) 2>/dev/null')
            elif system == "Linux":
                os.system(f'beep -f {frequency} -l {duration} 2>/dev/null')
        except:
            pass

class CasinoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Казино")
        self.geometry("500x400")
        self.minsize(400, 300)
        self.resizable(True, True)
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.frames = {}
        self.bg_color = "#ffffff"
        self.text_color = "#000000"
        self.bg_image_path = None
        self.create_frames()
        self.show_frame("WelcomeFrame")

    def create_frames(self):
        for F in (WelcomeFrame, MenuFrame, DonateFrame, WithdrawFrame, GameFrame, BackgroundFrame):
            frame = F(parent=self, controller=self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

    def show_frame(self, name):
        frame = self.frames[name]
        frame.tkraise()
        self.update_background()

    def update_background(self):
        for frame_name, frame in self.frames.items():
            try:
                for widget in frame.winfo_children():
                    try:
                        widget.configure(bg=self.bg_color, fg=self.text_color)
                    except:
                        pass
                
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
                    except Exception as e:
                        print(f"Помилка завантаження фону: {e}")
                        self.bg_image_path = None
                else:
                    frame.configure(bg=self.bg_color)
                    if hasattr(frame, 'bg_label'):
                        frame.bg_label.destroy()
                        del frame.bg_label
            except Exception as e:
                print(f"Помилка оновлення кадру {frame_name}: {e}")

class WelcomeFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        tk.Label(self, text="🎰 Ласкаво просимо до казино!", 
                font=("Arial", 20))\
            .grid(row=0, column=0, pady=20)
        
        tk.Button(self, text="Почати", 
                command=lambda: controller.show_frame("MenuFrame"),
                font=("Arial", 14),
                width=15,
                height=2)\
            .grid(row=1, column=0, pady=20)

class MenuFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        for i in range(7):
            self.grid_rowconfigure(i, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        tk.Label(self, text="Головне меню", 
                font=("Arial", 20))\
            .grid(row=0, column=0, pady=10)
        
        buttons = [
            ("Грати", "GameFrame"),
            ("Поповнити", "DonateFrame"),
            ("Вивести", "WithdrawFrame"),
            ("🎨 Змінити фон", "BackgroundFrame"),
            ("Вихід", "quit")
        ]
        
        for i, (text, command) in enumerate(buttons, start=1):
            if command == "quit":
                cmd = controller.quit
            else:
                cmd = lambda c=command: controller.show_frame(c)
                
            tk.Button(self, text=text, command=cmd,
                     font=("Arial", 14),
                     width=15,
                     height=2)\
                .grid(row=i, column=0, pady=5)

class DonateFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        for i in range(7):
            self.grid_rowconfigure(i, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        tk.Label(self, text="Поповнення балансу",
                font=("Arial", 16))\
            .grid(row=0, column=0, pady=10)
        
        fields = [
            ("Номер картки (16 цифр):", False),
            ("CVV2 (3 цифри):", True),
            ("Термін дії (MM/YY):", False),
            ("Сума поповнення:", False)
        ]
        
        self.entries = []
        for i, (text, is_password) in enumerate(fields, start=1):
            tk.Label(self, text=text)\
                .grid(row=i*2-1, column=0, sticky="e", padx=10)
            entry = tk.Entry(self, show="*" if is_password else "")
            if text == "Сума поповнення:":
                entry.insert(0, "100")
            entry.grid(row=i*2, column=0, sticky="ew", padx=20)
            self.entries.append(entry)

        tk.Button(self, text="Поповнити", 
                command=self.donate,
                font=("Arial", 12),
                width=15)\
            .grid(row=9, column=0, pady=10)
        
        self.msg = tk.Label(self, text="", font=("Arial", 10))
        self.msg.grid(row=10, column=0)

        tk.Button(self, text="Назад", 
                command=lambda: controller.show_frame("MenuFrame"),
                font=("Arial", 12),
                width=10)\
            .grid(row=11, column=0, pady=10)

    def donate(self):
        global balance
        card = self.entries[0].get().strip()
        cvv = self.entries[1].get().strip()
        date = self.entries[2].get().strip()
        amount = self.entries[3].get().strip()
        
        try:
            amount = int(amount)
            if (len(card) == 16 and card.isdigit() and
                len(cvv) == 3 and cvv.isdigit() and
                len(date) == 5 and date[2] == '/' and
                date[:2].isdigit() and date[3:].isdigit() and
                amount > 0):
                
                balance += amount
                self.msg.config(text=f"Баланс поповнено на {amount}. Залишок: {balance}")
            else:
                self.msg.config(text="Невірні реквізити")
        except ValueError:
            self.msg.config(text="Сума має бути числом")

class WithdrawFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        for i in range(5):
            self.grid_rowconfigure(i, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        tk.Label(self, text="Виведення коштів",
                font=("Arial", 16))\
            .grid(row=0, column=0, pady=10)
        
        tk.Label(self, text="Номер картки (16 цифр):")\
            .grid(row=1, column=0, sticky="e", padx=10)
        self.card_entry = tk.Entry(self)
        self.card_entry.grid(row=2, column=0, sticky="ew", padx=20)

        tk.Label(self, text="Сума виводу:")\
            .grid(row=3, column=0, sticky="e", padx=10)
        self.amount_entry = tk.Entry(self)
        self.amount_entry.insert(0, "100")
        self.amount_entry.grid(row=4, column=0, sticky="ew", padx=20)

        tk.Button(self, text="Вивести", 
                command=self.withdraw,
                font=("Arial", 12),
                width=15)\
            .grid(row=5, column=0, pady=10)
        
        self.msg = tk.Label(self, text="", font=("Arial", 10))
        self.msg.grid(row=6, column=0)

        tk.Button(self, text="Назад", 
                command=lambda: controller.show_frame("MenuFrame"),
                font=("Arial", 12),
                width=10)\
            .grid(row=7, column=0, pady=10)

    def withdraw(self):
        global balance
        card = self.card_entry.get().strip()
        amount = self.amount_entry.get().strip()
        
        try:
            amount = int(amount)
            if (len(card) == 16 and card.isdigit() and 
                0 < amount <= balance):
                balance -= amount
                self.msg.config(text=f"Виведено {amount}. Залишок: {balance}")
            else:
                self.msg.config(text="Невірна картка або недостатньо грошей")
        except ValueError:
            self.msg.config(text="Сума має бути числом")

class GameFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.spinning = False
        
        for i in range(7):
            self.grid_rowconfigure(i, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Слот-машина
        self.slot_frame = tk.Frame(self)
        self.slot_frame.grid(row=1, column=0, sticky="nsew", pady=10)
        
        for i in range(3):
            self.slot_frame.grid_columnconfigure(i, weight=1, uniform="slots")
            
        self.labels = []
        for i in range(3):
            symbol_frame = tk.Frame(
                self.slot_frame,
                bg="#FF00FF",
                bd=3,
                relief=tk.RAISED
            )
            symbol_frame.grid(row=0, column=i, sticky="nsew", padx=5, pady=5)
            
            label = tk.Label(
                symbol_frame,
                text=random.choice(symbols),
                font=("Arial", 30),
                bg="#000000",
                fg="#FFFFFF"
            )
            label.pack(expand=True, fill="both")
            self.labels.append(label)

        # Елементи керування
        tk.Label(self, text="Ставка:")\
            .grid(row=2, column=0, sticky="e", padx=10)
        self.bet_entry = tk.Entry(self)
        self.bet_entry.insert(0, "10")
        self.bet_entry.grid(row=3, column=0, sticky="ew", padx=20)

        self.spin_button = tk.Button(self, text="SPIN", 
                                   command=self.animate_spin,
                                   font=("Arial", 14),
                                   width=15,
                                   height=2)
        self.spin_button.grid(row=4, column=0, pady=10)

        self.result_label = tk.Label(self, text="", font=("Arial", 12))
        self.result_label.grid(row=5, column=0)
        
        self.balance_label = tk.Label(self, text=f"Баланс: {balance}", font=("Arial", 12))
        self.balance_label.grid(row=6, column=0)

        tk.Button(self, text="Назад", 
                command=lambda: controller.show_frame("MenuFrame"),
                font=("Arial", 12),
                width=10)\
            .grid(row=7, column=0, pady=10)

        self.bind("<Configure>", self.on_resize)

    def on_resize(self, event):
        width = self.winfo_width()
        font_size = max(20, int(width / 20))
        
        for label in self.labels:
            label.config(font=("Arial", font_size))

    def animate_spin(self):
        if self.spinning:
            return
            
        try:
            self.bet = int(self.bet_entry.get())
            if self.bet <= 0:
                self.result_label.config(text="Ставка має бути > 0")
                return
            if self.bet > balance:
                self.result_label.config(text="Недостатньо грошей")
                return
        except ValueError:
            self.result_label.config(text="Ставка має бути числом")
            return

        self.spinning = True
        self.spin_button.config(state=tk.DISABLED)
        self.frames = 10
        self.update_spin()

    def update_spin(self):
        global balance
        if self.frames > 0:
            for label in self.labels:
                label.config(text=random.choice(symbols))
            self.frames -= 1
            self.after(100, self.update_spin)
        else:
            self.spinning = False
            self.spin_button.config(state=tk.NORMAL)
            
            final = [random.choice(symbols) for _ in range(3)]
            for i, symbol in enumerate(final):
                self.labels[i].config(text=symbol)

            if final[0] == final[1] == final[2]:
                win = int(self.bet * 1.5)
                balance += win
                self.result_label.config(text=f"🎉 Виграш +{win} (x1.5)")
                threading.Thread(target=SoundPlayer.play_win).start()
            elif random.randint(1, 100) == 1:
                jackpot = self.bet * 10
                balance += jackpot
                self.result_label.config(text=f"💰 ДЖЕКПОТ! +{jackpot}")
                threading.Thread(target=SoundPlayer.play_jackpot).start()
            else:
                balance -= self.bet
                self.result_label.config(text=f"Програш -{self.bet}")
                threading.Thread(target=SoundPlayer.play_lose).start()
                
            self.balance_label.config(text=f"Баланс: {balance}")

class BackgroundFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        for i in range(6):
            self.grid_rowconfigure(i, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        tk.Label(self, text="Налаштування фону", 
                font=("Arial", 16))\
            .grid(row=0, column=0, pady=10)

        # Кнопки вибору кольору фону
        tk.Button(self, text="Обрати колір фону", 
                command=self.choose_bg_color,
                font=("Arial", 12),
                width=20)\
            .grid(row=1, column=0, pady=5)

        # Кнопка вибору зображення
        tk.Button(self, text="Обрати фонове зображення", 
                command=self.choose_image,
                font=("Arial", 12),
                width=20)\
            .grid(row=2, column=0, pady=5)

        # Кнопка скидання фону
        tk.Button(self, text="Скинути фон", 
                command=self.reset_background,
                font=("Arial", 12),
                width=20)\
            .grid(row=3, column=0, pady=5)

        # Кнопка вибору кольору тексту
        tk.Button(self, text="Обрати колір тексту", 
                command=self.choose_text_color,
                font=("Arial", 12),
                width=20)\
            .grid(row=4, column=0, pady=5)

        tk.Button(self, text="Назад", 
                command=lambda: controller.show_frame("MenuFrame"),
                font=("Arial", 12),
                width=15)\
            .grid(row=5, column=0, pady=20)

    def choose_bg_color(self):
        color = colorchooser.askcolor(title="Оберіть колір фону")[1]
        if color:
            self.controller.bg_color = color
            self.controller.bg_image_path = None
            self.controller.update_background()

    def choose_image(self):
        path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png;*.jpg;*.jpeg")]
        )
        if path:
            self.controller.bg_image_path = path
            self.controller.update_background()

    def reset_background(self):
        self.controller.bg_color = "#ffffff"
        self.controller.bg_image_path = None
        self.controller.update_background()

    def choose_text_color(self):
        color = colorchooser.askcolor(title="Оберіть колір тексту")[1]
        if color:
            self.controller.text_color = color
            self.controller.update_background()

if __name__ == "__main__":
    app = CasinoApp()
    app.mainloop()