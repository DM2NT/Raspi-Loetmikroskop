#!/usr/bin/env python3
"""Lötmikroskop Software - Version 0.1 - (c) 2025 DM2NT"""

import cv2, numpy as np, tkinter as tk, threading, time, os, subprocess
from picamera2 import Picamera2
from PIL import Image, ImageTk
from datetime import datetime
from libcamera import Transform as LibcameraTransform
try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except:
    GPIO_AVAILABLE = False

class Loetmikroskop:
    def __init__(s, root):
        s.root = root
        s.root.overrideredirect(True)
        s.root.geometry(f"{s.root.winfo_screenwidth()}x{s.root.winfo_screenheight()}+0+0")
        s.root.configure(bg='black')
        s.root.update_idletasks()
        s.root.bind('<Escape>', lambda e: s.beenden())
        
        s.foto_dir = os.path.expanduser("~/Fotos")
        os.makedirs(s.foto_dir, exist_ok=True)
        s.menu_timeout_id = None
        
        if GPIO_AVAILABLE:
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            GPIO.setup(17, GPIO.OUT)
            GPIO.setup(27, GPIO.OUT)
            GPIO.output(17, GPIO.LOW)
            GPIO.output(27, GPIO.LOW)
        
        s.picam2 = Picamera2()
        config = s.picam2.create_preview_configuration(main={"size":(2028,1520)}, buffer_count=2)
        config["transform"] = LibcameraTransform(hflip=1, vflip=1)
        s.picam2.configure(config)
        s.picam2.start()
        time.sleep(1)
        
        s.zoom_level=1.0; s.zoom_center_x=0.5; s.zoom_center_y=0.5
        s.brightness=0; s.contrast=1.0; s.saturation=1.0
        s.exposure_time=10000; s.analog_gain=1.0; s.manual_mode=False
        s.running=True; s.pan_active=False; s.current_frame=None
        s.current_resolution=(2028,1520); s.fps=0; s.frame_count=0; s.fps_time=time.time()
        s.light_mode="aus"
        s.bild_rotiert=True
        
        s.erstelle_gui()
        threading.Thread(target=s.update_bild, daemon=True).start()
        s.zeige_splash()
        
    def erstelle_gui(s):
        s.canvas = tk.Canvas(s.root, bg='black', highlightthickness=0)
        s.canvas.pack(fill=tk.BOTH, expand=True)
        s.canvas.bind('<Button-1>', s.canvas_click)
        s.canvas.bind('<B1-Motion>', s.pan_move)
        s.canvas.bind('<ButtonRelease-1>', lambda e: setattr(s, 'pan_active', False))
        
        s.sidebar_visible=False; s.res_menu_visible=False; s.light_menu_visible=False; s.shutdown_menu_visible=False
        
        tk.Button(s.root, text="⚙", font=('Arial',16), command=s.toggle_sidebar, bg='#404040', fg='white', relief=tk.FLAT, width=3, height=1).place(x=10,y=10)
        tk.Button(s.root, text="📷", font=('Arial',16), command=s.foto_machen, bg='#306030', fg='white', relief=tk.FLAT, width=3, height=1).place(x=10,y=60)
        tk.Button(s.root, text="▭", font=('Arial',20), command=s.toggle_resolution_menu, bg='#404040', fg='white', relief=tk.FLAT, width=3, height=1).place(x=10,y=110)
        tk.Button(s.root, text="☀", font=('Arial',16), command=s.toggle_light_menu, bg='#404040', fg='white', relief=tk.FLAT, width=3, height=1).place(x=10,y=160)
        tk.Button(s.root, text="↻", font=('Arial',20), command=s.toggle_rotation, bg='#404040', fg='white', relief=tk.FLAT, width=3, height=1).place(x=10,y=210)
        s.foto_status = tk.Label(s.root, text="", bg='black', fg='#00ff00', font=('Arial',10,'bold'))
        s.foto_status.place(x=60,y=62)
        s.fps_label = tk.Label(s.root, text="FPS: 0", font=('Arial',10), bg='#404040', fg='white')
        s.fps_label.place(x=70,y=15)
        tk.Button(s.root, text="✕", font=('Arial',16), command=s.beenden, bg='#803030', fg='white', relief=tk.FLAT, width=3, height=1).place(relx=1.0,x=-10,y=10,anchor='ne')
        tk.Button(s.root, text="⏻", font=('Arial',16), command=s.toggle_shutdown_menu, bg='#804040', fg='white', relief=tk.FLAT, width=3, height=1).place(relx=1.0,x=-10,y=60,anchor='ne')
        
        s.build_settings()
        s.build_resolution()
        s.build_light()
        s.build_shutdown()
        
    def build_settings(s):
        s.sidebar = tk.Frame(s.root, bg='#2b2b2b', width=280)
        
        canvas_scroll = tk.Canvas(s.sidebar, bg='#2b2b2b', highlightthickness=0, width=280)
        scrollbar = tk.Scrollbar(s.sidebar, orient="vertical", command=canvas_scroll.yview)
        scrollable_frame = tk.Frame(canvas_scroll, bg='#2b2b2b')
        
        scrollable_frame.bind("<Configure>", lambda e: canvas_scroll.configure(scrollregion=canvas_scroll.bbox("all")))
        canvas_scroll.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas_scroll.configure(yscrollcommand=scrollbar.set)
        
        canvas_scroll.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        tk.Label(scrollable_frame, text="Einstellungen", bg='#2b2b2b', fg='white', font=('Arial',11,'bold')).pack(pady=10)
        f=tk.Frame(scrollable_frame, bg='#2b2b2b'); f.pack(pady=8,padx=10,fill=tk.X)
        tk.Label(f, text="Zoom", bg='#2b2b2b', fg='white', font=('Arial',9,'bold')).pack(anchor='w')
        fc=tk.Frame(f, bg='#2b2b2b'); fc.pack(fill=tk.X)
        s.zoom_slider=tk.Scale(fc, from_=1.0, to=8.0, resolution=0.1, orient=tk.HORIZONTAL, command=s.update_zoom, bg='#404040', fg='white', highlightthickness=0, length=180, showvalue=0)
        s.zoom_slider.set(1.0); s.zoom_slider.pack(side=tk.LEFT)
        fi=tk.Frame(fc, bg='#2b2b2b'); fi.pack(side=tk.LEFT,padx=5)
        s.zoom_label=tk.Label(fi, text="1.0x", bg='#2b2b2b', fg='#00ff00', font=('Arial',10,'bold')); s.zoom_label.pack()
        tk.Button(fi, text="↺", command=s.reset_zoom, bg='#505050', fg='white', relief=tk.FLAT, font=('Arial',9), width=2).pack()
        tk.Frame(scrollable_frame, bg='#555', height=1).pack(fill=tk.X,pady=8)
        
        for name,var,fr,to in [("Helligkeit",'brightness_slider',-100,100),("Kontrast",'contrast_slider',0.5,2.0),("Farbe",'saturation_slider',0.0,2.0),("Belichtung",'exposure_slider',1000,50000),("ISO/Verstärkung",'gain_slider',1.0,16.0)]:
            fb=tk.Frame(scrollable_frame, bg='#2b2b2b'); fb.pack(pady=5,padx=10,fill=tk.X)
            tk.Label(fb, text=name, bg='#2b2b2b', fg='white', font=('Arial',8)).pack(anchor='w')
            sl=tk.Scale(fb, from_=fr, to=to, resolution=0.1 if to<=16 else 1000, orient=tk.HORIZONTAL, bg='#404040', fg='white', highlightthickness=0, length=240, showvalue=0)
            setattr(s, var, sl)
            sl.pack()
            if 'brightness' in var: sl.set(0); sl.config(command=lambda v: setattr(s,'brightness',int(v)))
            elif 'contrast' in var: sl.set(1.0); sl.config(command=lambda v: setattr(s,'contrast',float(v)))
            elif 'saturation' in var: sl.set(1.0); sl.config(command=lambda v: setattr(s,'saturation',float(v)))
            elif 'exposure' in var: sl.set(10000); sl.config(command=lambda v: setattr(s,'exposure_time',int(v))); sl.bind('<ButtonRelease-1>', lambda e: s.apply_exposure())
            elif 'gain' in var: sl.set(1.0); sl.config(command=lambda v: setattr(s,'analog_gain',float(v))); sl.bind('<ButtonRelease-1>', lambda e: s.apply_gain())
        tk.Frame(scrollable_frame, bg='#555', height=1).pack(fill=tk.X,pady=8)
        fc=tk.Frame(scrollable_frame, bg='#2b2b2b'); fc.pack(pady=5,padx=10,fill=tk.X)
        s.auto_btn=tk.Button(fc, text="AUTO", font=('Arial',9), command=s.set_auto_mode, bg='#505050', fg='white', relief=tk.FLAT, width=10); s.auto_btn.pack(side=tk.LEFT,padx=2)
        s.manual_btn=tk.Button(fc, text="MANUELL", font=('Arial',9), command=s.set_manual_mode, bg='#305050', fg='white', relief=tk.FLAT, width=10); s.manual_btn.pack(side=tk.LEFT,padx=2)
        tk.Label(scrollable_frame, text="Ziehen zum Verschieben (bei Zoom)", bg='#2b2b2b', fg='#666', font=('Arial',7), justify=tk.CENTER, wraplength=250).pack(pady=20)
        
    def build_resolution(s):
        s.res_menu = tk.Frame(s.root, bg='#2b2b2b', width=280)
        tk.Label(s.res_menu, text="Auflösung wählen", bg='#2b2b2b', fg='white', font=('Arial',11,'bold')).pack(pady=10)
        s.res_btns={}
        for label,res in [("12 Megapixel\n4056x3040\n~10 FPS",(4056,3040)),("3 Megapixel\n2028x1520\n~30 FPS",(2028,1520)),("Full HD\n1920x1080\n~40 FPS",(1920,1080)),("HD Ready\n1280x720\n~60 FPS",(1280,720))]:
            btn=tk.Button(s.res_menu, text=label, font=('Arial',10), command=lambda r=res:s.change_resolution(r), bg='#408040' if res==s.current_resolution else '#505050', fg='white', relief=tk.FLAT, height=3, width=20)
            btn.pack(pady=5,padx=10); s.res_btns[res]=btn
            
    def build_light(s):
        s.light_menu = tk.Frame(s.root, bg='#2b2b2b', width=280)
        tk.Label(s.light_menu, text="Beleuchtung", bg='#2b2b2b', fg='white', font=('Arial',11,'bold')).pack(pady=10)
        s.light_aus_btn=tk.Button(s.light_menu, text="⚫ AUS", font=('Arial',12), command=lambda:s.set_light("aus"), bg='#408040' if s.light_mode=="aus" else '#505050', fg='white', relief=tk.FLAT, height=3, width=20); s.light_aus_btn.pack(pady=10,padx=10)
        s.light_kalt_btn=tk.Button(s.light_menu, text="💡 KALTWEISS\nLeuchtstoffröhre\nGPIO 17", font=('Arial',11), command=lambda:s.set_light("kalt"), bg='#408040' if s.light_mode=="kalt" else '#505050', fg='white', relief=tk.FLAT, height=4, width=20); s.light_kalt_btn.pack(pady=10,padx=10)
        s.light_warm_btn=tk.Button(s.light_menu, text="💡 WARMWEISS\nGlühlampe\nGPIO 27", font=('Arial',11), command=lambda:s.set_light("warm"), bg='#408040' if s.light_mode=="warm" else '#505050', fg='white', relief=tk.FLAT, height=4, width=20); s.light_warm_btn.pack(pady=10,padx=10)
        
    def build_shutdown(s):
        s.shutdown_menu = tk.Frame(s.root, bg='#2b2b2b', width=280)
        tk.Label(s.shutdown_menu, text="Herunterfahren?", bg='#2b2b2b', fg='white', font=('Arial',14,'bold')).pack(pady=20)
        tk.Label(s.shutdown_menu, text="Raspberry Pi wirklich\nherunterfahren?", bg='#2b2b2b', fg='#ff6666', font=('Arial',12), justify=tk.CENTER).pack(pady=20)
        tk.Button(s.shutdown_menu, text="✓ JA\nHerunterfahren", font=('Arial',14,'bold'), command=s.do_shutdown, bg='#a04040', fg='white', relief=tk.FLAT, height=4, width=20).pack(pady=15,padx=10)
        tk.Button(s.shutdown_menu, text="✗ NEIN\nAbbrechen", font=('Arial',14,'bold'), command=s.toggle_shutdown_menu, bg='#408040', fg='white', relief=tk.FLAT, height=4, width=20).pack(pady=15,padx=10)
        
    def zeige_splash(s):
        sp=tk.Frame(s.root, bg='#1a1a1a'); sp.place(relx=0, rely=0, relwidth=1, relheight=1)
        c=tk.Frame(sp, bg='#1a1a1a'); c.place(relx=0.5, rely=0.5, anchor='center')
        tk.Label(c, text="Raspberry Pi\nLötmikroskop", bg='#1a1a1a', fg='#00ff00', font=('Arial',28,'bold'), justify=tk.CENTER).pack(pady=20)
        tk.Label(c, text="Version: 0.1", bg='#1a1a1a', fg='#aaaaaa', font=('Arial',16)).pack(pady=10)
        tk.Label(c, text="(c) 2025 DM2NT", bg='#1a1a1a', fg='#888888', font=('Arial',14)).pack(pady=10)
        tk.Frame(c, bg='#444444', height=2, width=300).pack(pady=20)
        tk.Label(c, text="Wird geladen...", bg='#1a1a1a', fg='#666666', font=('Arial',12,'italic')).pack(pady=10)
        s.root.update(); s.root.after(3000, sp.destroy)
    
    def start_menu_timeout(s):
        if s.menu_timeout_id: s.root.after_cancel(s.menu_timeout_id)
        s.menu_timeout_id = s.root.after(15000, s.close_all_menus)
    
    def close_all_menus(s):
        if s.sidebar_visible: s.toggle_sidebar()
        if s.res_menu_visible: s.toggle_resolution_menu()
        if s.light_menu_visible: s.toggle_light_menu()
        if s.shutdown_menu_visible: s.toggle_shutdown_menu()
        
    def canvas_click(s, e):
        if s.sidebar_visible or s.res_menu_visible or s.light_menu_visible or s.shutdown_menu_visible:
            # Prüfe ob Klick außerhalb der Menüs
            if s.sidebar_visible:
                sx = s.root.winfo_width() - 280
                if e.x < sx: s.close_all_menus(); return
            elif s.res_menu_visible or s.light_menu_visible or s.shutdown_menu_visible:
                mx = s.root.winfo_width() - 280
                if e.x < mx: s.close_all_menus(); return
        # Normal pan
        if s.zoom_level>1.0: s.pan_active=True; s.last_pan_x=e.x; s.last_pan_y=e.y
        
    def toggle_sidebar(s):
        if s.sidebar_visible: 
            s.sidebar.place_forget(); s.sidebar_visible=False
            if s.menu_timeout_id: s.root.after_cancel(s.menu_timeout_id)
        else:
            if s.res_menu_visible: s.toggle_resolution_menu()
            if s.light_menu_visible: s.toggle_light_menu()
            if s.shutdown_menu_visible: s.toggle_shutdown_menu()
            s.sidebar.place(relx=1.0, x=0, y=0, anchor='ne', relheight=1.0); s.sidebar_visible=True
            s.start_menu_timeout()
            
    def toggle_resolution_menu(s):
        if s.res_menu_visible: 
            s.res_menu.place_forget(); s.res_menu_visible=False
            if s.menu_timeout_id: s.root.after_cancel(s.menu_timeout_id)
        else:
            if s.sidebar_visible: s.toggle_sidebar()
            if s.light_menu_visible: s.toggle_light_menu()
            if s.shutdown_menu_visible: s.toggle_shutdown_menu()
            s.res_menu.place(relx=1.0, x=0, y=0, anchor='ne', relheight=1.0); s.res_menu_visible=True
            s.start_menu_timeout()
            
    def toggle_light_menu(s):
        if s.light_menu_visible: 
            s.light_menu.place_forget(); s.light_menu_visible=False
            if s.menu_timeout_id: s.root.after_cancel(s.menu_timeout_id)
        else:
            if s.sidebar_visible: s.toggle_sidebar()
            if s.res_menu_visible: s.toggle_resolution_menu()
            if s.shutdown_menu_visible: s.toggle_shutdown_menu()
            s.light_menu.place(relx=1.0, x=0, y=0, anchor='ne', relheight=1.0); s.light_menu_visible=True
            s.start_menu_timeout()
            
    def toggle_shutdown_menu(s):
        if s.shutdown_menu_visible: 
            s.shutdown_menu.place_forget(); s.shutdown_menu_visible=False
            if s.menu_timeout_id: s.root.after_cancel(s.menu_timeout_id)
        else:
            if s.sidebar_visible: s.toggle_sidebar()
            if s.res_menu_visible: s.toggle_resolution_menu()
            if s.light_menu_visible: s.toggle_light_menu()
            s.shutdown_menu.place(relx=1.0, x=0, y=0, anchor='ne', relheight=1.0); s.shutdown_menu_visible=True
            s.start_menu_timeout()
            
    def toggle_rotation(s):
        s.bild_rotiert = not s.bild_rotiert
        
    def reset_zoom(s): s.zoom_slider.set(1.0); s.zoom_center_x=0.5; s.zoom_center_y=0.5
    def update_zoom(s, v): s.zoom_level=float(v); s.zoom_label.config(text=f"{s.zoom_level:.1f}x")
    def apply_exposure(s):
        try:
            if s.manual_mode: s.picam2.set_controls({"ExposureTime":s.exposure_time})
        except: pass
    def apply_gain(s):
        try:
            if s.manual_mode: s.picam2.set_controls({"AnalogueGain":s.analog_gain})
        except: pass
    def set_auto_mode(s):
        s.manual_mode=False
        try: s.picam2.set_controls({"AeEnable":True, "AwbEnable":True}); s.auto_btn.config(bg='#408040'); s.manual_btn.config(bg='#305050')
        except: pass
    def set_manual_mode(s):
        s.manual_mode=True
        try: s.picam2.set_controls({"AeEnable":False, "AwbEnable":False, "ExposureTime":s.exposure_time, "AnalogueGain":s.analog_gain}); s.auto_btn.config(bg='#505050'); s.manual_btn.config(bg='#408040')
        except: pass
        
    def pan_move(s, e):
        if s.pan_active and s.zoom_level>1.0:
            dx=e.x-s.last_pan_x; dy=e.y-s.last_pan_y; w=s.canvas.winfo_width(); h=s.canvas.winfo_height()
            if w>1 and h>1:
                mf=0.0003*s.zoom_level; s.zoom_center_x-=dx*mf; s.zoom_center_y-=dy*mf
                mg=0.5/s.zoom_level; s.zoom_center_x=max(mg,min(1.0-mg,s.zoom_center_x)); s.zoom_center_y=max(mg,min(1.0-mg,s.zoom_center_y))
            s.last_pan_x=e.x; s.last_pan_y=e.y
            
    def foto_machen(s):
        if s.current_frame is not None:
            ts=datetime.now().strftime("%Y%m%d_%H%M%S"); fn=os.path.join(s.foto_dir, f"foto_{ts}.jpg")
            cv2.imwrite(fn, cv2.cvtColor(s.current_frame, cv2.COLOR_RGB2BGR))
            s.foto_status.config(text="✓ Gespeichert")
            s.root.after(3000, lambda: s.foto_status.config(text=""))
            
    def change_resolution(s, res):
        if res==s.current_resolution: return
        try:
            s.running=False; time.sleep(0.2); s.picam2.stop()
            config = s.picam2.create_preview_configuration(main={"size":res}, buffer_count=2)
            config["transform"] = LibcameraTransform(hflip=1, vflip=1)
            s.picam2.configure(config)
            s.picam2.start(); time.sleep(0.5); s.current_resolution=res
            for r,b in s.res_btns.items(): b.config(bg='#408040' if r==res else '#505050')
            s.running=True
            if s.res_menu_visible: s.toggle_resolution_menu()
        except: s.running=True
            
    def set_light(s, mode):
        s.light_mode=mode
        if not GPIO_AVAILABLE: return
        try:
            if mode=="aus": GPIO.output(17,GPIO.LOW); GPIO.output(27,GPIO.LOW); s.light_aus_btn.config(bg='#408040'); s.light_kalt_btn.config(bg='#505050'); s.light_warm_btn.config(bg='#505050')
            elif mode=="kalt": GPIO.output(17,GPIO.HIGH); GPIO.output(27,GPIO.LOW); s.light_aus_btn.config(bg='#505050'); s.light_kalt_btn.config(bg='#408040'); s.light_warm_btn.config(bg='#505050')
            elif mode=="warm": GPIO.output(17,GPIO.LOW); GPIO.output(27,GPIO.HIGH); s.light_aus_btn.config(bg='#505050'); s.light_kalt_btn.config(bg='#505050'); s.light_warm_btn.config(bg='#408040')
        except: pass
        
    def do_shutdown(s):
        if s.shutdown_menu_visible: s.toggle_shutdown_menu()
        s.running=False
        if GPIO_AVAILABLE:
            try: GPIO.output(17,GPIO.LOW); GPIO.output(27,GPIO.LOW); GPIO.cleanup()
            except: pass
        try: s.picam2.stop()
        except: pass
        subprocess.run(["sudo","shutdown","-h","now"])
        
    def beenden(s):
        s.running=False
        if GPIO_AVAILABLE:
            try: GPIO.output(17,GPIO.LOW); GPIO.output(27,GPIO.LOW); GPIO.cleanup()
            except: pass
        try: s.picam2.stop()
        except: pass
        s.root.quit(); s.root.destroy()
        
    def bildanpassung(s, f):
        if s.brightness!=0 or s.contrast!=1.0: f=cv2.convertScaleAbs(f, alpha=s.contrast, beta=s.brightness)
        if s.saturation!=1.0:
            hsv=cv2.cvtColor(f, cv2.COLOR_RGB2HSV).astype(np.float32)
            hsv[:,:,1]=np.clip(hsv[:,:,1]*s.saturation, 0, 255)
            f=cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB)
        return f
        
    def zoom_bild(s, f):
        if s.zoom_level>1.0:
            h,w=f.shape[:2]; cx=int(w*s.zoom_center_x); cy=int(h*s.zoom_center_y)
            nw=int(w/s.zoom_level); nh=int(h/s.zoom_level)
            x1=max(0,cx-nw//2); y1=max(0,cy-nh//2); x2=min(w,x1+nw); y2=min(h,y1+nh)
            if x2-x1<nw: x1=max(0,w-nw) if x1!=0 else 0; x2=min(w,nw)
            if y2-y1<nh: y1=max(0,h-nh) if y1!=0 else 0; y2=min(h,nh)
            f=cv2.resize(f[y1:y2,x1:x2], (w,h), interpolation=cv2.INTER_LANCZOS4)
        return f
        
    def update_bild(s):
        while s.running:
            try:
                f=s.picam2.capture_array()
                
                # Extra-Rotation falls gewünscht (zusätzlich zu Kamera-Transform)
                if not s.bild_rotiert:
                    f=cv2.rotate(f, cv2.ROTATE_180)
                
                f=s.zoom_bild(f); f=s.bildanpassung(f); s.current_frame=f.copy()
                s.frame_count+=1; ct=time.time()
                if ct-s.fps_time>=1.0: s.fps=s.frame_count; s.frame_count=0; s.fps_time=ct; s.fps_label.config(text=f"FPS: {s.fps}")
                cw=s.canvas.winfo_width(); ch=s.canvas.winfo_height()
                if cw>1 and ch>1:
                    # Seitenverhältnis beibehalten
                    h,w=f.shape[:2]
                    scale=min(cw/w, ch/h)
                    new_w=int(w*scale)
                    new_h=int(h*scale)
                    f=cv2.resize(f, (new_w,new_h), interpolation=cv2.INTER_LINEAR)
                    
                    img=ImageTk.PhotoImage(image=Image.fromarray(f))
                    s.canvas.create_image(cw//2, ch//2, image=img, anchor=tk.CENTER)
                    s.canvas.imgtk=img
            except: pass

if __name__=="__main__":
    root=tk.Tk()
    app=Loetmikroskop(root)
    root.mainloop()