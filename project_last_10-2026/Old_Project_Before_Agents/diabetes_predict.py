import tkinter as tk
from tkinter import messagebox
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib
import os
import numpy as np
import matplotlib.pyplot as plt
import arabic_reshaper
from bidi.algorithm import get_display

class DiabetesPredictorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Neelain University - Master's Project")
        self.root.geometry("750x900")
        self.root.configure(bg="#f4f7f6")

        self.data_path = r"diabetes_data.csv"
        self.model_filename = "diabetes_model.pkl"
        
        self.features_info = [
            {"en": "Pregnancies", "ar": "عدد مرات الحمل", "range": "0 - 17", "ideal": "0"},
            {"en": "Glucose", "ar": "مستوى الجلوكوز", "range": "70 - 200", "ideal": "70-100"},
            {"en": "BloodPressure", "ar": "ضغط الدم", "range": "40 - 122", "ideal": "80"},
            {"en": "SkinThickness", "ar": "سمك الجلد", "range": "0 - 99", "ideal": "20"},
            {"en": "Insulin", "ar": "الإنسولين", "range": "0 - 846", "ideal": "79"},
            {"en": "BMI", "ar": "مؤشر كتلة الجسم", "range": "10 - 67", "ideal": "18.5-25"},
            {"en": "DiabetesPedigreeFunction", "ar": "وراثة السكري", "range": "0.08 - 2.4", "ideal": "0.5"},
            {"en": "Age", "ar": "العمر", "range": "21 - 81", "ideal": "---"}
        ]

        self.inputs = {}
        self.model = None
        self.result_var = tk.StringVar()
        self.result_var.set(self.fix_text("أدخل البيانات ثم اضغط على زر التحليل"))

        self.prepare_system()
        self.create_widgets()

    def fix_text(self, text):
        reshaped_text = arabic_reshaper.reshape(text)
        return get_display(reshaped_text)

    def prepare_system(self):
        # محاولة تحميل النموذج أو تدريبه
        if os.path.exists(self.model_filename):
            try:
                self.model = joblib.load(self.model_filename)
            except:
                self.train_model_logic()
        else:
            self.train_model_logic()

    def train_model_logic(self):
        if os.path.exists(self.data_path):
            try:
                df = pd.read_csv(self.data_path)
                features_en = [f['en'] for f in self.features_info]
                X = df[features_en]
                y = df['Outcome']
                self.model = RandomForestClassifier(n_estimators=100, random_state=42)
                self.model.fit(X.values, y)
                joblib.dump(self.model, self.model_filename)
            except Exception as e:
                print("ERROR:", e)
                messagebox.showerror("ERROR", str(e))

    def create_widgets(self):
        # الهوية والأسماء
        header_frame = tk.Frame(self.root, bg="#1a4d2e", pady=5)
        header_frame.pack(fill=tk.X)
        tk.Label(header_frame, text=self.fix_text("جامعة النيلين"), font=("Tahoma", 16, "bold"), bg="#1a4d2e", fg="#deff9a").pack()
        
        info_frame = tk.Frame(self.root, bg="#2e7d32", pady=5)
        info_frame.pack(fill=tk.X)
        header_frame = tk.Frame(self.root, bg="#1a4d2e", pady=5)
        header_frame.pack(fill=tk.X)
        tk.Label(header_frame, text=self.fix_text("نظام التشخيص التنبئي للسكري"), font=("Tahoma", 16, "bold"), bg="#1a4d2e", fg="#deff9a").pack()
        
        info_frame = tk.Frame(self.root, bg="#2e7d32", pady=5)
        info_frame.pack(fill=tk.X)
        tk.Label(info_frame, text=self.fix_text("تصميم وبرمجة طالب ماجستير : محمد ابوالقاسم"), font=("Tahoma", 10, "bold"), bg="#2e7d32", fg="white").pack()
        tk.Label(info_frame, text=self.fix_text("اشراف : د. امين مبارك"), font=("Tahoma", 12, "bold"), bg="#2e7d32", fg="#deff9a").pack()

        # منطقة النتيجة (تم تكبيرها لضمان الظهور في EXE)
        result_frame = tk.LabelFrame(self.root, text=self.fix_text("نتائج التحليل"), font=("Tahoma", 11, "bold"), bg="#ffffff", fg="white", labelanchor="ne")
        result_frame.pack(fill=tk.X, padx=40, pady=10)
        
        self.result_label = tk.Label(result_frame, textvariable=self.result_var, font=("Tahoma", 11, "bold"), bg="#ffffff", fg="#333", height=4, wraplength=600, justify="right")
        self.result_label.pack(pady=10)

        container = tk.Frame(self.root, bg="#f4f7f6", padx=30)
        container.pack(expand=True, fill=tk.BOTH)

        # جدول المدخلات
        table_header = tk.Frame(container, bg="#cfd8dc")
        table_header.pack(fill=tk.X, pady=5)
        tk.Label(table_header, text=self.fix_text("المعيار الطبي"), font=("Tahoma", 9, "bold"), bg="#cfd8dc", width=25).pack(side=tk.RIGHT)
        tk.Label(table_header, text=self.fix_text("القيمة"), font=("Tahoma", 9, "bold"), bg="#cfd8dc", width=15).pack(side=tk.RIGHT)
        tk.Label(table_header, text=self.fix_text("المدى المثالي"), font=("Tahoma", 9, "bold"), bg="#cfd8dc", width=20).pack(side=tk.RIGHT)

        for info in self.features_info:
            frame = tk.Frame(container, bg="#f4f7f6")
            frame.pack(fill=tk.X, pady=2)
            tk.Label(frame, text=self.fix_text(info['ar']), font=("Tahoma", 10), bg="#f4f7f6", width=25, anchor="e").pack(side=tk.RIGHT)
            entry = tk.Entry(frame, font=("Arial", 11), justify="center", bd=2, width=15)
            entry.pack(side=tk.RIGHT, padx=10)
            self.inputs[info['en']] = entry
            tk.Label(frame, text=f"{info['range']} ({info['ideal']})", font=("Arial", 8), fg="#546e7a", bg="#f4f7f6", width=20).pack(side=tk.RIGHT)

        # الأزرار
        btn_container = tk.Frame(self.root, bg="#f4f7f6", pady=15)
        btn_container.pack()
        tk.Button(btn_container, text=self.fix_text("تحليل الحالة"), font=("Tahoma", 12, "bold"), bg="#2e7d32", fg="white", padx=50, pady=10, command=self.predict_diabetes).grid(row=0, column=1, padx=10)
        tk.Button(btn_container, text=self.fix_text("تحليل العوامل"), font=("Tahoma", 10), bg="#455a64", fg="white", padx=20, command=self.show_importance_chart).grid(row=0, column=0, padx=10)

    def predict_diabetes(self):
        if not self.model:
            self.result_var.set(self.fix_text("خطأ: تأكد من ملف C:\\proj\\diabetes_data.csv"))
            self.root.update_idletasks() # تحديث الواجهة فوراً
            return
        try:
            features_en = [f['en'] for f in self.features_info]
            data = [float(self.inputs[f].get()) for f in features_en]
            prediction = self.model.predict([data])[0]
            prob = self.model.predict_proba([data])[0][1] * 100
            
            if prediction == 1:
                l1 = self.fix_text("التشخيص: احتمال وجود إصابة بالسكري.")
                l2 = arabic_reshaper.reshape("درجة الموثوقية: ") + f"%{prob:.1f}"
                l3 = self.fix_text("توصية: يرجى مراجعة المختبر لإجراء الفحوصات.")
                self.result_label.config(fg="#c62828") 
            else:
                l1 = self.fix_text("التشخيص: الحالة سليمة من السكري حالياً.")
                l2 = arabic_reshaper.reshape("درجة الموثوقية: ") + f"%{100-prob:.1f}"
                l3 = self.fix_text("توصية: حافظ على النشاط البدني.")
                self.result_label.config(fg="#2e7d32")
            
            res = f"{l1}\n{l2}\n{l3}"
            self.result_var.set(res)
            self.root.update_idletasks() # إجبار الملف التنفيذي على إظهار النتيجة
            
        except ValueError:
            self.result_var.set(self.fix_text("خطأ: يرجى إدخال جميع الأرقام بشكل صحيح."))
            self.root.update_idletasks()

    def show_importance_chart(self):
        if not self.model: return
        importances = self.model.feature_importances_
        indices = np.argsort(importances)
        
        # Configure fonts for clean native Arabic rendering in Matplotlib
        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['font.sans-serif'] = ['Segoe UI', 'Arial', 'Tahoma', 'DejaVu Sans']
        
        plt_labels = [self.features_info[i]['ar'] for i in indices]
        plt.figure(figsize=(10, 6))
        plt.barh(range(len(indices)), importances[indices], color='#1a4d2e')
        plt.yticks(range(len(indices)), plt_labels, fontsize=11)
        plt.title("تحليل المعايير الطبية", fontsize=14, fontweight='bold', pad=12)
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    root = tk.Tk()
    app = DiabetesPredictorApp(root)
    root.mainloop()