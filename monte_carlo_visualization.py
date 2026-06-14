# Импортирую нужные библиотеки
import tkinter as tk
import math
import random
import time
from collections import deque


# Класс для хранения одной точки
class Point:
    def __init__(self, x, y, is_inside):
        self.x = x              
        self.y = y              
        self.is_inside = is_inside  


# Главный класс - мозг программы
class MonteCarloApp:
    def __init__(self):
        # Создаю главное окно программы
        self.window = tk.Tk()
        self.window.title("Метод Монте-Карло")
        self.window.geometry("750x700")          
        self.window.configure(bg="#1a1a2e")      
        self.window.minsize(600, 600)            
        
        # Счётчики для статистики
        self.total = 0          
        self.inside = 0         
        self.points_list = deque(maxlen=50000)   
        self.is_running = False  
        self.speed = 10         
        self.anim_id = None     
        
        # Размеры области рисования
        self.canvas_w = 500     
        self.canvas_h = 500     
        self.margin = 40        
        self.cx = self.canvas_w / 2   
        self.cy = self.canvas_h / 2   
        self.r = (self.canvas_w - 2 * self.margin) / 2  
        
        # Для подсчёта скорости точек в секунду
        self.fps_count = 0      
        self.fps_timer = time.time()  
        self.fps_value = 0      
        
        # Строим интерфейс и запускаем
        self.make_ui()          
        self.draw_field()      
        self.update_labels()    
    
    
    def make_ui(self):
        # Создание всего интерфейса, кнопок, надписей, canvas
        
        # Рамка для всех элементов
        main = tk.Frame(self.window, bg="#1a1a2e")
        main.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Заголовок программы
        title = tk.Label(main, text="Метод Монте-Карло", 
                        font=("Arial", 22, "bold"),
                        bg="#1a1a2e", fg="#e94560")
        title.pack(pady=(0, 3))
        
        # Подзаголовок
        sub = tk.Label(main, text="Вычисление числа Pi через случайные точки",
                      font=("Arial", 11), bg="#1a1a2e", fg="#a0a0b0")
        sub.pack(pady=(0, 12))
        
        # Рамка вокруг canvas для красоты
        canvas_border = tk.Frame(main, bg="#0f3460", bd=0, 
                                highlightbackground="#16213e", highlightthickness=3)
        canvas_border.pack(pady=5)
        
        # Сам canvas, на нём рисуем
        self.canvas = tk.Canvas(canvas_border, width=self.canvas_w, 
                               height=self.canvas_h, bg="#0a0a1a",
                               highlightthickness=0, bd=0)
        self.canvas.pack(padx=2, pady=2)
        
        # Панель со статистикой (5 блоков с цифрами)
        stats_frame = tk.Frame(main, bg="#1a1a2e")
        stats_frame.pack(fill=tk.X, pady=10)
        
        # Описание блоков статистики: (название, ключ, цвет цифр)
        blocks = [
            ("Всего точек", "total", "#e94560"),
            ("В круге", "inside", "#4ecca3"),
            ("Pi примерно", "pi", "#f0c040"),
            ("Ошибка", "error", "#ff6b6b"),
            ("Точек/сек", "fps", "#4ea8de"),
        ]
        
        # Словарь для быстрого доступа к цифрам (чтобы обновлять их)
        self.label_refs = {}
        
        # Создаю 5 блоков статистики в ряд
        for i, (text, key, clr) in enumerate(blocks):
            # Отдельная карточка для каждого показателя
            block = tk.Frame(stats_frame, bg="#16213e", bd=0,
                           highlightbackground="#0f3460", highlightthickness=1)
            block.grid(row=0, column=i, padx=5, pady=5, sticky="nsew")
            
            # Название показателя (мелкий шрифт)
            tk.Label(block, text=text, font=("Arial", 9),
                    bg="#16213e", fg="#a0a0b0").pack(pady=(6, 1))
            
            # Значение показателя (крупный шрифт)
            val = tk.Label(block, text="0", font=("Arial", 16, "bold"),
                          bg="#16213e", fg=clr)
            val.pack(pady=(0, 6))
            
            # Сохраняю ссылку на цифру в словарь
            self.label_refs[key] = val
        
        # Делаю все колонки одинаковой ширины
        for i in range(len(blocks)):
            stats_frame.grid_columnconfigure(i, weight=1)
        
        # Панель с кнопками управления
        ctrl = tk.Frame(main, bg="#1a1a2e")
        ctrl.pack(fill=tk.X, pady=8)
        
        # Кнопка запуска или паузы
        self.btn_start = tk.Button(ctrl, text="Запустить", 
                                   command=self.press_start,
                                   font=("Arial", 11, "bold"),
                                   bg="#e94560", fg="white",
                                   activebackground="#c23152",
                                   bd=0, padx=20, pady=8,
                                   cursor="hand2")
        self.btn_start.pack(side=tk.LEFT, padx=5)
        
        # Кнопка сброса
        tk.Button(ctrl, text="Сбросить", command=self.press_reset,
                 font=("Arial", 11, "bold"), bg="#533483", fg="white",
                 activebackground="#3b2560", bd=0, padx=20, pady=8,
                 cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        # Кнопка добавления 1000 точек
        tk.Button(ctrl, text="+1000 точек", command=self.add_1000,
                 font=("Arial", 10), bg="#0f3460", fg="white",
                 activebackground="#16213e", bd=0, padx=15, pady=8,
                 cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        # Ползунок скорости 
        speed_box = tk.Frame(ctrl, bg="#1a1a2e")
        speed_box.pack(side=tk.RIGHT, padx=5)
        
        tk.Label(speed_box, text="Скорость:", font=("Arial", 10),
                bg="#1a1a2e", fg="#a0a0b0").pack(side=tk.LEFT, padx=(0, 6))
        
        # Переменная для хранения значения ползунка
        self.speed_var = tk.IntVar(value=10)
        scale = tk.Scale(speed_box, from_=1, to=100, orient=tk.HORIZONTAL,
                        variable=self.speed_var, command=self.set_speed,
                        length=130, bg="#16213e", fg="white",
                        troughcolor="#0f3460", activebackground="#e94560",
                        highlightthickness=0, bd=0)
        scale.pack(side=tk.LEFT)
        
        # Цифра рядом с ползунком
        self.speed_display = tk.Label(speed_box, text="10",
                                      font=("Arial", 11, "bold"),
                                      bg="#1a1a2e", fg="#e94560", width=3)
        self.speed_display.pack(side=tk.LEFT, padx=(6, 0))
        
        # Формула метода Монте-Карло
        tk.Label(main, text="Pi = 4 * (точки в круге / всего точек)",
                font=("Arial", 9, "italic"), bg="#1a1a2e", fg="#606070"
                ).pack(pady=(8, 3))
        
        # Подсказка по горячим клавишам
        tk.Label(main, text="ПРОБЕЛ - старт/стоп | R - сброс | СТРЕЛКИ - скорость",
                font=("Arial", 8), bg="#1a1a2e", fg="#505060"
                ).pack(pady=(0, 3))
        
        # Привязываю клавиши к действиям
        self.window.bind("<space>", lambda e: self.press_start())   
        self.window.bind("<r>", lambda e: self.press_reset())       
        self.window.bind("<R>", lambda e: self.press_reset())       
        self.window.bind("<Up>", lambda e: self.change_speed(5))    
        self.window.bind("<Down>", lambda e: self.change_speed(-5)) 
        self.window.bind("<plus>", lambda e: self.add_1000())       
        self.window.bind("<equal>", lambda e: self.add_1000())      
    
    # Рисует квадрат, круг и оси координат 
    def draw_field(self):
        
        # Очищаю canvas
        self.canvas.delete("all")
        
        # Вычисляю границы квадрата
        left = self.cx - self.r     
        top = self.cy - self.r      
        right = self.cx + self.r    
        bottom = self.cy + self.r   
        
        # Рисую квадрат 
        self.canvas.create_rectangle(left, top, right, bottom,
                                     fill="#12122a", outline="#0f3460", width=2)
        
        # Рисую круг 
        self.canvas.create_oval(left, top, right, bottom,
                                fill="#1a1030", outline="#e94560", width=2)
        
        # Пунктирные оси координат
        dash = (6, 10)  
        
        # Горизонтальная ось 
        self.canvas.create_line(left, self.cy, right, self.cy,
                                fill="#1a1a40", width=1, dash=dash)
        
        # Вертикальная ось 
        self.canvas.create_line(self.cx, top, self.cx, bottom,
                                fill="#1a1a40", width=1, dash=dash)
        
        # Подпись начала координат 
        self.canvas.create_text(self.cx - 18, self.cy + 18,
                                text="(0,0)", fill="#707080", font=("Arial", 9))
        
        # Подпись радиуса
        self.canvas.create_text(self.cx + self.r * 0.55,
                                self.cy - self.r * 0.55,
                                text="R=1", fill="#e94560",
                                font=("Arial", 9, "italic"))
        
        # Перерисовываю все сохранённые точки поверх
        self.draw_saved_points()
    
    # Перерисовывает все точки из списка (после очистки canvas)
    def draw_saved_points(self):
        
        for pt in self.points_list:
            # Зелёный если внутри круга, красный если снаружи
            color = "#4ecca3" if pt.is_inside else "#ff6b6b"
            # Рисуем точку как маленький круг
            self.canvas.create_oval(pt.x - 1.5, pt.y - 1.5,
                                    pt.x + 1.5, pt.y + 1.5,
                                    fill=color, outline="")
    
    # Создаёт одну случайную точку и проверяет, попала ли она в круг
    def make_one_point(self):
        
        # Генерирую случайные координаты от -R до +R
        rx = (random.random() * 2 - 1) * self.r
        ry = (random.random() * 2 - 1) * self.r
        
        # Перевожу в экранные координаты
        sx = self.cx + rx
        sy = self.cy - ry
        
        # Вычисляю расстояние от точки до центра по теореме пифагора
        distance = math.sqrt(rx * rx + ry * ry)
        
        # Проверяю: точка внутри круга если расстояние <= радиус
        inside_circle = distance <= self.r
        
        # Обновляю счётчики
        self.total += 1
        if inside_circle:
            self.inside += 1
        
        # Сохраняю точку в список
        pt = Point(sx, sy, inside_circle)
        self.points_list.append(pt)
        
        # Рисую точку на canvas
        color = "#4ecca3" if inside_circle else "#ff6b6b"
        self.canvas.create_oval(sx - 1.5, sy - 1.5,
                                sx + 1.5, sy + 1.5,
                                fill=color, outline="")
        
        # Считаю для FPS
        self.fps_count += 1
    
    # Создаёт несколько точек и обновляет статистику
    def make_many_points(self, how_many):
        for _ in range(how_many):
            self.make_one_point()
        self.update_labels()
    
    # Мгновенно добавляет 1000 точек 
    def add_1000(self):
        was_active = self.is_running  
        if was_active:
            self.stop_anim()          
        
        self.make_many_points(1000)    
        
        if was_active:
            self.start_anim()          
    
    # Обновляет все цифры статистики на экране
    def update_labels(self):
        
        # Вычисляю pi и погрешность
        if self.total > 0:
            pi_now = 4 * self.inside / self.total
            # Сравниваю с настоящим pi и считаю ошибку в процентах
            mistake = abs(pi_now - math.pi) / math.pi * 100
        else:
            pi_now = 0
            mistake = 0
        
        # Обновляю fps каждую секунду
        now = time.time()
        if now - self.fps_timer >= 1.0:
            self.fps_value = self.fps_count
            self.fps_count = 0
            self.fps_timer = now
        
        # Записываю новые значения в метки на экране
        self.label_refs["total"].config(text=str(self.total))
        self.label_refs["inside"].config(text=str(self.inside))
        self.label_refs["pi"].config(text=f"{pi_now:.5f}")        # 5 знаков после запятой
        self.label_refs["error"].config(text=f"{mistake:.3f}%")   # 3 знака после запятой
        self.label_refs["fps"].config(text=str(self.fps_value))
        
        # Меняю цвет ошибки в зависимости от точности
        if mistake < 0.1:
            self.label_refs["error"].config(fg="#4ecca3")  
        elif mistake < 1.0:
            self.label_refs["error"].config(fg="#f0c040")  
        else:
            self.label_refs["error"].config(fg="#ff6b6b")  
        
        # Принудительно обновляю экран
        self.window.update_idletasks()
    
    # Один кадр анимации. Вызывается примерно 60 раз в секунду
    def do_frame(self):
        if not self.is_running:
            return  
        
        self.make_many_points(self.speed)
        
        self.anim_id = self.window.after(16, self.do_frame)
    
    # Запускает анимацию
    def start_anim(self):
        if self.is_running:
            return  
        
        self.is_running = True
        self.fps_timer = time.time()
        self.fps_count = 0
        
        self.btn_start.config(text="Пауза", bg="#f0a500")
        
        # Запускаю цикл анимации
        self.do_frame()
    
    # Останавливает анимацию
    def stop_anim(self):
        self.is_running = False
        
        if self.anim_id:
            self.window.after_cancel(self.anim_id)
            self.anim_id = None
        
        self.btn_start.config(text="Запустить", bg="#e94560")
    
    # Обработчик кнопки запуска и паузы
    def press_start(self):
        if self.is_running:
            self.stop_anim()
        else:
            self.start_anim()
    
    # Обработчик кнопки сброса
    def press_reset(self):
        self.stop_anim()
        self.total = 0
        self.inside = 0
        self.points_list.clear()  
        self.fps_value = 0
        self.fps_count = 0
        
        # Перерисовываю пустое поле
        self.draw_field()
        self.update_labels()
    
    # Обновляет скорость из ползунка
    def set_speed(self, *args):
        self.speed = self.speed_var.get()
        self.speed_display.config(text=str(self.speed))
    
    # Меняет скорость на delta единиц, для стрелок клавиатуры
    def change_speed(self, delta):
        new_val = self.speed + delta
        if new_val < 1:
            new_val = 1
        if new_val > 100:
            new_val = 100
        self.speed_var.set(new_val)
        self.set_speed()
    
    # Запускает главный цикл программы
    def run(self):
        self.window.mainloop()


# Точка входа
if __name__ == "__main__":
    app = MonteCarloApp()
    app.run()