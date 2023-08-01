import tkinter as tk
import threading
import time
import datetime as dt
import pyautogui
import random
import os
import io
import pystray
from PIL import Image, ImageTk

# Variável global para o menu da bandeja do sistema
estado_atual = None
tray_icon    = None
entry_state  = None

def change_state():
    global estado_atual

    if btn_state.get():
        estado_atual = "Desativado"
        btn_color_bg.set("red")
        btn_color_text.set("white")
        stop_function()
    else:
        if (timeEntry.get() == ''):
            btn_color_bg.set("gray")
            estado_atual = None
        else:
            estado_atual = "Ativado"
            start_function()
        btn_color_text.set("black")
    
    canvas.itemconfig(text_item, text=btn_text.get(), fill=btn_color_text.get())
    canvas.itemconfig(start_button, fill=btn_color_bg.get())
    create_systray_icon("icone.png", update=True)

def change_option_icon(state):
    global estado_atual
    
    if state:
        estado_atual = "Desativado"
    else:
        estado_atual = None
    create_systray_icon("icone.png", update=True)
       
def start_function():
    btn_state.set(True)
    btn_text.set("Ativado")
    btn_color_bg.set("green")
    btn_color_text.set("black")
    timeEntry.config(state = tk.DISABLED)
    # Iniciar a função em um thread separado
    threading.Thread(target=running_function, args=(is_running,)).start()

def stop_function():
    btn_state.set(False)
    btn_text.set("Desativado")
    btn_color_bg.set("red")
    btn_color_text.set("white")
    timeEntry.config(state=tk.NORMAL)

def running_function(is_running):
    data_atual = dt.datetime.now()
    diff_set = int(timeEntry.get())
    
    while is_running and btn_state.get():
        x_before, y_before = pyautogui.position()
        diff_atual = int( (dt.datetime.now() - data_atual).total_seconds() )

        if ( (diff_set - diff_atual) <= 0 ):
            x_after, y_after = pyautogui.position()
            if is_running and btn_state.get() and x_before == x_after and y_before == y_after:
                x_rand = random.randint(-100, 100)
                y_rand = random.randint(-100, 100)
                pyautogui.moveTo(x_after + x_rand, y_after + y_rand, duration=1)
                data_atual = dt.datetime.now()
                data_format = data_atual.strftime('%d/%m/%Y %H:%M:%S')
                text_ult_att.set(data_format)
                blockText.itemconfig(ultAtt, text=f"Ult. Att: {text_ult_att.get()}")

def on_exit(icon, item):
    global is_running
    is_running = False
    change_state()  # Adicionado para parar a função running_function quando o sistema é fechado sem parar a execução
    icon.stop()
    root.destroy()

def on_key_release(event):
    global entry_state
    
    text = timeEntry.get()
    boolEntry = bool(text)
    if not(btn_state.get()):       
        if (len(text) > 0):
            btn_color_bg.set("red")
            btn_color_text.set("white") 
        else:
            btn_color_bg.set("gray")
            btn_color_text.set("black")

    if (boolEntry != entry_state):
        entry_state = boolEntry
        change_option_icon(boolEntry)
    
    canvas.itemconfig(start_button, fill=btn_color_bg.get())
    canvas.itemconfig(text_item, fill=btn_color_text.get())

def on_validate_input(new_text):
    if new_text.isdigit() or new_text == "":
        return True
    else:
        return False

def on_close():
    root.withdraw()

def on_restore(icon, item):
    root.deiconify()

def create_systray_icon(icon_name, update=False):
    global tray_icon

    script_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(script_dir, "Images", icon_name)

    if os.path.exists(icon_path):
        with open(icon_path, "rb") as f:
            image_bytes = f.read()

        # Função para criar o ícone da bandeja do sistema na thread secundária
        def create_tray_icon():
            global tray_icon

            if update and tray_icon:
                tray_icon.stop()

            # Cria o ícone da bandeja do sistema usando a biblioteca pystray
            icon = Image.open(io.BytesIO(image_bytes))
            menu = pystray.Menu(pystray.MenuItem("Abrir", on_restore), 
                                pystray.MenuItem("Ativar", change_state, visible=(estado_atual=="Desativado")),
                                pystray.MenuItem("Desativar", change_state, visible=(estado_atual=="Ativado")),
                                pystray.MenuItem("Sair", on_exit))

            tray_icon = pystray.Icon("MouseLoop", icon, "MouseLoop", menu)
            tray_icon.run()

        # Cria a thread para criar o ícone da bandeja do sistema
        tray_thread = threading.Thread(target=create_tray_icon)
        tray_thread.daemon = True
        tray_thread.start()

# Cria a janela principal
root = tk.Tk()
root.title("MouseLoop")
root.geometry(f'{250}x{175}')
root.resizable(False, False)
root.withdraw()

current_directory = os.path.dirname(__file__)
icon_path = os.path.join(current_directory, "Images", "icone.ico")
icon_image = Image.open(icon_path)
icon_photo = ImageTk.PhotoImage(icon_image)
root.iconbitmap(icon_path)

# Configura o evento para minimizar ao clicar no botão de fechar (X)
root.protocol("WM_DELETE_WINDOW", on_close)

# Variável para controlar a execução do programa
is_running = True

#Declarando as configurações do botão
btn_text = tk.StringVar()
btn_text.set("Desativado")
btn_state = tk.BooleanVar()
btn_state.set(False)
btn_color_text = tk.StringVar()
btn_color_text.set("black")
btn_color_bg = tk.StringVar()
btn_color_bg.set("red")

data_atual = dt.datetime.now()
data_atual = data_atual.strftime('%d/%m/%Y %H:%M:%S')
text_ult_att = tk.StringVar()
text_ult_att.set(data_atual)

# Gerando botão circular
canvas = tk.Canvas(root, width=100, height=100)
canvas.pack()

timeLabel = tk.Label(root, text="Tempo de espera de Execução (seg):")
timeLabel.pack()

validation = root.register(on_validate_input)

timeEntry = tk.Entry(root, validate="key", validatecommand=(validation, "%P"))
timeEntry.pack()

timeEntry.bind("<KeyRelease>", on_key_release)

blockText = tk.Canvas(root, width=250, height=100)
blockText.pack()

if (timeEntry.get() == ''):
    btn_color_bg.set("gray")

start_button = canvas.create_oval(10,10,90,90, fill=btn_color_bg.get(), outline="black")
text_item = canvas.create_text(50, 50, text=btn_text.get(), fill=btn_color_text.get())

canvas.tag_bind(start_button, "<Button-1>", lambda event: change_state())
canvas.tag_bind(text_item, "<Button-1>", lambda event: change_state())

ultAtt = blockText.create_text(125, 20, text = f"Ult. Att: {text_ult_att.get()}", fill="black")

def update_gui():
    # Loop para atualizar a GUI enquanto a aplicação está em execução
    while is_running:
        try:
            root.update()
        except tk.TclError:
            # A exceção é lançada quando a janela é fechada
            break
        time.sleep(0.01)  # Intervalo de atualização de 10 ms

# Cria a thread para o ícone da bandeja do sistema
tray_thread = threading.Thread(target=create_systray_icon, args=("icone.png",False))
tray_thread.daemon = True
tray_thread.start()

# Inicia o loop da aplicação na thread principal
root.after(0, update_gui)
root.mainloop()