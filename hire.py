import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageDraw
import json, os
from datetime import datetime, timedelta

import itertools


# Default achievement thresholds (1 → A ... 26 → Z)
ACHIEVEMENT_THRESHOLDS = [
    (1, "Starter"),
    (5, "Helper"),
    (10, "Experienced"),
    (20, "Pro"),
    (50, "Expert"),
    (100, "Master"),
]

def show_achievement_popup(achievement_name):
    slide = ctk.CTkToplevel(window)
    slide.overrideredirect(True)
    slide.attributes("-topmost", True)
    slide.attributes("-alpha", 1.0)

    h = 100
    screen_w = slide.winfo_screenwidth()
    screen_h = slide.winfo_screenheight()

    max_width = screen_w
    y = int(screen_h / 2 - h / 2)

    slide.configure(fg_color="#000000")
    slide.geometry(f"{max_width}x{h}+0+{y}")

    congrats_text = "🎉 CONGRATULATIONS! 🎉"
    congrats_shadow = ctk.CTkLabel(slide, text=congrats_text,
                                   font=("Arial Black", 34, "bold"),
                                   text_color="black")
    congrats_shadow.place(relx=0.5, rely=0.5, anchor="center", x=2, y=2)

    congrats_label = ctk.CTkLabel(slide, text=congrats_text,
                                  font=("Arial Black", 34, "bold"),
                                  text_color="white")
    congrats_label.place(relx=0.5, rely=0.5, anchor="center")

    rainbow_colors = ["#FF0000", "#FF7F00", "#FFFF00", "#00FF00",
                      "#0000FF", "#4B0082", "#8B00FF"]
    color_cycle = itertools.cycle(rainbow_colors)

    def cycle_colors():
        if not congrats_label.winfo_exists():
            return
        congrats_label.configure(text_color=next(color_cycle))
        slide.after(100, cycle_colors)

    cycle_colors()

    def fade_out(alpha=1.0):
        if not slide.winfo_exists():
            return
        alpha -= 0.05
        if alpha > 0:
            slide.attributes("-alpha", alpha)
            slide.after(50, lambda: fade_out(alpha))
        else:
            if slide.winfo_exists():
                slide.destroy()
            if slide.winfo_exists():
                slide.destroy()
            show_achievement_unlocked(achievement_name)

    slide.after(1500, fade_out)


def show_achievement_unlocked(achievement_name):
    unlocked = ctk.CTkToplevel(window)
    unlocked.overrideredirect(True)
    unlocked.attributes("-topmost", True)
    unlocked.attributes("-alpha", 0.95)
    unlocked.configure(fg_color="#111111")

    h = 50
    w = 620
    screen_w = unlocked.winfo_screenwidth()
    screen_h = unlocked.winfo_screenheight()

    y = int(screen_h * 0.18)
    x = (screen_w - w) // 2
    unlocked.geometry(f"{w}x{h}+{x}+{y}")

    text = f"🏆 Successfully Achieved the Achievement: {achievement_name}"

    shadow = ctk.CTkLabel(unlocked, text=text,
                          font=("Arial Black", 18, "bold"),
                          text_color="black")
    shadow.place(relx=0.5, rely=0.5, anchor="center", x=1, y=1)

    label = ctk.CTkLabel(unlocked, text=text,
                         font=("Arial Black", 18, "bold"),
                         text_color="#FFFFFF")
    label.place(relx=0.5, rely=0.5, anchor="center")

    def fade_out(alpha=0.95):
        if not unlocked.winfo_exists():
            return
        alpha -= 0.05
        if alpha > 0:
            unlocked.attributes("-alpha", alpha)
            unlocked.after(50, lambda: fade_out(alpha))
        else:
            if unlocked.winfo_exists():
                unlocked.destroy()
            if unlocked.winfo_exists():
                unlocked.destroy()

    unlocked.after(2000, fade_out)


# Files
MESSAGES_FILE = "messages.json"
PROFILES_FILE = "profile.json"
REQUESTS_FILE = "requests.json"

def ensure_file(path, default):
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(default, f, indent=4)

def load_json(path):
    ensure_file(path, [])
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

ensure_file(MESSAGES_FILE, [])
ensure_file(PROFILES_FILE, [])
ensure_file(REQUESTS_FILE, [])

def load_messages():
    return load_json(MESSAGES_FILE)

def save_messages(msgs):
    save_json(MESSAGES_FILE, msgs)

def save_message(msg):
    # Ensure chat_id exists for conversation grouping
    if "chat_id" not in msg or not msg["chat_id"]:
        msg["chat_id"] = msg.get("to") or msg.get("from") or "unknown"
    msgs = load_messages()
    msgs.append(msg)
    save_messages(msgs)

def load_profiles():
    return load_json(PROFILES_FILE)

def save_profiles(profiles):
    save_json(PROFILES_FILE, profiles)

def load_requests():
    return load_json(REQUESTS_FILE)

def save_requests(reqs):
    save_json(REQUESTS_FILE, reqs)

# App state and UI setup

# --- Notification Red Dot Handling ---
notification_red_dot = None



def update_notification_dot():
    global notification_red_dot
    try:
        unread_msgs = [m for m in load_messages() if not m.get("read", False)]
        pending_requests = load_requests()

        # Remove old dot if exists
        if notification_red_dot:
            notification_red_dot.destroy()
            notification_red_dot = None

        if unread_msgs or pending_requests:
            # Create perfect circular red dot at bottom-right of bell
            size = 12
            notification_red_dot = ctk.CTkLabel(
                bell_button,
                text="",
                width=size,
                height=size,
                fg_color="#ff0000",
                corner_radius=size//2
            )
            notification_red_dot.place(relx=1, rely=1, anchor="se")
    except Exception as e:
        print("update_notification_dot error:", e)

def create_button(master, **kwargs):
    kwargs.setdefault("fg_color", "#222222")
    kwargs.setdefault("border_width", 1)
    kwargs.setdefault("border_color", "#555555")
    kwargs.setdefault("hover_color", "#333333")
    return ctk.CTkButton(master, **kwargs)

def circle_mask_with_border(pil_image, size=(60,60), border=4, online=False):
    try:
        img = pil_image.resize((size[0]-2*border, size[1]-2*border)).convert("RGBA")
    except Exception:
        img = Image.open(DEFAULT_AVATAR).resize((size[0]-2*border, size[1]-2*border)).convert("RGBA")
    mask = Image.new("L", img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0,0,img.size[0], img.size[1]), fill=255)
    img.putalpha(mask)
    base = Image.new("RGBA", size, (0,0,0,0))
    border_draw = ImageDraw.Draw(base)
    border_color = (0,200,0) if online else (255,255,255)
    border_draw.ellipse((0,0,size[0]-1,size[1]-1), outline=border_color, width=border)
    base.paste(img, (border,border), img)
    return base


def get_current_profile_name():
    """
    Returns the best-guess current profile name.
    Tries: current_profile_name -> a profile marked as self/owner -> first profile -> None.
    """
    try:
        # Use existing global if already set
        if 'current_profile_name' in globals() and current_profile_name:
            return current_profile_name
    except Exception:
        pass
    # Load profiles and try to find a likely "me" profile
    try:
        plist = profiles if 'profiles' in globals() and profiles else load_profiles()
    except Exception:
        plist = []
    # Prefer a profile that looks like the user
    for p in plist or []:
        if p.get('is_me') or p.get('owner') or p.get('self'):
            return p.get('name') or p.get('username') or p.get('display_name') or p.get('profile_name')
    # Fallback to first profile if available
    if plist:
        first = plist[0]
        return first.get('name') or first.get('username') or first.get('display_name') or first.get('profile_name')
    return None
def find_profile_by_name(name):
    if not name:
        return None
    # Ensure we have the latest profiles loaded
    global profiles
    try:
        candidates = profiles if profiles else load_profiles()
    except Exception:
        candidates = load_profiles()
    target = str(name).strip().lower()
    for p in candidates or []:
        for key in ("name", "username", "display_name", "profile_name"):
            val = str(p.get(key, "")).strip().lower()
            if val == target:
                return p
    return None
    for p in profiles:
        if p.get("name","").lower() == name.lower():
            return p
    return None

def check_award_achievements(profile, all_profiles=None):
    if profile is None:
        return
    newly_awarded = []
    for thresh, name in ACHIEVEMENT_THRESHOLDS:
        if profile.get("hire_count", 0) >= thresh and name not in profile.get("achievements", []):
            profile.setdefault("achievements", []).append(name)
            newly_awarded.append(name)
    if newly_awarded:
        if all_profiles:
            save_profiles(all_profiles)
        for ach in newly_awarded:
            save_message({
                "chat_id": profile.get("name"),
                "to": profile.get("name"),
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "read": False
            })
            show_achievement_popup(ach)

# UI pieces
def show_accept_popup(request):
    popup = ctk.CTkToplevel(window)
    popup.title("Hire Accepted")
    popup.geometry("420x180+420+220")
    popup.grab_set()

    ctk.CTkLabel(popup, text="🎉 Hire Accepted!", font=("Arial", 20, "bold")).pack(pady=(10,4))
    text = f"{request.get('to')} accepted your hire request from {request.get('from_username')}. They accepted at {request.get('accepted_time', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}."
    ctk.CTkLabel(popup, text=text, wraplength=460, justify="left").pack(pady=6)

    btnf = ctk.CTkFrame(popup, fg_color="transparent")
    btnf.pack(pady=10)

    def open_chat_from_popup():
        popup.destroy()
        open_chat_box(request.get("to"), chat_id=request.get("chat_id") or request.get("to"))

    create_button(btnf, text="Open Chat", width=140, height=40, command=open_chat_from_popup).pack(side="left", padx=8)
    create_button(btnf, text="Dismiss", width=120, height=40, command=popup.destroy).pack(side="left", padx=8)


def show_emergency_accept_popup(request):
    popup = ctk.CTkToplevel(window)
    popup.title("Emergency Accepted")
    popup.geometry("460x220+420+220")
    popup.grab_set()

    # fallback to current_profile_name if missing
    acceptor_name = request.get("accepted_by") or get_current_profile_name() or "Unknown"

    ctk.CTkLabel(popup, text="🚨 Emergency Request Accepted!", font=("Arial", 20, "bold")).pack(pady=(10,6))
    ctk.CTkLabel(popup,
                 text=f"Your emergency request has been accepted by {acceptor_name}.",
                 font=("Arial", 14), wraplength=440, justify="center").pack(pady=6)
    ctk.CTkLabel(popup, text="You can start contacting them.",
                 font=("Arial", 12, "italic"), text_color="#aaa").pack(pady=4)

    btnf = ctk.CTkFrame(popup, fg_color="transparent")
    btnf.pack(pady=12)

    def open_profile_from_popup():
        popup.destroy()
        prof = find_profile_by_name(acceptor_name)
        if prof:
            open_profile(prof)
        else:
            messagebox.showinfo("Not Found", f"Profile for {acceptor_name} not found.")

    create_button(btnf, text="Open Profile", width=140, height=40, command=open_profile_from_popup).pack(side="left", padx=8)
    create_button(btnf, text="Dismiss", width=120, height=40, command=popup.destroy).pack(side="left", padx=8)

def open_conversations():
    conv_win = ctk.CTkToplevel(window)
    conv_win.title("Conversations")
    conv_win.geometry("520x580+300+120")
    conv_win.grab_set()
    ctk.CTkLabel(conv_win, text="Conversations", font=("Arial", 20, "bold")).pack(pady=10)
    scroll = ctk.CTkScrollableFrame(conv_win, width=480, height=460)
    scroll.pack(padx=8, pady=8)
    messages = load_messages()
    grouped = {}
    for msg in messages:
        cid = msg.get("chat_id") or msg.get("to") or msg.get("from")
        if not cid:
            continue
        if cid not in grouped or msg.get("time","") > grouped[cid].get("time",""):
            grouped[cid] = msg
    items = sorted(grouped.values(), key=lambda x: x.get("time",""), reverse=True)
    for itm in items:
        partner = itm.get("chat_id") or itm.get("to") or itm.get("from")
        frame = ctk.CTkFrame(scroll, fg_color="#2c2c2c", corner_radius=10)
        frame.pack(fill="x", pady=6, padx=6)
        ctk.CTkLabel(frame, text=partner, font=("Arial", 16, "bold")).pack(side="left", padx=10)
        def open_chat_for(n=partner):
            conv_win.destroy()
            open_chat_box(n, chat_id=n)
        create_button(frame, text="Open Chat", width=110, height=34, command=open_chat_for).pack(side="right", padx=10)
        def make_delete(n=partner):
            def do_delete():
                msgs = load_messages()
                msgs = [m for m in msgs if m.get("chat_id") != n]
                save_messages(msgs)
                conv_win.destroy()
                open_conversations()
            return do_delete
        create_button(frame, text="Delete", width=110, height=34, command=make_delete()).pack(side="right", padx=10)

# Chat window
def open_chat_box(partner_name, chat_id=None):
    if chat_id is None:
        chat_id = partner_name
    partner_profile = find_profile_by_name(partner_name)
    chat_win = ctk.CTkToplevel(window)
    chat_win.title(f"Chat — {partner_name}")
    chat_win.geometry("620x700+300+80")
    chat_win.grab_set()

    header = ctk.CTkFrame(chat_win, fg_color="#101010")
    header.pack(fill="x")
    if partner_profile:
        try:
            pil_img = Image.open(partner_profile.get("image", DEFAULT_AVATAR))
            circ = circle_mask_with_border(pil_img, (60,60), border=4, online=partner_profile.get("online", False))
            img = ctk.CTkImage(circ, size=(60,60))
            ctk.CTkLabel(header, image=img, text="").pack(side="left", padx=8, pady=8)
        except Exception:
            pass
    name_label = partner_name
    if partner_profile and partner_profile.get("equipped_achievement"):
        name_label += f" 🏆 {partner_profile.get('equipped_achievement')}"
    ctk.CTkLabel(header, text=name_label, font=("Arial", 18, "bold")).pack(side="left", padx=8)

    def chat_options():
        opt_win = ctk.CTkToplevel(chat_win)
        opt_win.title("Options")
        opt_win.geometry("320x200+700+220")
        opt_win.grab_set()
        ctk.CTkLabel(opt_win, text="Send Hire Request", font=("Arial", 14, "bold")).pack(pady=8)
        ctk.CTkLabel(opt_win, text="Enter your username (this will be shown to the profile owner):", font=("Arial", 12)).pack(pady=4)
        username_var = ctk.StringVar()
        username_entry = ctk.CTkEntry(opt_win, textvariable=username_var, width=260, placeholder_text="Your username")
        username_entry.pack(pady=6)
        def send_request():
            uname = username_var.get().strip()
            if not uname:
                messagebox.showwarning("Error", "Enter a username.", parent=opt_win)
                return
            reqs = load_requests()
            for r in reqs:
                if r.get("from_username")==uname and r.get("to")==partner_name and r.get("status")=="pending":
                    try:
                        last_time = datetime.strptime(r.get("time"), "%Y-%m-%d %H:%M:%S")
                        if datetime.now() - last_time < timedelta(hours=3):
                            messagebox.showwarning("Limit", "You can only send one request to this user every 3 hours.", parent=opt_win)
                            return
                    except Exception:
                        pass
            req = {"to": partner_name, "from_username": uname, "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "status":"pending", "chat_id": chat_id}
            reqs.append(req)
            save_requests(reqs)
            update_notification_dot()
            messagebox.showinfo("Sent", "Hire request sent.", parent=opt_win)
            opt_win.destroy()
        create_button(opt_win, text="Send Request", width=140, height=38, command=send_request).pack(pady=8)
    create_button(header, text="⋮", width=42, height=38, command=chat_options).pack(side="right", padx=8, pady=8)

    last_lbl = ctk.CTkLabel(chat_win, text=f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", font=("Arial", 11))
    last_lbl.pack(pady=(6,0))
    msgs_frame = ctk.CTkScrollableFrame(chat_win, width=580, height=460)
    msgs_frame.pack(padx=10, pady=8)

    def add_bubble(sender, text):
        if sender == "You":
            bg = "#D1FFD6"
            anchor = "e"
        else:
            bg = "#F1F1F1"
            anchor = "w"
        bubble = ctk.CTkFrame(msgs_frame, fg_color=bg, corner_radius=12)
        lbl = ctk.CTkLabel(bubble, text=f"{sender}: {text}", wraplength=420, anchor="w", justify="left", text_color="black")
        lbl.pack(padx=10, pady=8)
        if anchor == "e":
            bubble.pack(anchor="e", padx=12, pady=6)
        else:
            bubble.pack(anchor="w", padx=12, pady=6)
        try:
            msgs_frame.update_idletasks()
            msgs_frame._canvas.yview_moveto(1.0)
        except Exception:
            pass

    messages = load_messages()
    history = [m for m in messages if m.get("chat_id") == chat_id]
    history.sort(key=lambda x: x.get("time",""))
    for m in history:
        sender = m.get("from") if m.get("from") else ("You" if m.get("to")==partner_name else partner_name)
        add_bubble(sender, m.get("text",""))

    changed = False
    msgs_all = load_messages()
    for m in msgs_all:
        if m.get("chat_id")==chat_id and m.get("to")=="You" and not m.get("read"):
            m["read"] = True
            changed = True
    if changed:
        save_messages(msgs_all)
        update_notification_dot()

    bottom_frame = ctk.CTkFrame(chat_win, fg_color="transparent")
    bottom_frame.pack(side="bottom", fill="x", pady=8, padx=10)
    msg_entry = ctk.CTkTextbox(bottom_frame, width=420, height=110, fg_color="white", text_color="black", font=("Arial", 14))
    msg_entry.pack(side="left", padx=(0,8))
    btns_frame = ctk.CTkFrame(bottom_frame, fg_color="transparent")
    btns_frame.pack(side="right", padx=6)

    def send_msg():
        text = msg_entry.get("1.0", "end").strip()
        if not text and not image_path:
            messagebox.showwarning("Error", "Message cannot be empty.", parent=chat_win)
            return
        m = {"chat_id": chat_id, "to": partner_name, "text": text, "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "from": "You", "read": False}
        save_message(m)
        update_notification_dot()
        add_bubble("You", text)
        msg_entry.delete("1.0", "end")
        last_lbl.configure(text=f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    def clear_entry():
        msg_entry.delete("1.0", "end")

    def back_to_profiles():
        chat_win.destroy()
        view_profiles_page()

    create_button(btns_frame, text="Send", width=120, height=44, corner_radius=14, command=send_msg).pack(pady=6)
    create_button(btns_frame, text="Clear", width=100, height=44, corner_radius=14, command=clear_entry).pack(pady=6)
    create_button(btns_frame, text="Back", width=100, height=44, corner_radius=14, command=back_to_profiles).pack(pady=6)

# Main pages, profiles, notifications, etc.
def main_page():
    for w in window.winfo_children():
        w.destroy()
    ctk.CTkLabel(window, text="Welcome To SHX :)", font=("Arial", 32, "bold")).pack(pady=30)
    create_button(window, text="Smart Hire", width=360, height=70, font=ctk.CTkFont(size=22, weight="bold"), command=view_profiles_page, corner_radius=25).pack(pady=20)
    
    # Emergency Request button (packed under Smart Hire)
    create_button(window, text="Emergency Request", width=360, height=50, font=ctk.CTkFont(size=20), command=open_emergency_request, corner_radius=20).pack(pady=6)
    menu_button = create_button(window, text="⋮", width=56, height=56, font=ctk.CTkFont(size=28), command=open_menu, corner_radius=28)
    menu_button.place(x=16, y=14)
    emergency_button = create_button(window, text="Emergency Request", width=200, height=40,
                                     font=ctk.CTkFont(size=16), command=open_emergency_request)

    global bell_button
    bell_button = create_button(window, text="🔔", width=56, height=56, font=ctk.CTkFont(size=24), command=show_notifications, corner_radius=28)
    bell_button.place(x=872, y=14)
    # schedule notification dot update after widgets have geometry
    window.after(120, update_notification_dot)

def open_menu():
    menu = ctk.CTkToplevel(window)
    menu.geometry("200x360+40+60")
    menu.title("Menu")
    menu.grab_set()
    def close_menu():
        menu.grab_release()
        menu.destroy()
    if not profiles:
        create_button(menu, text="Create Profile", command=lambda: (menu.destroy(), create_profile()), width=170, height=40, corner_radius=15).pack(pady=6)
    valid_profile = next((p for p in profiles if "age" in p and "address" in p), None)
    if valid_profile:
        create_button(menu, text="Edit Profile", command=lambda: (menu.destroy(), create_profile(edit_profile=valid_profile)), width=170, height=40, corner_radius=15).pack(pady=6)
        create_button(menu, text="Saved Profiles", command=lambda: (menu.destroy(), view_profiles_page(saved_only=True)), width=170, height=40, corner_radius=15).pack(pady=6)
    create_button(menu, text="Conversations", command=lambda: (menu.destroy(), open_conversations()), width=170, height=40, corner_radius=15).pack(pady=6)
    create_button(menu, text="Leaderboard", command=lambda: (menu.destroy(), leaderboard_page("week")), width=170, height=40, corner_radius=15).pack(pady=6)
    create_button(menu, text="Achievements", command=lambda: (menu.destroy(), open_achievements_page(get_current_profile_name())), width=170, height=40, corner_radius=15).pack(pady=6)


def show_notifications():
    notif_win = ctk.CTkToplevel(window)
    notif_win.title("Notifications")
    notif_win.geometry("760x520+200+100")
    notif_win.grab_set()

    ctk.CTkLabel(notif_win, text="Notifications", font=("Arial", 20, "bold")).pack(pady=8)

    tab_frame = ctk.CTkFrame(notif_win, fg_color="#1a1a1a")
    tab_frame.pack(fill="x", padx=10, pady=5)

    current_tab = ctk.StringVar(value="Unread")

    def switch_tab(tab):
        current_tab.set(tab)
        refresh_list()

    create_button(tab_frame, text="Unread", command=lambda: switch_tab("Unread"), width=120, height=35).pack(side="left", padx=8, pady=8)
    create_button(tab_frame, text="Read", command=lambda: switch_tab("Read"), width=120, height=35).pack(side="left", padx=8, pady=8)
    create_button(tab_frame, text="Hire Requests", command=lambda: switch_tab("Requests"), width=160, height=35).pack(side="left", padx=8, pady=8)
    create_button(tab_frame, text="Emergency", command=lambda: switch_tab("Emergency"), width=160, height=35).pack(side="left", padx=8, pady=8)

    body = ctk.CTkFrame(notif_win, fg_color="#121212")
    body.pack(fill="both", expand=True, padx=10, pady=10)

    canvas = ctk.CTkCanvas(body, bg="#121212", highlightthickness=0)
    canvas.pack(side="left", fill="both", expand=True)

    scrollbar = ctk.CTkScrollbar(body, orientation="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")

    list_frame = ctk.CTkFrame(canvas, fg_color="#121212")

    # --- Hire Request helpers (scoped to Notifications window) ---
    def remove_request(req):
        reqs = load_requests()
        reqs = [r for r in reqs if not (('title' not in r) and r.get('to')==req.get('to') and r.get('from_username')==req.get('from_username') and r.get('time')==req.get('time'))]
        save_requests(reqs)
        update_notification_dot()
        try:
            refresh_list()
        except Exception:
            pass

    def accept_request(req):
        reqs = load_requests()
        updated = False
        for r in reqs:
            if ('title' not in r) and r.get('to')==req.get('to') and r.get('from_username')==req.get('from_username') and r.get('time')==req.get('time'):
                r['status'] = 'accepted'
                r['accepted_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                updated = True
                break
        if updated:
            save_requests(reqs)
            update_notification_dot()
            try:
                all_profiles = load_profiles()
                prof = next((p for p in all_profiles if p.get("name","").lower() == req.get("to","").lower()), None)
                if prof is not None:
                    prof["hire_count"] = prof.get("hire_count", 0) + 1
                    check_award_achievements(prof, all_profiles)
                    save_profiles(all_profiles)
            except Exception as e:
                print("accept_request achievement error:", e)
            try:
                refresh_list()
            except Exception:
                pass
            try:
                show_accept_popup(req)
            except Exception:
                pass

    def decline_request(req):
        reqs = load_requests()
        reqs = [r for r in reqs if not (('title' not in r) and r.get('to')==req.get('to') and r.get('from_username')==req.get('from_username') and r.get('time')==req.get('time'))]
        save_requests(reqs)
        update_notification_dot()
        try:
            refresh_list()
        except Exception:
            pass
    list_window = canvas.create_window((0,0), window=list_frame, anchor="nw")

    canvas.configure(yscrollcommand=scrollbar.set)
    def on_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    list_frame.bind("<Configure>", on_configure)

    def mark_as_read_for_profile(profile_name):
        messages = load_messages()
        changed = False
        for m in messages:
            if m.get("to") == profile_name and not m.get("read"):
                m["read"] = True
                changed = True
        if changed:
            save_messages(messages)
        update_notification_dot()
        refresh_list()

    def delete_messages_for_profile(profile_name):
        messages = load_messages()
        messages = [m for m in messages if m.get("to") != profile_name]
        save_messages(messages)
        refresh_list()

    def refresh_list():
        for child in list_frame.winfo_children():
            child.destroy()

        # Build entries based on tab
        if current_tab.get() in ("Unread", "Read"):
            messages = load_messages()
            grouped = {}
            for m in messages:
                name = m.get("to")
                if name not in grouped or m.get("time","") > grouped[name].get("time",""):
                    grouped[name] = m
            entries = [v for v in grouped.values() if (not v.get("read"))] if current_tab.get() == "Unread" else [v for v in grouped.values() if v.get("read")]
        elif current_tab.get() == "Requests":
            entries = [r for r in load_requests() if "title" not in r]
        elif current_tab.get() == "Emergency":
            entries = [r for r in load_requests() if "title" in r]
        else:
            entries = []

        entries.sort(key=lambda x: x.get("time",""), reverse=True)

        for item in entries:
            frame = ctk.CTkFrame(list_frame, fg_color="#222", corner_radius=10)
            frame.pack(fill="x", padx=8, pady=6)

            # Messaging tabs
            if current_tab.get() in ("Unread","Read"):
                ctk.CTkLabel(frame, text=f"{item.get('to')}", font=("Arial", 14, "bold")).pack(anchor="w", padx=8, pady=2)
                ctk.CTkLabel(frame, text=item.get("text",""), wraplength=650, justify="left").pack(anchor="w", padx=8)
                ctk.CTkLabel(frame, text=f"{item.get('time','')}", font=("Arial", 11), text_color="#888").pack(anchor="w", padx=8, pady=3)

                btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
                btn_frame.pack(anchor="e", padx=8, pady=5)
                create_button(btn_frame, text="Open Chat", width=110, height=34,
                              command=lambda n=item.get('to'): open_chat_box(n, chat_id=n)).pack(side="right", padx=6)
                if current_tab.get() == "Unread":
                    create_button(btn_frame, text="Mark Read", width=110, height=34,
                                  command=lambda n=item.get('to'): mark_as_read_for_profile(n)).pack(side="right", padx=6)
                else:
                    create_button(btn_frame, text="Delete", width=110, height=34,
                                  command=lambda n=item.get('to'): delete_messages_for_profile(n)).pack(side="right", padx=6)

            
            # Hire Requests
            elif current_tab.get() == "Requests":
                # Only non-emergency requests (no "title" field) are shown here;
                # entries were already filtered above in the existing code.
                ctk.CTkLabel(frame, text=f"Hire request from: {item.get('from_username')}", font=("Arial", 14, "bold")).pack(anchor="w", padx=8, pady=2)
                ctk.CTkLabel(frame, text=f"To: {item.get('to')}", font=("Arial", 12)).pack(anchor="w", padx=8)
                ctk.CTkLabel(frame, text=f"Time: {item.get('time','')}", font=("Arial", 11), text_color="#888").pack(anchor="w", padx=8, pady=3)

                status = item.get("status")
                if status == "accepted":
                    try:
                        frame.configure(fg_color="#2e7d32")
                    except Exception:
                        pass
                    btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
                    btn_frame.pack(anchor="e", padx=8, pady=5)
                    create_button(btn_frame, text="Open Chat", width=110, height=34, command=lambda it=item: open_chat_box(it.get('to'), chat_id=it.get('chat_id') or it.get('to'))).pack(side="right", padx=6)
                    create_button(btn_frame, text="Remove", width=100, height=34, command=lambda it=item: remove_request(it)).pack(side="right", padx=6)
                else:
                    btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
                    btn_frame.pack(anchor="e", padx=8, pady=5)
                    create_button(btn_frame, text="Accept", width=100, height=34, command=lambda it=item: accept_request(it)).pack(side="right", padx=6)
                    create_button(btn_frame, text="Decline", width=100, height=34, command=lambda it=item: decline_request(it)).pack(side="right", padx=6)

            # Emergency Requests

            elif current_tab.get() == "Emergency":
                ctk.CTkLabel(frame, text=f"🚨 {item.get('title')}", font=("Arial", 14, "bold")).pack(anchor="w", padx=8, pady=2)
                ctk.CTkLabel(frame, text=f"From: {item.get('from_username')} | Address: {item.get('address')}", font=("Arial", 12)).pack(anchor="w", padx=8)

                ctk.CTkLabel(frame, text=f"Occupation: {item.get('occupation')}", font=("Arial", 12)).pack(anchor="w", padx=8)
                # Added by patch: show Contact and Description for Emergency items
                ctk.CTkLabel(frame, text=f"Contact: {item.get('contact','')}", font=("Arial", 12)).pack(anchor="w", padx=8)
                ctk.CTkLabel(frame, text=f"Description: {item.get('description','')}", font=("Arial", 12), wraplength=460, justify="left").pack(anchor="w", padx=8, pady=(2,0))
                ctk.CTkLabel(frame, text=f"Time: {item.get('time','')}", font=("Arial", 11), text_color="#888").pack(anchor="w", padx=8, pady=3)

                btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
                btn_frame.pack(anchor="e", padx=8, pady=5)

                if item.get("status") == "accepted":
                    frame.configure(fg_color="#1d3d1d")
                    ctk.CTkLabel(frame, text="✅ Accepted", font=("Arial", 12, "bold"), text_color="#6f6").pack(anchor="w", padx=8, pady=2)
                    def dismiss_emergency(req=item):
                        reqs = [r for r in load_requests() if not (r.get("time")==req.get("time") and r.get("title")==req.get("title"))]
                        save_requests(reqs)
                        update_notification_dot()
                        refresh_list()
                    create_button(btn_frame, text="Dismiss", width=100, height=34, command=dismiss_emergency).pack(side="right", padx=6)
                else:
                    def accept_emergency(req=item):
                        reqs = load_requests()
                        updated_obj = None
                        # Determine acceptor name robustly
                        acceptor_name = get_current_profile_name()
                        for r in reqs:
                            if r.get("time") == req.get("time") and r.get("title") == req.get("title"):
                                r["status"] = "accepted"
                                r["accepted_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                if acceptor_name:
                                    r["accepted_by"] = acceptor_name
                                    req["accepted_by"] = acceptor_name  # sync local copy
                                updated_obj = r
                                break
                        save_requests(reqs)
                        update_notification_dot()
                        refresh_list()
                        show_emergency_accept_popup(updated_obj or req)
                    def decline_emergency(req=item):
                        reqs = [r for r in load_requests() if not (r.get("time")==req.get("time") and r.get("title")==req.get("title"))]
                        save_requests(reqs)
                        update_notification_dot()
                        refresh_list()

                    create_button(btn_frame, text="Accept", width=100, height=34, command=accept_emergency).pack(side="right", padx=6)
                    create_button(btn_frame, text="Decline", width=100, height=34, command=decline_emergency).pack(side="right", padx=6)

    refresh_list()
def create_profile(edit_profile=None):
    global current_profile_name
    for w in window.winfo_children():
        w.destroy()
    title_text = "Edit Profile" if edit_profile else "Create Profile"
    ctk.CTkLabel(window, text=title_text, font=("Arial", 26, "bold")).pack(pady=10)
    frame = ctk.CTkFrame(window, corner_radius=20, fg_color="#1c1c1c")
    frame.pack(pady=10)
    name_entry = ctk.CTkEntry(frame, placeholder_text="Enter Name", width=300, height=40)
    name_entry.pack(pady=8)
    age_entry = ctk.CTkEntry(frame, placeholder_text="Enter Age", width=300, height=40)
    age_entry.pack(pady=8)
    address_entry = ctk.CTkEntry(frame, placeholder_text="Enter Address", width=300, height=40)
    address_entry.pack(pady=8)
    contact_entry = ctk.CTkEntry(frame, placeholder_text="Enter Contact No. (India)", width=300, height=40)
    contact_entry.pack(pady=8)
    occupation = ctk.CTkComboBox(frame, values=["Electrician","Plumber","Mechanic","Developer","Tutor"], width=300, height=40)
    occupation.set("None Selected")
    occupation.pack(pady=8)
    avatar_path = [DEFAULT_AVATAR]
    def select_image():
        file_path = filedialog.askopenfilename(title="Select Avatar Image", filetypes=[("Image Files","*.png;*.jpg;*.jpeg;*.bmp")])
        if file_path:
            avatar_path[0] = file_path
            select_image_btn.configure(text="Image Selected!")
    select_image_btn = create_button(window, text="Select Avatar Image", command=select_image, width=350, height=45, corner_radius=20)
    select_image_btn.pack(pady=10)
    if edit_profile:
        name_entry.insert(0, edit_profile.get("name",""))
        name_entry.configure(state="disabled")
        age_entry.insert(0, edit_profile.get("age",""))
        address_entry.insert(0, edit_profile.get("address",""))
        contact_entry.insert(0, edit_profile.get("contact",""))
        occupation.set(edit_profile.get("occupation","None Selected"))
        avatar_path[0] = edit_profile.get("image", DEFAULT_AVATAR)
        select_image_btn.configure(text="Image Selected!")
    def save_p():
        nonlocal edit_profile
        name = name_entry.get().strip()
        age = age_entry.get().strip()
        addr = address_entry.get().strip()
        contact = contact_entry.get().strip()
        occ = occupation.get()
        if not (name and age and addr and contact):
            messagebox.showwarning("Error", "Please fill all fields!")
            return
        if not (contact.isdigit() and len(contact)==10 and contact[0] in "6789"):
            messagebox.showwarning("Error", "Please enter a valid 10-digit Indian contact number starting with 6-9.")
            return
        # prevent duplicate profiles with same contact (and prevent creating multiple profiles total)
        existing_same = next((p for p in profiles if p.get("contact")==contact and p is not edit_profile), None)
        if existing_same:
            messagebox.showwarning("Error", "A profile with this contact number already exists!")
            return
        if edit_profile:
            edit_profile["age"] = age
            edit_profile["address"] = addr
            edit_profile["contact"] = contact
            edit_profile["occupation"] = occ
            edit_profile["image"] = avatar_path[0]
            edit_profile.setdefault("achievements", [])
            edit_profile.setdefault("equipped_achievement", None)
        else:
            if find_profile_by_name(name):
                messagebox.showwarning("Error", "Profile with this name already exists!")
                return
            new_profile = {"name": name, "age": age, "address": addr, "contact": contact, "occupation": occ, "image": avatar_path[0], "rating_sum":0.0, "num_votes":0, "saved":False, "favorite":False, "hire_count":0, "achievements":[], "equipped_achievement": None}
            profiles.append(new_profile)
            edit_profile = new_profile
        save_profiles(profiles)
        current_profile_name = edit_profile.get("name")
        main_page()
    btn_text = "₹ 300" if edit_profile is None else "Save Profile"
    create_button(window, text=btn_text, command=save_p, width=350, height=55, corner_radius=20).pack(pady=10)
    if edit_profile:
        def delete_profile():
            if messagebox.askyesno("Confirm", "Are you sure you want to delete this profile?"):
                profiles.remove(edit_profile)
                save_profiles(profiles)
                main_page()
        create_button(window, text="Delete Profile", command=delete_profile, width=350, height=45, corner_radius=20).pack(pady=5)
    create_button(window, text="Back", command=main_page, width=350, height=55, corner_radius=20).pack()

def view_profiles_page(saved_only=False):
    for w in window.winfo_children():
        w.destroy()
    ctk.CTkLabel(window, text="Available Profiles", font=("Arial", 26, "bold")).pack(pady=(10,5))
    category_frame = ctk.CTkFrame(window, fg_color="#1a1a1a", corner_radius=20)
    category_frame.pack(pady=10, padx=20, fill="x")
    categories = ["All","Electrician","Plumber","Mechanic","Developer","Tutor"]
    selected_category = ctk.StringVar(value="All")
    def select_category(cat):
        selected_category.set(cat)
        update_profiles()
    for cat in categories:
        btn = create_button(category_frame, text=cat, width=120, height=40, command=lambda c=cat: select_category(c))
        btn.pack(side="left", padx=10, pady=10)
    search_frame = ctk.CTkFrame(window, fg_color="#1a1a1a", corner_radius=20)
    search_frame.pack(pady=5, padx=20, fill="x")
    search_var = ctk.StringVar()
    search_entry = ctk.CTkEntry(search_frame, textvariable=search_var, placeholder_text="Search by Name...", width=400)
    search_entry.pack(side="left", padx=10, pady=10, fill="x", expand=True)
    scroll_frame = ctk.CTkScrollableFrame(window, width=860, height=420, fg_color="#1c1c1c")
    scroll_frame.pack(pady=5)
    def create_profile_card(parent, profile):
        frame = ctk.CTkFrame(parent, fg_color="#222222", corner_radius=20)
        frame.pack(pady=10, padx=20, fill="x")
        try:
            pil_img = Image.open(profile.get("image", DEFAULT_AVATAR))
            circ = circle_mask_with_border(pil_img, (60,60), border=4, online=profile.get("online", False))
            img = ctk.CTkImage(circ, size=(60,60))
        except Exception:
            pil_img = Image.open(DEFAULT_AVATAR)
            circ = circle_mask_with_border(pil_img, (60,60), border=4, online=profile.get("online", False))
            img = ctk.CTkImage(circ, size=(60,60))
        ctk.CTkLabel(frame, image=img, text="").pack(side="left", padx=10, pady=5)
        display_name = f"[{profile.get('equipped_achievement')}] {profile.get('name','Unnamed')}" if profile.get('equipped_achievement') else profile.get('name','Unnamed')
        ctk.CTkLabel(frame, text=display_name, font=("Arial", 18, "bold")).pack(side="left", padx=10)
        if profile.get('favorite'):
            ctk.CTkLabel(frame, text="❤️", font=("Arial", 18)).pack(side="left", padx=5)
        ctk.CTkLabel(frame, text=f"({profile.get('occupation','')})", font=("Arial", 14, "italic"), text_color="#AAAAAA").pack(side="left")
        def open_three_dots_menu():
            menu = ctk.CTkToplevel(frame)
            menu.geometry("200x240+100+120")
            menu.title("Options")
            menu.grab_set()
            def close_menu():
                menu.grab_release()
                menu.destroy()
            def toggle_save():
                profile["saved"] = not profile.get("saved", False)
                save_profiles(profiles)
                close_menu()
                update_profiles()
            def toggle_fav():
                profile["favorite"] = not profile.get("favorite", False)
                save_profiles(profiles)
                close_menu()
                update_profiles()
            create_button(menu, text="Edit Profile", command=lambda: (menu.destroy(), create_profile(edit_profile=profile)), width=170, height=40, corner_radius=15).pack(pady=6)
            save_text = "Unsave" if profile.get("saved") else "Save"
            create_button(menu, text=save_text, command=toggle_save, width=170, height=40, corner_radius=15).pack(pady=6)
            fav_text = "Unfavorite ❤️" if profile.get("favorite") else "Favorite 🤍"
            create_button(menu, text=fav_text, command=toggle_fav, width=170, height=40, corner_radius=15).pack(pady=6)
        three_dots_btn = create_button(frame, text="⋮", width=44, height=44, command=open_three_dots_menu, corner_radius=20)
        three_dots_btn.pack(side="right", padx=10)
        create_button(frame, text="View Profile", command=lambda p=profile: open_profile(p), width=140, height=42, corner_radius=15).pack(side="right", padx=10)
    def update_profiles(*args):
        search_text = search_var.get().lower()
        cat = selected_category.get()
        for child in scroll_frame.winfo_children():
            child.destroy()
        for profile in profiles:
            if saved_only and not profile.get("saved", False): continue
            if cat != "All" and profile.get("occupation") != cat: continue
            if search_text and search_text not in profile.get("name","").lower(): continue
            create_profile_card(scroll_frame, profile)
    search_var.trace("w", update_profiles)
    update_profiles()
    create_button(window, text="← Back", command=main_page, width=100, height=40, corner_radius=20).place(relx=0.85, rely=0.9)





def open_profile(profile):
    global current_profile_name
    current_profile_name = profile.get("name")
    reply_target = {"path": None}


    def render_normal_view():
        for w in window.winfo_children():
            w.destroy()
        frame = ctk.CTkFrame(window, fg_color="#1a1a1a", corner_radius=20)
        frame.pack(padx=20, pady=20, fill="both", expand=True)

        # Avatar & Name
        try:
            pil_img = Image.open(profile.get("image", DEFAULT_AVATAR))
            circ = circle_mask_with_border(pil_img, (120,120), border=6, online=profile.get("online", False))
            img = ctk.CTkImage(circ, size=(120,120))
        except Exception:
            pil_img = Image.open(DEFAULT_AVATAR)
            circ = circle_mask_with_border(pil_img, (120,120), border=6, online=profile.get("online", False))
            img = ctk.CTkImage(circ, size=(120,120))
        ctk.CTkLabel(frame, image=img, text="").pack(pady=10)

        equipped = profile.get("equipped_achievement")
        name_text = f"Name: {profile.get('name','')}" + (f" ({equipped})" if equipped else "")
        ctk.CTkLabel(frame, text=name_text, font=("Arial", 20, "bold")).pack(pady=5)
        ctk.CTkLabel(frame, text=f"Age: {profile.get('age','')}", font=("Arial", 16)).pack(pady=2)
        ctk.CTkLabel(frame, text=f"Address: {profile.get('address','')}", font=("Arial", 16)).pack(pady=2)
        ctk.CTkLabel(frame, text=f"Occupation: {profile.get('occupation','')}", font=("Arial", 16)).pack(pady=2)

        # Rating
        def get_average_rating():
            if profile.get("num_votes",0) == 0:
                return 0
            return profile.get("rating_sum",0) / profile.get("num_votes",1)
        average = get_average_rating()
        rating_label = ctk.CTkLabel(frame, text=f"Rating: {(average/5)*100:.1f}%", font=("Arial", 16))
        rating_label.pack(pady=5)

        if profile.get("num_votes", 0) == 0:
            stars_frame = ctk.CTkFrame(frame, fg_color="transparent")
            stars_frame.pack(pady=5)
            star_buttons = []
            selected_rating = [0]
            def update_stars_display(selected=0):
                for idx, btn in enumerate(star_buttons, start=1):
                    if idx <= selected:
                        btn.configure(text="★", text_color="yellow")
                    else:
                        btn.configure(text="☆", text_color="white")
            def select_rating(value):
                selected_rating[0] = value
                update_stars_display(value)
            def submit_rating():
                if selected_rating[0] <= 0:
                    messagebox.showwarning("Error", "Please select a star rating first.", parent=window)
                    return
                profile["rating_sum"] = profile.get("rating_sum", 0) + selected_rating[0]
                profile["num_votes"] = profile.get("num_votes", 0) + 1
                save_profiles(profiles)
                avg = profile["rating_sum"] / profile["num_votes"]
                rating_label.configure(text=f"Rating: {(avg/5)*100:.1f}%")
                stars_frame.destroy()
                submit_btn.destroy()
                messagebox.showinfo("Thank you!", "Your rating has been submitted.", parent=window)
            for i in range(1, 5+1):
                b = create_button(stars_frame, text="☆", width=40, height=40, command=lambda v=i: select_rating(v))
                b.pack(side="left", padx=2)
                star_buttons.append(b)
            update_stars_display(int(round(average)))
            submit_btn = create_button(frame, text="Submit Rating", width=180, height=36, corner_radius=12, command=submit_rating)
            submit_btn.pack(pady=4)

        # Hire count
        create_button(frame, text=f"Hire Count: {profile.get('hire_count',0)}", width=180, height=36, corner_radius=12).pack(pady=6)

        # Hire options
        def hire_options_popup():
            opt = ctk.CTkToplevel(window)
            opt.title("Hire Options")
            opt.geometry("320x180+420+220")
            opt.grab_set()
            create_button(opt, text="Message", width=200, height=45, command=lambda: (opt.destroy(), open_chat_box(profile.get("name"), chat_id=profile.get("name")))).pack(pady=8)
            create_button(opt, text="Contact", width=200, height=45, command=lambda: messagebox.showinfo("Contact Info", f"Name: {profile.get('name')}\nContact: {profile.get('contact')}")).pack(pady=8)
            create_button(opt, text="Close", width=200, height=45, command=opt.destroy).pack(pady=8)

        create_button(frame, text="Hire", command=hire_options_popup, width=200, height=50, corner_radius=20).pack(pady=10)

        create_button(window, text="← Back", command=lambda: view_profiles_page(), width=100, height=40, corner_radius=20).place(relx=0.85, rely=0.9)

        # Comments button
        create_button(frame, text="Comments", width=200, height=40, corner_radius=15, command=render_comments_view).pack(pady=8)

    

    def render_comments_view():
        for w in window.winfo_children():
            w.destroy()
        frame = ctk.CTkFrame(window, fg_color="#1a1a1a", corner_radius=20)
        frame.pack(padx=20, pady=20, fill="both", expand=True)

        # Avatar & Name
        try:
            pil_img = Image.open(profile.get("image", DEFAULT_AVATAR))
            circ = circle_mask_with_border(pil_img, (120,120), border=6, online=profile.get("online", False))
            img = ctk.CTkImage(circ, size=(120,120))
        except Exception:
            pil_img = Image.open(DEFAULT_AVATAR)
            circ = circle_mask_with_border(pil_img, (120,120), border=6, online=profile.get("online", False))
            img = ctk.CTkImage(circ, size=(120,120))
        ctk.CTkLabel(frame, image=img, text="").pack(pady=10)
        ctk.CTkLabel(frame, text=profile.get("name",""), font=("Arial", 20, "bold")).pack(pady=5)

        profile.setdefault("comments", [])
        save_profiles(profiles)

        scroll = ctk.CTkScrollableFrame(frame, width=500, height=350)
        scroll.pack(pady=5)

        # reply_target is defined in outer scope (open_profile) so it persists across renders
        # functions to manipulate comments
        def toggle_like_at_path(path):
            user = str(current_profile_name or "Anon").strip().lower()
            # locate comment by path
            target = profile['comments']
            for idx in path[:-1]:
                target = target[idx].setdefault('replies', [])
            comment = target[path[-1]]
            likes = comment.setdefault('likes', [])
            # normalize existing likes to lower-case
            likes = [str(u).strip().lower() for u in likes]
            if user in likes:
                likes = [u for u in likes if u != user]
            else:
                likes.append(user)
            comment['likes'] = likes
            save_profiles(profiles)
            render_comments_view()

        def add_comment_at_path(path, user, text, image_path):
            new_comment = {
        "image": image_path, "user": user, "text": text, "likes": [], "replies": []}
            if not path:
                profile["comments"].append(new_comment)
            else:
                target = profile["comments"]
                for idx in path[:-1]:
                    target = target[idx].setdefault("replies", [])
                parent = target[path[-1]]
                parent.setdefault("replies", []).append(new_comment)
            save_profiles(profiles)
            render_comments_view()

        # Render comments recursively

        def delete_comment(path):
            # Navigate to parent list
            if not path:
                return
            parent_list = profile["comments"]
            for idx in path[:-1]:
                parent_list = parent_list[idx]["replies"]
            parent_list.pop(path[-1])
            save_profiles(profiles)
            render_comments_view()

        def render_comment_list(comments, container, depth=0, path_prefix=[]):
            for i, c in enumerate(comments):
                frm = ctk.CTkFrame(container, fg_color="#222", corner_radius=8)
                frm.pack(fill="x", pady=4, padx=(20*depth,4))

                ctk.CTkLabel(frm, text=f"{c.get('user','Anon')}: ", font=("Arial", 13, "bold")).pack(anchor="w", padx=4, pady=2)
                ctk.CTkLabel(frm, text=c.get("text",""), font=("Arial", 13), wraplength=460, justify="left").pack(anchor="w", padx=4, pady=2)
                if c.get("image"):
                    try:
                        im = Image.open(c["image"])
                        im.thumbnail((150,150))
                        tkimg = ctk.CTkImage(im, size=(im.width, im.height))
                        lbl_img = ctk.CTkLabel(frm, image=tkimg, text="")
                        lbl_img.image = tkimg

                        # On click, open full-size image preview
                        def open_full_image(path=c["image"]):
                            try:
                                img_full = Image.open(path)
                                screen_w = window.winfo_screenwidth()
                                screen_h = window.winfo_screenheight()
                                max_w, max_h = screen_w - 100, screen_h - 100
                                img_full.thumbnail((max_w, max_h))
                                img_full_tk = ctk.CTkImage(img_full, size=(img_full.width, img_full.height))

                                # Close all other Toplevels so only preview is open
                                for wdg in window.winfo_children():
                                    if isinstance(wdg, ctk.CTkToplevel):
                                        try:
                                            wdg.destroy()
                                        except:
                                            pass

                                top = ctk.CTkToplevel(window)
                                top.title("Image Preview")
                                top.attributes("-topmost", True)
                                top.geometry(f"{img_full.width+40}x{img_full.height+80}+50+50")

                                lbl_full = ctk.CTkLabel(top, image=img_full_tk, text="")
                                lbl_full.image = img_full_tk
                                lbl_full.pack(padx=10, pady=10)

                                def back_to_comments():
                                    top.destroy()
                                    render_comments_view()  # reopen comments view

                                back_btn = ctk.CTkButton(
                                    top,
                                    text="← Back",
                                    width=80,
                                    height=36,
                                    fg_color="white",
                                    text_color="black",
                                    command=back_to_comments
                                )
                                back_btn.place(relx=0.95, rely=0.95, anchor="se")

                            except Exception as e:
                                messagebox.showerror("Error", f"Could not open image: {e}")

                                messagebox.showerror("Error", f"Could not open image: {e}")

                        lbl_img.bind("<Button-1>", lambda e: open_full_image())
                        lbl_img.pack(anchor="w", padx=4, pady=(0,4))
                    except Exception as e:
                        ctk.CTkLabel(frm, text=f"[Image not found: {os.path.basename(c['image'])}]", font=("Arial", 11), text_color="red").pack(anchor="w", padx=4, pady=(0,4))

                if c.get("likes"):
                    ctk.CTkLabel(frm, text=f"👍 {len(c.get('likes', []))}", font=("Arial", 12)).pack(anchor="w", padx=8, pady=(0,4))

                # right-click menu
                def on_right_click(event, path=path_prefix+[i], comment=c):
                    user = str(current_profile_name or "Anon").strip().lower()
                    likes = [str(u).strip().lower() for u in comment.get("likes", [])]
                    menu = tk.Menu(window, tearoff=0, font=("Arial", 14))
                    if user in likes:
                        menu.add_command(label="👎 Unlike", command=lambda: toggle_like_at_path(path))
                    else:
                        menu.add_command(label="👍 Like", command=lambda: toggle_like_at_path(path))
                    menu.add_command(label="↩ Reply", command=lambda: (reply_target.update({"path": path}), render_comments_view()))
                    if user == str(comment.get("user", "")).strip().lower():
                        menu.add_command(label="🗑 Delete", command=lambda: delete_comment(path))
                    try:
                        menu.tk_popup(event.x_root, event.y_root)
                    finally:
                        menu.grab_release()

                frm.bind("<Button-3>", on_right_click)
                for child in frm.winfo_children():
                    child.bind("<Button-3>", on_right_click)

                # render replies recursively
                render_comment_list(c.get("replies", []), container, depth+1, path_prefix+[i])

        render_comment_list(profile["comments"], scroll)

        # Reply mode bar
        if reply_target.get("path"):
            # fetch target comment
            target = profile["comments"]
            for idx in reply_target["path"]:
                target = target[idx]
            target_comment = target
            reply_text_preview = (target_comment.get("text","")[:60] + "...") if len(target_comment.get("text",""))>60 else target_comment.get("text","")
            reply_bar = ctk.CTkFrame(frame, fg_color="#333", corner_radius=8)
            reply_bar.pack(fill="x", padx=10, pady=(5,0))
            ctk.CTkLabel(reply_bar, text=f"Replying to: \"{reply_text_preview}\"", font=("Arial", 12, "italic")).pack(side="left", padx=8)
            create_button(reply_bar, text="❌", width=40, height=25, command=lambda: (reply_target.update({"path": None}), render_comments_view())).pack(side="right", padx=5)

        # Comment input bar
        comment_bar = ctk.CTkFrame(frame, fg_color="transparent")
        comment_bar.pack(fill="x", pady=8, padx=10)
        entry = ctk.CTkEntry(comment_bar, placeholder_text="Write a comment...")

        # Photo attachment preview frame
        preview_frame = ctk.CTkFrame(comment_bar, fg_color="transparent")
        preview_frame.pack(side="left", padx=(0,5))
        attached_image = {"path": None}

        def clear_preview():
            attached_image["path"] = None
            for w in preview_frame.winfo_children():
                w.destroy()

        def pick_image():
            file_path = filedialog.askopenfilename(title="Select Image", filetypes=[("Image Files","*.png;*.jpg;*.jpeg;*.gif")])
            if not file_path:
                return
            attached_image["path"] = file_path
            for w in preview_frame.winfo_children():
                w.destroy()
            try:
                im = Image.open(file_path)
                im.thumbnail((80,80))
                tkimg = ctk.CTkImage(im, size=(im.width, im.height))
                lbl = ctk.CTkLabel(preview_frame, image=tkimg, text="")
                lbl.image = tkimg
                lbl.pack(side="left")
                create_button(preview_frame, text="✖", width=30, height=30, command=clear_preview).pack(side="left", padx=(4,0))
            except Exception:
                ctk.CTkLabel(preview_frame, text=os.path.basename(file_path)).pack(side="left")

        # Photo button
        create_button(comment_bar, text="🖼", width=40, height=30, command=pick_image).pack(side="left", padx=(4,4))
        entry.pack(side="left", fill="x", expand=True, padx=(0,5))

        def on_add_click():
            text = entry.get().strip()
            image_path = attached_image.get('path')
            if not text and not image_path:
                return
            user = str(current_profile_name or "Anon").strip()
            entry.delete(0, "end")
            path = reply_target.get("path")
            add_comment_at_path(path, user, text, image_path)
            reply_target.update({"path": None})

        create_button(comment_bar, text="Add", width=60, height=30, command=on_add_click).pack(side="left", padx=(0,5))
        create_button(comment_bar, text="❌", width=40, height=30, command=render_normal_view).pack(side="left")

    render_normal_view()

def leaderboard_page(timeframe):
    for w in window.winfo_children():
        w.destroy()
    ctk.CTkLabel(window, text="Leaderboard", font=("Arial", 26, "bold")).pack(pady=10)
    tab_frame = ctk.CTkFrame(window, fg_color="#1a1a1a", corner_radius=20)
    tab_frame.pack(pady=10, padx=20, fill="x")
    def update_tab(selected):
        leaderboard_page(selected)
    week_btn = create_button(tab_frame, text="Top 10 Week", width=150, height=40, corner_radius=20, command=lambda: update_tab("week"))
    week_btn.pack(side="left", padx=10)
    month_btn = create_button(tab_frame, text="Top 10 Month", width=150, height=40, corner_radius=20, command=lambda: update_tab("month"))
    month_btn.pack(side="left", padx=10)
    all_btn = create_button(tab_frame, text="Top 10 All Time", width=150, height=40, corner_radius=20, command=lambda: update_tab("all"))
    all_btn.pack(side="left", padx=10)

    # New formula: both hire count and rating as percentages, averaged
    highest_hire = max((p.get("hire_count", 0) for p in profiles), default=1)
    def get_score(profile):
        rating_percentage = (profile.get("rating_sum", 0) / max(profile.get("num_votes", 1), 1)) * 0.1  # stars to %
        hire_percentage = (profile.get("hire_count", 0) / highest_hire) * 100 if highest_hire > 0 else 0
        return (rating_percentage + hire_percentage) / 2

    sorted_profiles = sorted(profiles, key=get_score, reverse=True)[:10]
    scroll_frame = ctk.CTkScrollableFrame(window, width=880, height=420, fg_color="#1c1c1c")
    scroll_frame.pack(pady=10)
    colors = ["#FFD700", "#C0C0C0", "#8B4513"]
    for i, p in enumerate(sorted_profiles, 1):
        bg_color = "#222222"
        if i <= 3:
            bg_color = colors[i-1]
        frame = ctk.CTkFrame(scroll_frame, fg_color=bg_color, corner_radius=20)
        frame.pack(pady=10, padx=20, fill="x")
        try:
            pil_img = Image.open(p.get("image", DEFAULT_AVATAR))
            circ = circle_mask_with_border(pil_img, (60,60), border=4, online=p.get("online", False))
            img = ctk.CTkImage(circ, size=(60,60))
        except Exception:
            pil_img = Image.open(DEFAULT_AVATAR)
            circ = circle_mask_with_border(pil_img, (60,60), border=4, online=p.get("online", False))
            img = ctk.CTkImage(circ, size=(60,60))
        ctk.CTkLabel(frame, text=f"#{i}", font=("Arial", 20, "bold"), width=30).pack(side="left", padx=5)
        ctk.CTkLabel(frame, image=img, text="").pack(side="left", padx=10, pady=5)
        ctk.CTkLabel(frame, text=p.get("name","Unnamed"), font=("Arial", 18, "bold"), anchor="w").pack(side="left", padx=10)
        score_val = get_score(p)
        ctk.CTkLabel(frame, text=f"Score: {score_val:.2f}%", font=("Arial", 16)).pack(side="right", padx=20)
        create_button(frame, text="View Profile", command=lambda prof=p: open_profile(prof), width=150, height=40, corner_radius=15).pack(side="right", padx=10)
    create_button(window, text="← Back", command=main_page, width=100, height=40, corner_radius=20).place(relx=0.85, rely=0.9)


def open_achievements_page(profile_name):
    prof = find_profile_by_name(profile_name)
    if not prof:
        messagebox.showwarning("Error", "Profile not found!")
        return

    # 🔥 Ensure achievements are awarded before showing
    all_profiles = load_profiles()
    p = next((x for x in all_profiles if x.get("name") == prof.get("name")), None)
    if p:
        check_award_achievements(p, all_profiles)
        prof = p  # update reference

    win = ctk.CTkToplevel(window)
    win.title(f"Achievements — {profile_name}")
    win.geometry("500x600+400+120")
    win.grab_set()

    ctk.CTkLabel(win, text="Achievements", font=("Arial", 22, "bold")).pack(pady=10)

    scroll = ctk.CTkScrollableFrame(win, width=460, height=480)
    scroll.pack(padx=10, pady=10)

    equipped = prof.get("equipped_achievement")

    ach_list = prof.get("achievements", [])
    if not ach_list:
        ctk.CTkLabel(scroll, text="No achievements unlocked yet.", font=("Arial", 16, "italic"), text_color="#888").pack(pady=20)
        ctk.CTkLabel(scroll, text="HINT: Increase your Hire Count to unlock achievements!", font=("Arial", 14), text_color="#aaa").pack(pady=10)
    else:
        for ach in ach_list:
            frame = ctk.CTkFrame(scroll, fg_color="#222", corner_radius=10)
            frame.pack(fill="x", padx=6, pady=6)

            ctk.CTkLabel(frame, text=ach, font=("Arial", 16, "bold")).pack(side="left", padx=10, pady=10)

            if ach == equipped:
                def unequip(a=ach):
                    all_profiles = load_profiles()
                    p = next((x for x in all_profiles if x.get("name") == prof.get("name")), None)
                    if p:
                        p["equipped_achievement"] = None
                        save_profiles(all_profiles)
                    try:
                        show_equipment_popup(f"Unequipped {a}", success=False)
                    except Exception:
                        pass
                    win.destroy()
                    open_achievements_page(profile_name)
                create_button(frame, text="Unequip", width=100, height=34, command=unequip).pack(side="right", padx=10)
            else:
                def equip(a=ach):
                    all_profiles = load_profiles()
                    p = next((x for x in all_profiles if x.get("name") == prof.get("name")), None)
                    if p:
                        p["equipped_achievement"] = a
                        save_profiles(all_profiles)
                    try:
                        show_equipment_popup(f"Equipped: {a}")
                    except Exception:
                        pass
                    win.destroy()
                    open_achievements_page(profile_name)
                create_button(frame, text="Equip", width=100, height=34, command=equip).pack(side="right", padx=10)

    create_button(win, text="Close", width=120, height=40, command=win.destroy).pack(pady=12)
def equip_achievement(profile, ach_name):
    profile["equipped_achievement"] = ach_name
    save_profiles(profiles)
    messagebox.showinfo("Equipped", f"{ach_name} equipped for {profile.get('name')}")


def unequip_achievement(profile, ach_name):
    profile["equipped_achievement"] = None
    save_profiles(profiles)
    messagebox.showinfo("Unequipped", f"{ach_name} unequipped for {profile.get('name')}")




# --- Injected App Initialization Block ---
try:
    ctk.set_appearance_mode("dark")
except Exception:
    pass

try:
    window = ctk.CTk()
    window.title("Smart Hire")
    window.geometry("980x720")
except Exception:
    try:
        window = tk.Tk()
        window.title("Smart Hire")
    except Exception:
        window = None

# Ensure a default avatar image exists
try:
    DEFAULT_AVATAR = "default_avatar.png"
    if not os.path.exists(DEFAULT_AVATAR):
        from PIL import Image as _Image
        img = _Image.new("RGBA", (120,120), (200,200,200,255))
        img.save(DEFAULT_AVATAR)
except Exception:
    DEFAULT_AVATAR = ""

# Load persisted profiles and initialize state if available
try:
    profiles = load_profiles()
except Exception:
    profiles = []

try:
    current_profile_name = None
except Exception:
    current_profile_name = None

# Ensure notification variable exists
try:
    notification_red_dot = None
except Exception:
    notification_red_dot = None

# Provide a safe emergency handler (will be used by the Emergency Request button)


def open_emergency_request():
    # --- Emergency Request Form (with labels + robust placeholders) ---
    form = ctk.CTkToplevel(window)
    form.title("Emergency Request")
    form.geometry("560x690+480+120")
    form.grab_set()

    ctk.CTkLabel(form, text="🚨 Emergency Request Form", font=("Arial", 20, "bold")).pack(pady=(14, 10))

    # Vars
    name_var = tk.StringVar()
    contact_var = tk.StringVar()
    addr_var = tk.StringVar()
    title_var = tk.StringVar()
    occ_var = tk.StringVar(value="Select Person Required")

    # Helper to create a stacked label + entry with manual placeholder that works in any CTk version
    def labeled_entry(parent, label, var, ph_text, width=420):
        ctk.CTkLabel(parent, text=label, font=("Arial", 13, "bold")).pack(anchor="w", padx=12, pady=(8, 2))
        entry = ctk.CTkEntry(parent, textvariable=var, width=width, height=40)
        entry.pack(padx=12, pady=(0, 2))

        ph_color = "#9aa0a6"
        normal_color = None  # theme default

        def set_ph():
            try:
                entry.delete(0, "end")
                entry.insert(0, ph_text)
                entry.configure(text_color=ph_color)
            except Exception:
                pass

        def on_focus_in(_e):
            try:
                if entry.get() == ph_text:
                    entry.delete(0, "end")
                    entry.configure(text_color=normal_color)
            except Exception:
                pass

        def on_focus_out(_e):
            try:
                if not entry.get().strip():
                    set_ph()
            except Exception:
                pass

        set_ph()
        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)
        return entry, ph_text

    # Name
    _, PH_NAME = labeled_entry(form, "Your Name", name_var, "Your Name")

    # Contact
    _, PH_CONTACT = labeled_entry(form, "Your Contact No.", contact_var, "10-digit mobile number (starts with 6-9)")

    # Address
    _, PH_ADDR = labeled_entry(form, "Your Address", addr_var, "House/Street, City, PIN")

    # Person Required (no 'Myself')
    ctk.CTkLabel(form, text="Person Required", font=("Arial", 13, "bold")).pack(anchor="w", padx=12, pady=(8, 2))
    occ_combo = ctk.CTkComboBox(
        form,
        values=["Electrician","Plumber","Mechanic","Developer","Tutor"],
        variable=occ_var,
        width=420
    )
    occ_combo.pack(padx=12, pady=(0, 2))
    occ_combo.set("Select Person Required")

    # Title
    _, PH_TITLE = labeled_entry(form, "Title", title_var, "Short title e.g., 'Power outage at home'")

    # Description
    ctk.CTkLabel(form, text="Describe your emergency", font=("Arial", 13, "bold")).pack(anchor="w", padx=12, pady=(8, 2))
    desc_text = ctk.CTkTextbox(form, width=500, height=140)
    desc_text.pack(padx=12, pady=(0, 2))

    _PH_DESC = "Describe your emergency in detail..."
    ph_desc_color = "#9aa0a6"
    def set_desc_ph():
        try:
            desc_text.configure(state="normal")
            desc_text.delete("1.0", "end")
            desc_text.insert("1.0", _PH_DESC)
            desc_text.configure(text_color=ph_desc_color)
        except Exception:
            pass
    def clear_desc_ph(_e=None):
        try:
            if desc_text.get("1.0", "end-1c") == _PH_DESC:
                desc_text.delete("1.0", "end")
                desc_text.configure(text_color=None)
        except Exception:
            pass
    def restore_desc_ph(_e=None):
        try:
            if not desc_text.get("1.0", "end-1c").strip():
                set_desc_ph()
        except Exception:
            pass
    set_desc_ph()
    desc_text.bind("<FocusIn>", clear_desc_ph)
    desc_text.bind("<FocusOut>", restore_desc_ph)

    # Live character count
    char_var = tk.StringVar(value="Characters: 0")
    ctk.CTkLabel(form, textvariable=char_var, font=("Arial", 11), text_color="#9aa0a6").pack(anchor="w", padx=12, pady=(2, 8))
    def _upd_chars(_e=None):
        txt = desc_text.get("1.0", "end-1c")
        char_var.set(f"Characters: {0 if txt == _PH_DESC else len(txt)}")
    desc_text.bind("<KeyRelease>", _upd_chars)

    # Buttons
    btn_frame = ctk.CTkFrame(form, fg_color="transparent")
    btn_frame.pack(pady=14)

    def send_request():
        name = name_var.get().strip()
        contact = contact_var.get().strip()
        addr = addr_var.get().strip()
        occ = occ_var.get().strip()
        title = title_var.get().strip()
        description = desc_text.get("1.0", "end-1c").strip()

        # Treat placeholders as empty
        if name == PH_NAME: name = ""
        if contact == PH_CONTACT: contact = ""
        if addr == PH_ADDR: addr = ""
        if title == PH_TITLE: title = ""
        if description == _PH_DESC: description = ""

        # Validate
        if not name or not contact or not addr or not title or not description:
            messagebox.showwarning("Error", "Please fill all fields.", parent=form)
            return
        if occ == "Select Person Required":
            messagebox.showwarning("Error", "Please choose the person required.", parent=form)
            return
        # 10-digit mobile starting with 6-9
        if not (contact.isdigit() and len(contact) == 10 and contact[0] in "6789"):
            messagebox.showwarning("Error", "Enter a valid 10-digit contact number starting with 6–9.", parent=form)
            return

        reqs = load_requests()
        reqs.append({
            "from_username": name,
            "contact": contact,
            "address": addr,
            "occupation": occ,
            "title": title,
            "description": description,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "pending"
        })
        save_requests(reqs)
        update_notification_dot()
        form.destroy()
        messagebox.showinfo("Sent", "Emergency request sent!", parent=window)

    ctk.CTkButton(btn_frame, text="Send", width=160, command=send_request).pack(side="left", padx=10)
    ctk.CTkButton(btn_frame, text="Cancel", width=160, command=form.destroy).pack(side="left", padx=10)
# --- End injected block ---






def accept_request(req):
        reqs = load_requests()
        updated = False
        for r in reqs:
            if ('title' not in r) and r.get('to')==req.get('to') and r.get('from_username')==req.get('from_username') and r.get('time')==req.get('time'):
                r['status'] = 'accepted'
                r['accepted_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                updated = True
                break
        if updated:
            save_requests(reqs)
            update_notification_dot()
            try:
                all_profiles = load_profiles()
                prof = next((p for p in all_profiles if p.get("name","").lower() == req.get("to","").lower()), None)
                if prof is not None:
                    prof["hire_count"] = prof.get("hire_count", 0) + 1
                    check_award_achievements(prof, all_profiles)
                    save_profiles(all_profiles)
            except Exception as e:
                print("accept_request achievement error:", e)
            try:
                refresh_list()
            except Exception:
                pass
            try:
                show_accept_popup(req)
            except Exception:
                pass

def show_equipment_popup(text, success=True):
    popup = ctk.CTkToplevel(window)
    popup.overrideredirect(True)
    popup.attributes("-topmost", True)
    popup.configure(fg_color="#111111")
    w, h = 420, 80
    screen_w, screen_h = popup.winfo_screenwidth(), popup.winfo_screenheight()
    x, y = (screen_w - w) // 2, int(screen_h * 0.25)
    popup.geometry(f"{w}x{h}+{x}+{y}")

    emoji = "🏆" if success else "❌"
    msg = f"{emoji} {text}"

    label = ctk.CTkLabel(popup, text=msg,
                         font=("Arial Black", 18, "bold"),
                         text_color="white")
    label.pack(expand=True)

    def fade_out(alpha=0.95):
        if not popup.winfo_exists():
            return
        alpha -= 0.05
        if alpha > 0:
            popup.attributes("-alpha", alpha)
            popup.after(50, lambda: fade_out(alpha))
        else:
            if popup.winfo_exists():
                popup.destroy()
    popup.after(1800, fade_out)

# Start the app
main_page()
window.mainloop()
