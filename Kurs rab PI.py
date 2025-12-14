import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import sqlite3
import hashlib
import os
import json
from datetime import datetime
import random

class JobFinderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("JobFinder - Поиск работы и персонала")
        self.root.geometry("1200x700")
        self.root.configure(bg='#f0f2f5')
        
        # Цветовая схема
        self.colors = {
            'primary': '#4361ee',
            'secondary': '#3a0ca3',
            'accent': '#7209b7',
            'success': '#4cc9f0',
            'danger': '#f72585',
            'light': '#f8f9fa',
            'dark': '#212529',
            'gray': '#6c757d',
            'white': '#ffffff'
        }
        
        # Стиль для ttk
        self.setup_styles()
        
        # Текущий пользователь
        self.current_user = None
        self.user_type = None
        
        # База данных
        self.init_database()
        
        # Загрузка тестовых данных
        self.load_sample_data()
        
        # Запуск стартового экрана
        self.show_start_screen()
    
    def setup_styles(self):
        """Настройка стилей для виджетов"""
        style = ttk.Style()
        
        # Настраиваем стили для кнопок
        style.configure('Primary.TButton', 
                       background=self.colors['primary'],
                       foreground=self.colors['white'],
                       padding=10,
                       font=('Segoe UI', 10, 'bold'))
        
        style.configure('Secondary.TButton',
                       background=self.colors['secondary'],
                       foreground=self.colors['white'],
                       padding=8,
                       font=('Segoe UI', 9))
        
        style.configure('Accent.TButton',
                       background=self.colors['accent'],
                       foreground=self.colors['white'],
                       padding=8,
                       font=('Segoe UI', 9))
        
        style.configure('Success.TButton',
                       background=self.colors['success'],
                       foreground=self.colors['dark'],
                       padding=8,
                       font=('Segoe UI', 9))
        
        style.configure('Danger.TButton',
                       background=self.colors['danger'],
                       foreground=self.colors['white'],
                       padding=8,
                       font=('Segoe UI', 9))
        
        # Стиль для рамок
        style.configure('Card.TFrame',
                       background=self.colors['white'],
                       relief='raised',
                       borderwidth=2)
        
        style.configure('Light.TFrame',
                       background=self.colors['light'])
    
    def init_database(self):
        """Инициализация базы данных"""
        self.conn = sqlite3.connect('jobfinder.db', check_same_thread=False)
        self.cursor = self.conn.cursor()
        
        # Создание таблиц
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                user_type TEXT NOT NULL,
                first_name TEXT,
                last_name TEXT,
                phone TEXT,
                city TEXT,
                company_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS resumes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                desired_position TEXT,
                salary_expectation INTEGER,
                experience TEXT,
                education TEXT,
                skills TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS vacancies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employer_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                requirements TEXT,
                salary_from INTEGER,
                salary_to INTEGER,
                employment_type TEXT,
                city TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (employer_id) REFERENCES users (id)
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resume_id INTEGER NOT NULL,
                vacancy_id INTEGER NOT NULL,
                cover_letter TEXT,
                status TEXT DEFAULT 'pending',
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (resume_id) REFERENCES resumes (id),
                FOREIGN KEY (vacancy_id) REFERENCES vacancies (id)
            )
        ''')
        
        self.conn.commit()
    
    def load_sample_data(self):
        """Загрузка тестовых данных"""
        # Проверяем, есть ли уже вакансии
        self.cursor.execute("SELECT COUNT(*) FROM vacancies")
        if self.cursor.fetchone()[0] == 0:
            # Добавляем тестовые вакансии
            sample_vacancies = [
                ("Python Developer", "Разработка backend-части веб-приложений", "Опыт работы от 1 года, знание Django/Flask", 120000, 200000, "full_time", "Москва"),
                ("Frontend Developer", "Создание пользовательских интерфейсов", "Знание React/Vue.js, опыт от 2 лет", 100000, 180000, "full_time", "Санкт-Петербург"),
                ("Data Analyst", "Анализ данных, построение отчетов", "SQL, Python, Excel, опыт от 1 года", 80000, 150000, "full_time", "Новосибирск"),
                ("UX/UI Designer", "Дизайн интерфейсов мобильных и веб-приложений", "Figma, Adobe XD, опыт от 2 лет", 90000, 160000, "full_time", "Екатеринбург"),
                ("DevOps Engineer", "Настройка и поддержка инфраструктуры", "Docker, Kubernetes, AWS, опыт от 3 лет", 150000, 250000, "full_time", "Москва"),
                ("Project Manager", "Управление IT-проектами", "Опыт управления командами от 3 лет", 130000, 220000, "full_time", "Казань"),
                ("QA Engineer", "Тестирование программного обеспечения", "Опыт тестирования от 1 года", 70000, 130000, "full_time", "Москва"),
                ("System Administrator", "Администрирование IT-инфраструктуры", "Linux, Windows Server, сетевые технологии", 60000, 120000, "full_time", "Ростов-на-Дону"),
                ("Mobile Developer", "Разработка мобильных приложений", "Kotlin/Swift или React Native/Flutter", 110000, 190000, "full_time", "Санкт-Петербург"),
                ("Marketing Manager", "Разработка и реализация маркетинговых стратегий", "Опыт в digital-маркетинге от 2 лет", 90000, 160000, "full_time", "Москва"),
                ("Backend Developer", "Разработка серверной логики", "Node.js/Python/Java, опыт от 2 лет", 130000, 220000, "remote", "Удаленно"),
                ("Data Scientist", "Построение ML-моделей", "Python, ML-библиотеки, опыт от 2 лет", 140000, 250000, "hybrid", "Москва"),
                ("HR Specialist", "Подбор IT-персонала", "Опыт рекрутинга в IT от 2 лет", 70000, 130000, "full_time", "Москва"),
                ("SEO Specialist", "Продвижение сайтов в поисковых системах", "Опыт SEO-оптимизации от 1.5 лет", 60000, 120000, "remote", "Удаленно"),
                ("Content Manager", "Создание и редактирование контента", "Копирайтинг, редактура, SMM", 50000, 100000, "part_time", "Санкт-Петербург")
            ]
            
            # Создаем тестового работодателя
            self.cursor.execute("""
                INSERT OR IGNORE INTO users (email, password_hash, user_type, company_name) 
                VALUES (?, ?, ?, ?)
            """, ('employer@test.com', self.hash_password('123'), 'employer', 'IT Solutions Inc.'))
            
            employer_id = self.cursor.lastrowid
            
            # Добавляем вакансии
            for vacancy in sample_vacancies:
                self.cursor.execute("""
                    INSERT INTO vacancies (employer_id, title, description, requirements, 
                                         salary_from, salary_to, employment_type, city)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (employer_id, *vacancy))
            
            self.conn.commit()
    
    def hash_password(self, password):
        """Хеширование пароля"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def show_start_screen(self):
        """Показать стартовый экран"""
        self.clear_window()
        
        # Основной фрейм
        main_frame = tk.Frame(self.root, bg=self.colors['light'])
        main_frame.pack(fill='both', expand=True)
        
        # Заголовок
        title_frame = tk.Frame(main_frame, bg=self.colors['primary'])
        title_frame.pack(fill='x', pady=(0, 50))
        
        title_label = tk.Label(title_frame, text="JobFinder", 
                               font=('Segoe UI', 36, 'bold'),
                               fg=self.colors['white'],
                               bg=self.colors['primary'],
                               pady=30)
        title_label.pack()
        
        subtitle_label = tk.Label(title_frame, 
                                 text="Найди работу или персонал мечты",
                                 font=('Segoe UI', 16),
                                 fg=self.colors['light'],
                                 bg=self.colors['primary'])
        subtitle_label.pack()
        
        # Контейнер для кнопок
        buttons_frame = tk.Frame(main_frame, bg=self.colors['light'])
        buttons_frame.pack(expand=True)
        
        # Кнопка "Я соискатель"
        seeker_btn = tk.Button(buttons_frame, 
                              text="🔍 Я СОИСКАТЕЛЬ\nИщу работу",
                              font=('Segoe UI', 18, 'bold'),
                              bg=self.colors['accent'],
                              fg='white',
                              width=25,
                              height=3,
                              cursor='hand2',
                              command=lambda: self.show_login_screen('seeker'))
        seeker_btn.pack(pady=20)
        
        # Кнопка "Я работодатель"
        employer_btn = tk.Button(buttons_frame,
                                text="💼 Я РАБОТОДАТЕЛЬ\nИщу сотрудников",
                                font=('Segoe UI', 18, 'bold'),
                                bg=self.colors['secondary'],
                                fg='white',
                                width=25,
                                height=3,
                                cursor='hand2',
                                command=lambda: self.show_login_screen('employer'))
        employer_btn.pack(pady=20)
        
        # Информация о проекте
        info_frame = tk.Frame(main_frame, bg=self.colors['light'])
        info_frame.pack(pady=50)
        
        info_text = """
        JobFinder - современная платформа для поиска работы и подбора персонала.
        • Создавайте профессиональные резюме
        • Найдите идеальную вакансию
        • Управляйте откликами
        • Находите лучших кандидатов
        """
        
        info_label = tk.Label(info_frame, text=info_text,
                             font=('Segoe UI', 10),
                             fg=self.colors['dark'],
                             bg=self.colors['light'],
                             justify='left')
        info_label.pack()
    
    def show_login_screen(self, user_type):
        """Показать экран входа"""
        self.clear_window()
        
        main_frame = tk.Frame(self.root, bg=self.colors['light'])
        main_frame.pack(fill='both', expand=True)
        
        # Заголовок
        title = "Вход для соискателя" if user_type == 'seeker' else "Вход для работодателя"
        title_frame = tk.Frame(main_frame, bg=self.colors['primary'])
        title_frame.pack(fill='x', pady=(0, 30))
        
        title_label = tk.Label(title_frame, text=title,
                              font=('Segoe UI', 24, 'bold'),
                              fg=self.colors['white'],
                              bg=self.colors['primary'],
                              pady=20)
        title_label.pack()
        
        # Форма входа
        form_frame = tk.Frame(main_frame, bg=self.colors['white'],
                             relief='groove', borderwidth=2)
        form_frame.pack(pady=20, padx=100)
        
        tk.Label(form_frame, text="Email:", 
                font=('Segoe UI', 12),
                bg=self.colors['white']).grid(row=0, column=0, padx=20, pady=20, sticky='w')
        
        email_entry = tk.Entry(form_frame, font=('Segoe UI', 12), width=30)
        email_entry.grid(row=0, column=1, padx=20, pady=20)
        
        tk.Label(form_frame, text="Пароль:",
                font=('Segoe UI', 12),
                bg=self.colors['white']).grid(row=1, column=0, padx=20, pady=20, sticky='w')
        
        password_entry = tk.Entry(form_frame, font=('Segoe UI', 12), 
                                 width=30, show='*')
        password_entry.grid(row=1, column=1, padx=20, pady=20)
        
        # Кнопки
        button_frame = tk.Frame(form_frame, bg=self.colors['white'])
        button_frame.grid(row=2, column=0, columnspan=2, pady=30)
        
        login_btn = tk.Button(button_frame, text="Войти",
                             font=('Segoe UI', 12, 'bold'),
                             bg=self.colors['success'],
                             fg=self.colors['dark'],
                             width=15,
                             command=lambda: self.login(user_type, email_entry.get(), password_entry.get()))
        login_btn.pack(side='left', padx=10)
        
        register_btn = tk.Button(button_frame, text="Регистрация",
                                font=('Segoe UI', 12),
                                bg=self.colors['primary'],
                                fg='white',
                                width=15,
                                command=lambda: self.show_register_screen(user_type))
        register_btn.pack(side='left', padx=10)
        
        back_btn = tk.Button(button_frame, text="Назад",
                            font=('Segoe UI', 12),
                            bg=self.colors['gray'],
                            fg='white',
                            width=15,
                            command=self.show_start_screen)
        back_btn.pack(side='left', padx=10)
        
        # Тестовые учетные данные
        test_frame = tk.Frame(main_frame, bg=self.colors['light'])
        test_frame.pack(pady=20)
        
        test_text = "Тестовые данные: seeker@test.com / 123 или employer@test.com / 123"
        tk.Label(test_frame, text=test_text,
                font=('Segoe UI', 10),
                fg=self.colors['gray'],
                bg=self.colors['light']).pack()
    
    def show_register_screen(self, user_type):
        """Показать экран регистрации"""
        self.clear_window()
        
        main_frame = tk.Frame(self.root, bg=self.colors['light'])
        main_frame.pack(fill='both', expand=True)
        
        title = "Регистрация соискателя" if user_type == 'seeker' else "Регистрация работодателя"
        title_frame = tk.Frame(main_frame, bg=self.colors['primary'])
        title_frame.pack(fill='x', pady=(0, 30))
        
        title_label = tk.Label(title_frame, text=title,
                              font=('Segoe UI', 24, 'bold'),
                              fg=self.colors['white'],
                              bg=self.colors['primary'],
                              pady=20)
        title_label.pack()
        
        # Форма регистрации
        form_frame = tk.Frame(main_frame, bg=self.colors['white'],
                             relief='groove', borderwidth=2)
        form_frame.pack(pady=20, padx=50)
        
        row = 0
        
        if user_type == 'seeker':
            tk.Label(form_frame, text="Имя:",
                    font=('Segoe UI', 12),
                    bg=self.colors['white']).grid(row=row, column=0, padx=20, pady=10, sticky='w')
            first_name_entry = tk.Entry(form_frame, font=('Segoe UI', 12), width=30)
            first_name_entry.grid(row=row, column=1, padx=20, pady=10)
            row += 1
            
            tk.Label(form_frame, text="Фамилия:",
                    font=('Segoe UI', 12),
                    bg=self.colors['white']).grid(row=row, column=0, padx=20, pady=10, sticky='w')
            last_name_entry = tk.Entry(form_frame, font=('Segoe UI', 12), width=30)
            last_name_entry.grid(row=row, column=1, padx=20, pady=10)
            row += 1
        else:
            tk.Label(form_frame, text="Название компании:",
                    font=('Segoe UI', 12),
                    bg=self.colors['white']).grid(row=row, column=0, padx=20, pady=10, sticky='w')
            company_entry = tk.Entry(form_frame, font=('Segoe UI', 12), width=30)
            company_entry.grid(row=row, column=1, padx=20, pady=10)
            row += 1
        
        tk.Label(form_frame, text="Email:",
                font=('Segoe UI', 12),
                bg=self.colors['white']).grid(row=row, column=0, padx=20, pady=10, sticky='w')
        email_entry = tk.Entry(form_frame, font=('Segoe UI', 12), width=30)
        email_entry.grid(row=row, column=1, padx=20, pady=10)
        row += 1
        
        tk.Label(form_frame, text="Пароль:",
                font=('Segoe UI', 12),
                bg=self.colors['white']).grid(row=row, column=0, padx=20, pady=10, sticky='w')
        password_entry = tk.Entry(form_frame, font=('Segoe UI', 12), width=30, show='*')
        password_entry.grid(row=row, column=1, padx=20, pady=10)
        row += 1
        
        tk.Label(form_frame, text="Подтвердите пароль:",
                font=('Segoe UI', 12),
                bg=self.colors['white']).grid(row=row, column=0, padx=20, pady=10, sticky='w')
        confirm_password_entry = tk.Entry(form_frame, font=('Segoe UI', 12), width=30, show='*')
        confirm_password_entry.grid(row=row, column=1, padx=20, pady=10)
        row += 1
        
        # Кнопки
        button_frame = tk.Frame(form_frame, bg=self.colors['white'])
        button_frame.grid(row=row, column=0, columnspan=2, pady=30)
        
        if user_type == 'seeker':
            register_callback = lambda: self.register(
                user_type, email_entry.get(), password_entry.get(),
                confirm_password_entry.get(), first_name=first_name_entry.get(),
                last_name=last_name_entry.get()
            )
        else:
            register_callback = lambda: self.register(
                user_type, email_entry.get(), password_entry.get(),
                confirm_password_entry.get(), company_name=company_entry.get()
            )
        
        register_btn = tk.Button(button_frame, text="Зарегистрироваться",
                                font=('Segoe UI', 12, 'bold'),
                                bg=self.colors['success'],
                                fg=self.colors['dark'],
                                width=20,
                                command=register_callback)
        register_btn.pack(side='left', padx=10)
        
        back_btn = tk.Button(button_frame, text="Назад",
                            font=('Segoe UI', 12),
                            bg=self.colors['gray'],
                            fg='white',
                            width=20,
                            command=lambda: self.show_login_screen(user_type))
        back_btn.pack(side='left', padx=10)
    
    def login(self, user_type, email, password):
        """Вход в систему"""
        if not email or not password:
            messagebox.showerror("Ошибка", "Заполните все поля")
            return
        
        password_hash = self.hash_password(password)
        
        self.cursor.execute("""
            SELECT id, user_type, first_name, last_name, company_name 
            FROM users 
            WHERE email = ? AND password_hash = ?
        """, (email, password_hash))
        
        user = self.cursor.fetchone()
        
        if user:
            self.current_user = {
                'id': user[0],
                'user_type': user[1],
                'name': user[2] or user[4] or 'Пользователь'
            }
            
            if user[1] != user_type:
                messagebox.showerror("Ошибка", "Неверный тип учетной записи")
                return
            
            # Показываем соответствующий интерфейс
            if user_type == 'seeker':
                self.show_seeker_interface()
            else:
                self.show_employer_interface()
        else:
            messagebox.showerror("Ошибка", "Неверный email или пароль")
    
    def register(self, user_type, email, password, confirm_password, **kwargs):
        """Регистрация нового пользователя"""
        if not email or not password:
            messagebox.showerror("Ошибка", "Заполните все обязательные поля")
            return
        
        if password != confirm_password:
            messagebox.showerror("Ошибка", "Пароли не совпадают")
            return
        
        if len(password) < 3:
            messagebox.showerror("Ошибка", "Пароль должен содержать минимум 3 символа")
            return
        
        try:
            password_hash = self.hash_password(password)
            
            if user_type == 'seeker':
                self.cursor.execute("""
                    INSERT INTO users (email, password_hash, user_type, first_name, last_name)
                    VALUES (?, ?, ?, ?, ?)
                """, (email, password_hash, user_type, 
                      kwargs.get('first_name', ''), kwargs.get('last_name', '')))
            else:
                self.cursor.execute("""
                    INSERT INTO users (email, password_hash, user_type, company_name)
                    VALUES (?, ?, ?, ?)
                """, (email, password_hash, user_type, kwargs.get('company_name', '')))
            
            self.conn.commit()
            messagebox.showinfo("Успех", "Регистрация прошла успешно!")
            self.show_login_screen(user_type)
            
        except sqlite3.IntegrityError:
            messagebox.showerror("Ошибка", "Пользователь с таким email уже существует")
    
    def show_seeker_interface(self):
        """Показать интерфейс соискателя"""
        self.clear_window()
        
        # Основной контейнер
        main_container = tk.Frame(self.root, bg=self.colors['light'])
        main_container.pack(fill='both', expand=True)
        
        # Боковая панель
        sidebar = tk.Frame(main_container, bg=self.colors['dark'], width=250)
        sidebar.pack(side='left', fill='y')
        sidebar.pack_propagate(False)
        
        # Заголовок в сайдбаре
        tk.Label(sidebar, text=f"👤 {self.current_user['name']}", 
                font=('Segoe UI', 14, 'bold'),
                fg=self.colors['white'],
                bg=self.colors['dark'],
                pady=20).pack(fill='x')
        
        # Меню навигации
        nav_items = [
            ("📋 Лента вакансий", self.show_vacancy_feed),
            ("🔍 Поиск вакансий", self.show_vacancy_search),
            ("📄 Мое резюме", self.show_my_resume),
            ("📨 Мои отклики", self.show_my_applications),
            ("⭐ Избранное", self.show_favorites),
            ("⚙️ Профиль", self.show_seeker_profile),
            ("🚪 Выйти", self.logout)
        ]
        
        for text, command in nav_items:
            btn = tk.Button(sidebar, text=text,
                          font=('Segoe UI', 11),
                          bg=self.colors['dark'],
                          fg=self.colors['light'],
                          anchor='w',
                          relief='flat',
                          cursor='hand2',
                          command=command)
            btn.pack(fill='x', padx=10, pady=5)
        
        # Основная область
        self.main_content = tk.Frame(main_container, bg=self.colors['white'])
        self.main_content.pack(side='right', fill='both', expand=True)
        
        # Показываем ленту вакансий по умолчанию
        self.show_vacancy_feed()
    
    def show_employer_interface(self):
        """Показать интерфейс работодателя"""
        self.clear_window()
        
        main_container = tk.Frame(self.root, bg=self.colors['light'])
        main_container.pack(fill='both', expand=True)
        
        # Боковая панель
        sidebar = tk.Frame(main_container, bg=self.colors['secondary'], width=250)
        sidebar.pack(side='left', fill='y')
        sidebar.pack_propagate(False)
        
        tk.Label(sidebar, text=f"🏢 {self.current_user['name']}", 
                font=('Segoe UI', 14, 'bold'),
                fg=self.colors['white'],
                bg=self.colors['secondary'],
                pady=20).pack(fill='x')
        
        nav_items = [
            ("📋 Мои вакансии", self.show_my_vacancies),
            ("➕ Создать вакансию", self.show_create_vacancy),
            ("📨 Отклики", self.show_employer_applications),
            ("🔍 Поиск резюме", self.show_resume_search),
            ("📊 Статистика", self.show_statistics),
            ("⚙️ Профиль компании", self.show_employer_profile),
            ("🚪 Выйти", self.logout)
        ]
        
        for text, command in nav_items:
            btn = tk.Button(sidebar, text=text,
                          font=('Segoe UI', 11),
                          bg=self.colors['secondary'],
                          fg=self.colors['light'],
                          anchor='w',
                          relief='flat',
                          cursor='hand2',
                          command=command)
            btn.pack(fill='x', padx=10, pady=5)
        
        self.main_content = tk.Frame(main_container, bg=self.colors['white'])
        self.main_content.pack(side='right', fill='both', expand=True)
        
        self.show_my_vacancies()
    
    def show_vacancy_feed(self):
        """Показать ленту вакансий"""
        self.clear_main_content()
        
        # Заголовок
        header_frame = tk.Frame(self.main_content, bg=self.colors['primary'], height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="💼 Лента вакансий",
                font=('Segoe UI', 20, 'bold'),
                fg=self.colors['white'],
                bg=self.colors['primary']).pack(expand=True)
        
        # Контейнер для вакансий
        content_frame = tk.Frame(self.main_content, bg=self.colors['light'])
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Получаем вакансии из базы данных
        self.cursor.execute("""
            SELECT v.id, v.title, v.description, v.salary_from, v.salary_to, 
                   v.city, v.employment_type, u.company_name, v.created_at
            FROM vacancies v
            JOIN users u ON v.employer_id = u.id
            WHERE v.is_active = 1
            ORDER BY v.created_at DESC
            LIMIT 20
        """)
        
        vacancies = self.cursor.fetchall()
        
        if not vacancies:
            tk.Label(content_frame, text="Нет доступных вакансий",
                    font=('Segoe UI', 16),
                    fg=self.colors['gray'],
                    bg=self.colors['light']).pack(pady=50)
            return
        
        # Создаем скроллируемый фрейм
        canvas = tk.Canvas(content_frame, bg=self.colors['light'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(content_frame, orient='vertical', command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['light'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Отображаем вакансии
        for i, vacancy in enumerate(vacancies):
            vac_frame = tk.Frame(scrollable_frame, bg=self.colors['white'],
                                relief='groove', borderwidth=1)
            vac_frame.pack(fill='x', padx=10, pady=10, ipady=10)
            
            # Заголовок и зарплата
            title_frame = tk.Frame(vac_frame, bg=self.colors['white'])
            title_frame.pack(fill='x', padx=20, pady=(10, 5))
            
            tk.Label(title_frame, text=vacancy[1], 
                    font=('Segoe UI', 16, 'bold'),
                    fg=self.colors['dark'],
                    bg=self.colors['white'],
                    anchor='w').pack(side='left')
            
            salary_text = f"💰 {vacancy[3]:,} - {vacancy[4]:,} руб."
            tk.Label(title_frame, text=salary_text,
                    font=('Segoe UI', 14),
                    fg=self.colors['success'],
                    bg=self.colors['white']).pack(side='right')
            
            # Компания и локация
            info_frame = tk.Frame(vac_frame, bg=self.colors['white'])
            info_frame.pack(fill='x', padx=20, pady=5)
            
            tk.Label(info_frame, text=f"🏢 {vacancy[7]}",
                    font=('Segoe UI', 12),
                    fg=self.colors['gray'],
                    bg=self.colors['white']).pack(side='left')
            
            location_text = f"📍 {vacancy[5]} • {self.get_employment_type(vacancy[6])}"
            tk.Label(info_frame, text=location_text,
                    font=('Segoe UI', 12),
                    fg=self.colors['gray'],
                    bg=self.colors['white']).pack(side='right')
            
            # Описание
            description = vacancy[2][:200] + "..." if len(vacancy[2]) > 200 else vacancy[2]
            tk.Label(vac_frame, text=description,
                    font=('Segoe UI', 11),
                    fg=self.colors['dark'],
                    bg=self.colors['white'],
                    wraplength=800,
                    justify='left',
                    anchor='w').pack(fill='x', padx=20, pady=10)
            
            # Кнопки действий
            button_frame = tk.Frame(vac_frame, bg=self.colors['white'])
            button_frame.pack(fill='x', padx=20, pady=(5, 10))
            
            details_btn = tk.Button(button_frame, text="Подробнее",
                                   font=('Segoe UI', 10),
                                   bg=self.colors['primary'],
                                   fg='white',
                                   cursor='hand2',
                                   command=lambda v=vacancy: self.show_vacancy_details(v))
            details_btn.pack(side='left', padx=5)
            
            apply_btn = tk.Button(button_frame, text="Откликнуться",
                                 font=('Segoe UI', 10, 'bold'),
                                 bg=self.colors['success'],
                                 fg=self.colors['dark'],
                                 cursor='hand2',
                                 command=lambda v=vacancy: self.apply_to_vacancy(v[0]))
            apply_btn.pack(side='left', padx=5)
            
            favorite_btn = tk.Button(button_frame, text="⭐ В избранное",
                                    font=('Segoe UI', 10),
                                    bg=self.colors['accent'],
                                    fg='white',
                                    cursor='hand2')
            favorite_btn.pack(side='left', padx=5)
        
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
    
    def show_vacancy_search(self):
        """Показать поиск вакансий"""
        self.clear_main_content()
        
        header_frame = tk.Frame(self.main_content, bg=self.colors['primary'], height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="🔍 Поиск вакансий",
                font=('Segoe UI', 20, 'bold'),
                fg=self.colors['white'],
                bg=self.colors['primary']).pack(expand=True)
        
        # Панель фильтров
        filter_frame = tk.Frame(self.main_content, bg=self.colors['white'],
                               relief='groove', borderwidth=1)
        filter_frame.pack(fill='x', padx=20, pady=20)
        
        tk.Label(filter_frame, text="Ключевые слова:",
                font=('Segoe UI', 12),
                bg=self.colors['white']).grid(row=0, column=0, padx=10, pady=10, sticky='w')
        
        keyword_entry = tk.Entry(filter_frame, font=('Segoe UI', 12), width=30)
        keyword_entry.grid(row=0, column=1, padx=10, pady=10)
        
        tk.Label(filter_frame, text="Город:",
                font=('Segoe UI', 12),
                bg=self.colors['white']).grid(row=0, column=2, padx=10, pady=10, sticky='w')
        
        cities = ['Любой', 'Москва', 'Санкт-Петербург', 'Новосибирск', 'Екатеринбург', 
                 'Казань', 'Удаленно']
        city_combo = ttk.Combobox(filter_frame, values=cities, width=15)
        city_combo.set('Любой')
        city_combo.grid(row=0, column=3, padx=10, pady=10)
        
        tk.Label(filter_frame, text="Зарплата от:",
                font=('Segoe UI', 12),
                bg=self.colors['white']).grid(row=1, column=0, padx=10, pady=10, sticky='w')
        
        salary_from_entry = tk.Entry(filter_frame, font=('Segoe UI', 12), width=15)
        salary_from_entry.grid(row=1, column=1, padx=10, pady=10)
        
        tk.Label(filter_frame, text="Зарплата до:",
                font=('Segoe UI', 12),
                bg=self.colors['white']).grid(row=1, column=2, padx=10, pady=10, sticky='w')
        
        salary_to_entry = tk.Entry(filter_frame, font=('Segoe UI', 12), width=15)
        salary_to_entry.grid(row=1, column=3, padx=10, pady=10)
        
        search_btn = tk.Button(filter_frame, text="Найти",
                              font=('Segoe UI', 12, 'bold'),
                              bg=self.colors['success'],
                              fg=self.colors['dark'],
                              width=20)
        search_btn.grid(row=2, column=0, columnspan=4, pady=20)
    
    def show_my_resume(self):
        """Показать мое резюме"""
        self.clear_main_content()
        
        header_frame = tk.Frame(self.main_content, bg=self.colors['primary'], height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="📄 Мое резюме",
                font=('Segoe UI', 20, 'bold'),
                fg=self.colors['white'],
                bg=self.colors['primary']).pack(expand=True)
        
        content_frame = tk.Frame(self.main_content, bg=self.colors['white'])
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Проверяем, есть ли резюме
        self.cursor.execute("""
            SELECT id, title, desired_position, salary_expectation, 
                   experience, education, skills
            FROM resumes 
            WHERE user_id = ? AND is_active = 1
        """, (self.current_user['id'],))
        
        resume = self.cursor.fetchone()
        
        if resume:
            # Отображаем существующее резюме
            tk.Label(content_frame, text=resume[2] or "Должность не указана",
                    font=('Segoe UI', 24, 'bold'),
                    fg=self.colors['dark'],
                    bg=self.colors['white']).pack(pady=20)
            
            if resume[3]:
                tk.Label(content_frame, text=f"💰 Ожидаемая зарплата: {resume[3]:,} руб.",
                        font=('Segoe UI', 16),
                        fg=self.colors['success'],
                        bg=self.colors['white']).pack(pady=10)
            
            # Опыт работы
            if resume[4]:
                exp_frame = tk.Frame(content_frame, bg=self.colors['white'])
                exp_frame.pack(fill='x', pady=10)
                
                tk.Label(exp_frame, text="💼 Опыт работы:",
                        font=('Segoe UI', 16, 'bold'),
                        fg=self.colors['dark'],
                        bg=self.colors['white']).pack(anchor='w')
                
                tk.Label(exp_frame, text=resume[4],
                        font=('Segoe UI', 12),
                        fg=self.colors['dark'],
                        bg=self.colors['white'],
                        wraplength=800,
                        justify='left').pack(anchor='w', pady=5)
            
            # Кнопки управления
            button_frame = tk.Frame(content_frame, bg=self.colors['white'])
            button_frame.pack(pady=30)
            
            edit_btn = tk.Button(button_frame, text="✏️ Редактировать",
                                font=('Segoe UI', 12),
                                bg=self.colors['primary'],
                                fg='white',
                                width=20,
                                cursor='hand2',
                                command=self.edit_resume)
            edit_btn.pack(side='left', padx=10)
            
            delete_btn = tk.Button(button_frame, text="🗑️ Удалить",
                                  font=('Segoe UI', 12),
                                  bg=self.colors['danger'],
                                  fg='white',
                                  width=20,
                                  cursor='hand2',
                                  command=lambda: self.delete_resume(resume[0]))
            delete_btn.pack(side='left', padx=10)
        else:
            # Предлагаем создать резюме
            tk.Label(content_frame, text="У вас еще нет резюме",
                    font=('Segoe UI', 18),
                    fg=self.colors['gray'],
                    bg=self.colors['white']).pack(pady=50)
            
            create_btn = tk.Button(content_frame, text="➕ Создать резюме",
                                  font=('Segoe UI', 14, 'bold'),
                                  bg=self.colors['success'],
                                  fg=self.colors['dark'],
                                  width=30,
                                  height=3,
                                  cursor='hand2',
                                  command=self.create_resume)
            create_btn.pack(pady=20)
    
    def show_my_applications(self):
        """Показать мои отклики"""
        self.clear_main_content()
        
        header_frame = tk.Frame(self.main_content, bg=self.colors['primary'], height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="📨 Мои отклики",
                font=('Segoe UI', 20, 'bold'),
                fg=self.colors['white'],
                bg=self.colors['primary']).pack(expand=True)
        
        content_frame = tk.Frame(self.main_content, bg=self.colors['white'])
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Получаем отклики пользователя
        self.cursor.execute("""
            SELECT a.id, v.title, u.company_name, a.status, 
                   a.applied_at, a.cover_letter
            FROM applications a
            JOIN vacancies v ON a.vacancy_id = v.id
            JOIN users u ON v.employer_id = u.id
            JOIN resumes r ON a.resume_id = r.id
            WHERE r.user_id = ?
            ORDER BY a.applied_at DESC
        """, (self.current_user['id'],))
        
        applications = self.cursor.fetchall()
        
        if not applications:
            tk.Label(content_frame, text="У вас пока нет откликов",
                    font=('Segoe UI', 16),
                    fg=self.colors['gray'],
                    bg=self.colors['white']).pack(pady=50)
            return
        
        # Создаем таблицу для отображения откликов
        columns = ('Вакансия', 'Компания', 'Статус', 'Дата отклика')
        tree = ttk.Treeview(content_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=200)
        
        # Добавляем данные
        for app in applications:
            status_text = self.get_status_text(app[3])
            status_color = self.get_status_color(app[3])
            
            tree.insert('', 'end', values=(
                app[1], app[2], status_text, app[4]
            ))
        
        # Панель прокрутки
        scrollbar = ttk.Scrollbar(content_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
    
    def show_favorites(self):
        """Показать избранное"""
        self.clear_main_content()
        
        header_frame = tk.Frame(self.main_content, bg=self.colors['primary'], height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="⭐ Избранное",
                font=('Segoe UI', 20, 'bold'),
                fg=self.colors['white'],
                bg=self.colors['primary']).pack(expand=True)
        
        content_frame = tk.Frame(self.main_content, bg=self.colors['white'])
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        tk.Label(content_frame, text="Раздел в разработке",
                font=('Segoe UI', 18),
                fg=self.colors['gray'],
                bg=self.colors['white']).pack(expand=True)
    
    def show_seeker_profile(self):
        """Показать профиль соискателя"""
        self.clear_main_content()
        
        header_frame = tk.Frame(self.main_content, bg=self.colors['primary'], height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="⚙️ Профиль",
                font=('Segoe UI', 20, 'bold'),
                fg=self.colors['white'],
                bg=self.colors['primary']).pack(expand=True)
        
        content_frame = tk.Frame(self.main_content, bg=self.colors['white'])
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Получаем данные пользователя
        self.cursor.execute("""
            SELECT first_name, last_name, email, phone, city
            FROM users WHERE id = ?
        """, (self.current_user['id'],))
        
        user_data = self.cursor.fetchone()
        
        # Отображаем информацию
        info_frame = tk.Frame(content_frame, bg=self.colors['white'])
        info_frame.pack(pady=20)
        
        labels = ['Имя:', 'Фамилия:', 'Email:', 'Телефон:', 'Город:']
        for i, label in enumerate(labels):
            tk.Label(info_frame, text=label,
                    font=('Segoe UI', 12, 'bold'),
                    fg=self.colors['dark'],
                    bg=self.colors['white'],
                    width=10,
                    anchor='e').grid(row=i, column=0, padx=10, pady=10, sticky='e')
            
            value = user_data[i] if user_data[i] else 'Не указано'
            tk.Label(info_frame, text=value,
                    font=('Segoe UI', 12),
                    fg=self.colors['dark'],
                    bg=self.colors['white'],
                    width=30,
                    anchor='w').grid(row=i, column=1, padx=10, pady=10, sticky='w')
    
    def show_my_vacancies(self):
        """Показать мои вакансии (для работодателя)"""
        self.clear_main_content()
        
        header_frame = tk.Frame(self.main_content, bg=self.colors['secondary'], height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        title_frame = tk.Frame(header_frame, bg=self.colors['secondary'])
        title_frame.pack(expand=True)
        
        tk.Label(title_frame, text="📋 Мои вакансии",
                font=('Segoe UI', 20, 'bold'),
                fg=self.colors['white'],
                bg=self.colors['secondary']).pack(side='left', padx=10)
        
        create_btn = tk.Button(title_frame, text="➕ Создать вакансию",
                              font=('Segoe UI', 12, 'bold'),
                              bg=self.colors['success'],
                              fg=self.colors['dark'],
                              cursor='hand2',
                              command=self.show_create_vacancy)
        create_btn.pack(side='right', padx=10)
        
        content_frame = tk.Frame(self.main_content, bg=self.colors['white'])
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Получаем вакансии работодателя
        self.cursor.execute("""
            SELECT id, title, salary_from, salary_to, city, 
                   employment_type, is_active, created_at
            FROM vacancies 
            WHERE employer_id = ?
            ORDER BY created_at DESC
        """, (self.current_user['id'],))
        
        vacancies = self.cursor.fetchall()
        
        if not vacancies:
            tk.Label(content_frame, text="У вас пока нет вакансий",
                    font=('Segoe UI', 16),
                    fg=self.colors['gray'],
                    bg=self.colors['white']).pack(pady=50)
            return
        
        # Отображаем вакансии
        for vacancy in vacancies:
            vac_frame = tk.Frame(content_frame, bg=self.colors['light'],
                                relief='groove', borderwidth=1)
            vac_frame.pack(fill='x', pady=10, padx=10)
            
            # Статус
            status_frame = tk.Frame(vac_frame, bg=self.colors['light'])
            status_frame.pack(fill='x', padx=10, pady=5)
            
            status = "✅ Активна" if vacancy[6] else "❌ Неактивна"
            status_color = self.colors['success'] if vacancy[6] else self.colors['danger']
            
            tk.Label(status_frame, text=status,
                    font=('Segoe UI', 10, 'bold'),
                    fg=status_color,
                    bg=self.colors['light']).pack(side='left')
            
            # Информация о вакансии
            info_frame = tk.Frame(vac_frame, bg=self.colors['light'])
            info_frame.pack(fill='x', padx=10, pady=5)
            
            tk.Label(info_frame, text=vacancy[1],
                    font=('Segoe UI', 14, 'bold'),
                    fg=self.colors['dark'],
                    bg=self.colors['light']).pack(side='left')
            
            salary_text = f"💰 {vacancy[2]:,} - {vacancy[3]:,} руб."
            tk.Label(info_frame, text=salary_text,
                    font=('Segoe UI', 12),
                    fg=self.colors['success'],
                    bg=self.colors['light']).pack(side='right')
            
            # Детали
            details_frame = tk.Frame(vac_frame, bg=self.colors['light'])
            details_frame.pack(fill='x', padx=10, pady=5)
            
            tk.Label(details_frame, text=f"📍 {vacancy[4]} • {self.get_employment_type(vacancy[5])}",
                    font=('Segoe UI', 11),
                    fg=self.colors['gray'],
                    bg=self.colors['light']).pack(side='left')
            
            # Кнопки управления
            button_frame = tk.Frame(vac_frame, bg=self.colors['light'])
            button_frame.pack(fill='x', padx=10, pady=(5, 10))
            
            edit_btn = tk.Button(button_frame, text="✏️ Редактировать",
                                font=('Segoe UI', 10),
                                bg=self.colors['primary'],
                                fg='white',
                                cursor='hand2')
            edit_btn.pack(side='left', padx=5)
            
            toggle_btn = tk.Button(button_frame, 
                                  text="✅ Активировать" if not vacancy[6] else "❌ Деактивировать",
                                  font=('Segoe UI', 10),
                                  bg=self.colors['accent'],
                                  fg='white',
                                  cursor='hand2')
            toggle_btn.pack(side='left', padx=5)
            
            delete_btn = tk.Button(button_frame, text="🗑️ Удалить",
                                  font=('Segoe UI', 10),
                                  bg=self.colors['danger'],
                                  fg='white',
                                  cursor='hand2')
            delete_btn.pack(side='left', padx=5)
            
            stats_btn = tk.Button(button_frame, text="📊 Статистика",
                                 font=('Segoe UI', 10),
                                 bg=self.colors['success'],
                                 fg=self.colors['dark'],
                                 cursor='hand2')
            stats_btn.pack(side='left', padx=5)
    
    def show_create_vacancy(self):
        """Показать создание вакансии"""
        self.clear_main_content()
        
        header_frame = tk.Frame(self.main_content, bg=self.colors['secondary'], height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="➕ Создание вакансии",
                font=('Segoe UI', 20, 'bold'),
                fg=self.colors['white'],
                bg=self.colors['secondary']).pack(expand=True)
        
        # Форма создания вакансии
        form_frame = tk.Frame(self.main_content, bg=self.colors['white'])
        form_frame.pack(fill='both', expand=True, padx=50, pady=30)
        
        # Поля формы
        fields = [
            ("Название вакансии:", tk.Entry(form_frame, font=('Segoe UI', 12), width=40)),
            ("Описание:", tk.Text(form_frame, font=('Segoe UI', 12), height=6, width=40)),
            ("Требования:", tk.Text(form_frame, font=('Segoe UI', 12), height=4, width=40)),
            ("Зарплата от:", tk.Entry(form_frame, font=('Segoe UI', 12), width=15)),
            ("Зарплата до:", tk.Entry(form_frame, font=('Segoe UI', 12), width=15)),
            ("Город:", tk.Entry(form_frame, font=('Segoe UI', 12), width=20))
        ]
        
        for i, (label, widget) in enumerate(fields):
            tk.Label(form_frame, text=label,
                    font=('Segoe UI', 12),
                    bg=self.colors['white']).grid(row=i, column=0, padx=10, pady=10, sticky='w')
            widget.grid(row=i, column=1, padx=10, pady=10, sticky='w')
        
        # Тип занятости
        tk.Label(form_frame, text="Тип занятости:",
                font=('Segoe UI', 12),
                bg=self.colors['white']).grid(row=6, column=0, padx=10, pady=10, sticky='w')
        
        employment_types = ['Полная занятость', 'Частичная занятость', 'Удаленная работа', 'Проектная работа']
        employment_combo = ttk.Combobox(form_frame, values=employment_types, width=20)
        employment_combo.set('Полная занятость')
        employment_combo.grid(row=6, column=1, padx=10, pady=10, sticky='w')
        
        # Кнопки
        button_frame = tk.Frame(form_frame, bg=self.colors['white'])
        button_frame.grid(row=7, column=0, columnspan=2, pady=30)
        
        create_btn = tk.Button(button_frame, text="Создать вакансию",
                              font=('Segoe UI', 12, 'bold'),
                              bg=self.colors['success'],
                              fg=self.colors['dark'],
                              width=20,
                              cursor='hand2')
        create_btn.pack(side='left', padx=10)
        
        cancel_btn = tk.Button(button_frame, text="Отмена",
                              font=('Segoe UI', 12),
                              bg=self.colors['gray'],
                              fg='white',
                              width=20,
                              cursor='hand2',
                              command=self.show_my_vacancies)
        cancel_btn.pack(side='left', padx=10)
    
    def show_employer_applications(self):
        """Показать отклики (для работодателя)"""
        self.clear_main_content()
        
        header_frame = tk.Frame(self.main_content, bg=self.colors['secondary'], height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="📨 Отклики на вакансии",
                font=('Segoe UI', 20, 'bold'),
                fg=self.colors['white'],
                bg=self.colors['secondary']).pack(expand=True)
        
        content_frame = tk.Frame(self.main_content, bg=self.colors['white'])
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Получаем отклики на вакансии работодателя
        self.cursor.execute("""
            SELECT a.id, v.title, u.first_name, u.last_name, 
                   r.desired_position, a.status, a.applied_at
            FROM applications a
            JOIN vacancies v ON a.vacancy_id = v.id
            JOIN resumes r ON a.resume_id = r.id
            JOIN users u ON r.user_id = u.id
            WHERE v.employer_id = ?
            ORDER BY a.applied_at DESC
        """, (self.current_user['id'],))
        
        applications = self.cursor.fetchall()
        
        if not applications:
            tk.Label(content_frame, text="Пока нет откликов на ваши вакансии",
                    font=('Segoe UI', 16),
                    fg=self.colors['gray'],
                    bg=self.colors['white']).pack(pady=50)
            return
        
        # Таблица откликов
        columns = ('Вакансия', 'Кандидат', 'Должность', 'Статус', 'Дата')
        tree = ttk.Treeview(content_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        
        # Добавляем данные
        for app in applications:
            candidate = f"{app[2]} {app[3]}" if app[2] and app[3] else "Не указано"
            status_text = self.get_status_text(app[5])
            
            tree.insert('', 'end', values=(
                app[1], candidate, app[4], status_text, app[6]
            ))
        
        scrollbar = ttk.Scrollbar(content_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
    
    def show_resume_search(self):
        """Показать поиск резюме (для работодателя)"""
        self.clear_main_content()
        
        header_frame = tk.Frame(self.main_content, bg=self.colors['secondary'], height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="🔍 Поиск резюме",
                font=('Segoe UI', 20, 'bold'),
                fg=self.colors['white'],
                bg=self.colors['secondary']).pack(expand=True)
        
        content_frame = tk.Frame(self.main_content, bg=self.colors['white'])
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        tk.Label(content_frame, text="Раздел в разработке",
                font=('Segoe UI', 18),
                fg=self.colors['gray'],
                bg=self.colors['white']).pack(expand=True)
    
    def show_statistics(self):
        """Показать статистику"""
        self.clear_main_content()
        
        header_frame = tk.Frame(self.main_content, bg=self.colors['secondary'], height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="📊 Статистика",
                font=('Segoe UI', 20, 'bold'),
                fg=self.colors['white'],
                bg=self.colors['secondary']).pack(expand=True)
        
        content_frame = tk.Frame(self.main_content, bg=self.colors['white'])
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Пример статистики
        stats = [
            ("Всего вакансий:", "15"),
            ("Активных вакансий:", "12"),
            ("Всего откликов:", "47"),
            ("Новых откликов:", "3"),
            ("Приглашено на собеседование:", "12"),
            ("Отклонено:", "8")
        ]
        
        for i, (label, value) in enumerate(stats):
            stat_frame = tk.Frame(content_frame, bg=self.colors['white'])
            stat_frame.pack(fill='x', pady=10)
            
            tk.Label(stat_frame, text=label,
                    font=('Segoe UI', 14),
                    fg=self.colors['dark'],
                    bg=self.colors['white']).pack(side='left', padx=20)
            
            tk.Label(stat_frame, text=value,
                    font=('Segoe UI', 16, 'bold'),
                    fg=self.colors['primary'],
                    bg=self.colors['white']).pack(side='right', padx=20)
    
    def show_employer_profile(self):
        """Показать профиль компании"""
        self.clear_main_content()
        
        header_frame = tk.Frame(self.main_content, bg=self.colors['secondary'], height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="⚙️ Профиль компании",
                font=('Segoe UI', 20, 'bold'),
                fg=self.colors['white'],
                bg=self.colors['secondary']).pack(expand=True)
        
        content_frame = tk.Frame(self.main_content, bg=self.colors['white'])
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Получаем данные компании
        self.cursor.execute("""
            SELECT company_name, email, phone, city
            FROM users WHERE id = ?
        """, (self.current_user['id'],))
        
        company_data = self.cursor.fetchone()
        
        # Отображаем информацию
        info_frame = tk.Frame(content_frame, bg=self.colors['white'])
        info_frame.pack(pady=20)
        
        labels = ['Название компании:', 'Email:', 'Телефон:', 'Город:']
        for i, label in enumerate(labels):
            tk.Label(info_frame, text=label,
                    font=('Segoe UI', 12, 'bold'),
                    fg=self.colors['dark'],
                    bg=self.colors['white'],
                    width=20,
                    anchor='e').grid(row=i, column=0, padx=10, pady=10, sticky='e')
            
            value = company_data[i] if company_data[i] else 'Не указано'
            tk.Label(info_frame, text=value,
                    font=('Segoe UI', 12),
                    fg=self.colors['dark'],
                    bg=self.colors['white'],
                    width=30,
                    anchor='w').grid(row=i, column=1, padx=10, pady=10, sticky='w')
    
    def create_resume(self):
        """Создание резюме"""
        # В реальном приложении здесь должна быть форма для создания резюме
        self.cursor.execute("""
            INSERT INTO resumes (user_id, title, desired_position, 
                               salary_expectation, experience, education, skills)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (self.current_user['id'], 
              "Мое резюме", 
              "Разработчик Python",
              120000,
              "Опыт работы 2 года в IT-компании",
              "Высшее техническое образование",
              "Python, Django, SQL, Git"))
        
        self.conn.commit()
        messagebox.showinfo("Успех", "Резюме создано успешно!")
        self.show_my_resume()
    
    def edit_resume(self):
        """Редактирование резюме"""
        messagebox.showinfo("Информация", "Функция редактирования резюме в разработке")
    
    def delete_resume(self, resume_id):
        """Удаление резюме"""
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить резюме?"):
            self.cursor.execute("DELETE FROM resumes WHERE id = ?", (resume_id,))
            self.conn.commit()
            messagebox.showinfo("Успех", "Резюме удалено")
            self.show_my_resume()
    
    def apply_to_vacancy(self, vacancy_id):
        """Откликнуться на вакансию"""
        # Проверяем, есть ли у пользователя резюме
        self.cursor.execute("SELECT id FROM resumes WHERE user_id = ?", (self.current_user['id'],))
        resume = self.cursor.fetchone()
        
        if not resume:
            messagebox.showerror("Ошибка", "Сначала создайте резюме")
            self.show_my_resume()
            return
        
        # Создаем отклик
        try:
            self.cursor.execute("""
                INSERT INTO applications (resume_id, vacancy_id, cover_letter)
                VALUES (?, ?, ?)
            """, (resume[0], vacancy_id, "Заинтересован в вакансии"))
            
            self.conn.commit()
            messagebox.showinfo("Успех", "Отклик отправлен успешно!")
            
        except sqlite3.IntegrityError:
            messagebox.showinfo("Информация", "Вы уже откликались на эту вакансию")
    
    def show_vacancy_details(self, vacancy):
        """Показать детали вакансии"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Детали вакансии")
        dialog.geometry("800x600")
        dialog.configure(bg=self.colors['white'])
        
        # Заголовок
        title_frame = tk.Frame(dialog, bg=self.colors['primary'])
        title_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(title_frame, text=vacancy[1],
                font=('Segoe UI', 20, 'bold'),
                fg=self.colors['white'],
                bg=self.colors['primary'],
                pady=15).pack()
        
        # Контент
        content_frame = tk.Frame(dialog, bg=self.colors['white'])
        content_frame.pack(fill='both', expand=True, padx=30, pady=20)
        
        # Зарплата
        salary_frame = tk.Frame(content_frame, bg=self.colors['white'])
        salary_frame.pack(fill='x', pady=10)
        
        salary_text = f"💰 {vacancy[3]:,} - {vacancy[4]:,} руб."
        tk.Label(salary_frame, text=salary_text,
                font=('Segoe UI', 18, 'bold'),
                fg=self.colors['success'],
                bg=self.colors['white']).pack()
        
        # Компания и локация
        info_frame = tk.Frame(content_frame, bg=self.colors['white'])
        info_frame.pack(fill='x', pady=10)
        
        tk.Label(info_frame, text=f"🏢 {vacancy[7]}",
                font=('Segoe UI', 14),
                fg=self.colors['dark'],
                bg=self.colors['white']).pack()
        
        location_text = f"📍 {vacancy[5]} • {self.get_employment_type(vacancy[6])}"
        tk.Label(info_frame, text=location_text,
                font=('Segoe UI', 14),
                fg=self.colors['gray'],
                bg=self.colors['white']).pack()
        
        # Описание
        tk.Label(content_frame, text="📝 Описание:",
                font=('Segoe UI', 14, 'bold'),
                fg=self.colors['dark'],
                bg=self.colors['white']).pack(anchor='w', pady=(20, 5))
        
        description_text = tk.Text(content_frame, font=('Segoe UI', 12),
                                  height=10, width=70, wrap='word')
        description_text.insert('1.0', vacancy[2])
        description_text.config(state='disabled')
        description_text.pack(fill='both', expand=True)
        
        # Кнопки
        button_frame = tk.Frame(content_frame, bg=self.colors['white'])
        button_frame.pack(pady=20)
        
        close_btn = tk.Button(button_frame, text="Закрыть",
                             font=('Segoe UI', 12),
                             bg=self.colors['gray'],
                             fg='white',
                             width=20,
                             command=dialog.destroy)
        close_btn.pack()
    
    def get_employment_type(self, type_code):
        """Получить текстовое представление типа занятости"""
        types = {
            'full_time': 'Полная занятость',
            'part_time': 'Частичная занятость',
            'remote': 'Удаленная работа',
            'hybrid': 'Гибридный формат'
        }
        return types.get(type_code, type_code)
    
    def get_status_text(self, status):
        """Получить текстовое представление статуса"""
        statuses = {
            'pending': 'Ожидает рассмотрения',
            'viewed': 'Просмотрено',
            'interview': 'Приглашен на собеседование',
            'rejected': 'Отклонено',
            'hired': 'Принят'
        }
        return statuses.get(status, status)
    
    def get_status_color(self, status):
        """Получить цвет для статуса"""
        colors = {
            'pending': self.colors['gray'],
            'viewed': self.colors['primary'],
            'interview': self.colors['accent'],
            'rejected': self.colors['danger'],
            'hired': self.colors['success']
        }
        return colors.get(status, self.colors['dark'])
    
    def clear_window(self):
        """Очистить главное окно"""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def clear_main_content(self):
        """Очистить основную область контента"""
        if hasattr(self, 'main_content'):
            for widget in self.main_content.winfo_children():
                widget.destroy()
    
    def logout(self):
        """Выйти из системы"""
        self.current_user = None
        self.user_type = None
        self.show_start_screen()

def main():
    root = tk.Tk()
    app = JobFinderApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()