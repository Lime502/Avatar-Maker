import os
import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser
import customtkinter as ctk
from PIL import Image
import requests
from io import BytesIO

INNER_OUTLINE_BLACK = "Black"
INNER_OUTLINE_SHADED = "Shaded"

def process_avatar(skin_image, use_outer_outline=True, inner_outline_mode=INNER_OUTLINE_BLACK, outline_color=(0, 0, 0)):
    try:
        skin = skin_image.convert("RGBA")
        canvas = Image.new("RGBA", (38, 38), (0, 0, 0, 0))
        parts_grid = [[0 for _ in range(38)] for _ in range(38)]
        color_grid = [[(0,0,0,0) for _ in range(38)] for _ in range(38)]
        render_outline_color = (outline_color[0], outline_color[1], outline_color[2], 255)

        def get_texel(x, y):
            if 0 <= x < skin.width and 0 <= y < skin.height:
                return skin.getpixel((x, y))
            return (0, 0, 0, 0)

        def apply_shadow(color, factor):
            if color[3] == 0: return color
            return (int(color[0] * factor), int(color[1] * factor), int(color[2] * factor), color[3])

        def get_darker_color(color):
            return apply_shadow(color, 0.7)

        y_offset = 1 if use_outer_outline else 2

        for py in range(38):
            for px in range(38):
                x, y = px - 7, py - 5 - y_offset
                final_color, part_id = (0, 0, 0, 0), 0
                if 18 <= x < 27 and 17 <= y < 31:
                    part_id = 1
                    if x < 24:
                        c = get_texel((x - 18) // 2 + 52, (y - 17) // 2 + 52)
                        if c[3] < 25: c = get_texel((x - 18) // 2 + 36, (y - 17) // 2 + 52)
                        final_color = c
                    else:
                        c = get_texel((x - 24) + 56, (y - 17) // 2 + 52)
                        if c[3] < 25: c = get_texel((x - 24) + 40, (y - 17) // 2 + 52)
                        final_color = apply_shadow(c, 0.6)
                if (part_id == 0 or final_color[3] < 25) and (0 <= x < 24 and 0 <= y < 18):
                    h_c = (0,0,0,0)
                    if x < 16:
                        ty = y - (1 if y > 1 else 0) - (1 if y > 15 else 0)
                        h_c = get_texel(x // 2 + 40, ty // 2 + 8)
                    else:
                        ty = y - (1 if y > 0 else 0) - (1 if y > 15 else 0)
                        h_c = apply_shadow(get_texel((x - 16) + 48, ty // 2 + 8), 0.6)
                    if h_c[3] < 25:
                        if 1 <= x < 16 and 1 <= y < 17:
                            tx = x - 1 + (1 if (x-1) > 6 else 0)
                            h_c = get_texel(tx // 2 + 8, (y - 1) // 2 + 8)
                        elif 16 <= x < 24 and 1 <= y < 17:
                            h_c = apply_shadow(get_texel((x - 16) + 16, (y - 1) // 2 + 8), 0.6)
                    if h_c[3] >= 25: final_color, part_id = h_c, 2
                if (part_id == 0 or final_color[3] < 25) and (3 <= x < 18 and 17 <= y < 31):
                    tx, ty = x - 3, y - 17
                    if tx > 6: tx += 1
                    c = get_texel(tx // 2 + 20, ty // 2 + 36)
                    if c[3] < 25: c = get_texel(tx // 2 + 20, ty // 2 + 20)
                    if c[3] >= 25: final_color, part_id = c, 3
                if (part_id == 0 or final_color[3] < 25):
                    lx, ly = px - 4, py - 5 - y_offset
                    if 0 <= lx < 6 and 17 <= ly < 31:
                        c = get_texel(lx // 2 + 44, (ly - 17) // 2 + 36)
                        if c[3] < 25: c = get_texel(lx // 2 + 44, (ly - 17) // 2 + 20)
                        if c[3] >= 25: final_color, part_id = c, 4
                color_grid[py][px], parts_grid[py][px] = final_color, part_id

        for py in range(38):
            for px in range(38):
                curr_id = parts_grid[py][px]
                if curr_id == 0:
                    if use_outer_outline:
                        is_ext = False
                        for dy in [-1, 0, 1]:
                            for dx in [-1, 0, 1]:
                                if dy == 0 and dx == 0: continue
                                if 0 <= py+dy < 38 and 0 <= px+dx < 38:
                                    nb_id = parts_grid[py+dy][px+dx]
                                    if nb_id != 0:
                                        if abs(dx) + abs(dy) == 2:
                                            if dy == -1 and nb_id in [1, 3, 4]: is_ext = True
                                        else: is_ext = True
                                if is_ext: break
                            if is_ext: break
                        if is_ext: canvas.putpixel((px, py), render_outline_color)
                else:
                    is_inner = False
                    for dy in [-1, 0, 1]:
                        for dx in [-1, 0, 1]:
                            if dy == 0 and dx == 0: continue
                            if 0 <= py+dy < 38 and 0 <= px+dx < 38:
                                nb_id = parts_grid[py+dy][px+dx]
                                if nb_id != 0 and nb_id != curr_id:
                                    if curr_id == 2 and nb_id == 1:
                                        if abs(dx) + abs(dy) == 1: is_inner = True
                                    elif curr_id in [1, 4] and nb_id == 3: is_inner = True
                                    elif nb_id == 2 and curr_id != 2 and curr_id != 1: is_inner = True
                                    if is_inner: break
                        if is_inner: break
                    if is_inner:
                        if not use_outer_outline:
                            final_c = get_darker_color(color_grid[py][px])
                        else:
                            final_c = get_darker_color(color_grid[py][px]) if inner_outline_mode == INNER_OUTLINE_SHADED else render_outline_color
                        canvas.putpixel((px, py), final_c)
                    else:
                        c = color_grid[py][px]
                        if c[3] >= 25: canvas.putpixel((px, py), (c[0], c[1], c[2], 255))
        return canvas
    except Exception as e:
        messagebox.showerror("Error", f"Processing failed: {e}")
        return None

class AvatarApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Avatar Maker")
        self.geometry("820x550")
        self.resizable(False, False)
        ctk.set_appearance_mode("dark")
        self.current_skin_img, self.result_image = None, None
        self.outer_outline_var = tk.BooleanVar(value=True)
        self.inner_outline_mode_var = tk.StringVar(value=INNER_OUTLINE_BLACK)
        self.mirror_var = tk.BooleanVar(value=False)
        self.outline_color = (0, 0, 0)

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        self.label = ctk.CTkLabel(self, text="AVATAR GENERATOR", font=("Arial", 22, "bold"))
        self.label.grid(row=0, column=0, columnspan=2, pady=(15, 10))

        self.left_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.left_frame.grid(row=1, column=0, padx=(20, 10), pady=10, sticky="nsew")

        self.preview_frame = ctk.CTkFrame(self.left_frame, width=320, height=320)
        self.preview_frame.pack(pady=10)
        self.preview_frame.pack_propagate(False)
        self.preview_label = ctk.CTkLabel(self.preview_frame, text="No Image", font=("Arial", 14))
        self.preview_label.pack(expand=True, fill="both")

        self.btn_save = ctk.CTkButton(self.left_frame, text="Save Result", font=("Arial", 13, "bold"), command=self.save_avatar, state="disabled")
        self.btn_save.pack(pady=15, padx=20, fill="x")

        self.right_frame = ctk.CTkScrollableFrame(self, width=400)
        self.right_frame.grid(row=1, column=1, padx=(10, 20), pady=10, sticky="nsew")

        self.tab_view = ctk.CTkTabview(self.right_frame, height=160)
        self.tab_view.pack(pady=(0, 10), padx=5, fill="x")
        self.tab_view.add("File")
        self.tab_view.add("Nickname")
        ctk.CTkButton(self.tab_view.tab("File"), text="Select Skin File", command=self.select_skin).pack(pady=20)
        self.nick_entry = ctk.CTkEntry(self.tab_view.tab("Nickname"), placeholder_text="Enter Nickname")
        self.nick_entry.pack(pady=10, padx=20, fill="x")
        ctk.CTkButton(self.tab_view.tab("Nickname"), text="Load by Nick", command=self.load_by_nick).pack(pady=5)

        self.settings_frame = ctk.CTkFrame(self.right_frame)
        self.settings_frame.pack(pady=10, padx=5, fill="x")
        
        ctk.CTkCheckBox(self.settings_frame, text="Enable Outer Outline", variable=self.outer_outline_var, command=self.update_outline_settings).pack(pady=(10, 5), anchor="w", padx=15)
        self.btn_color = ctk.CTkButton(self.settings_frame, text="Outline Color", fg_color="gray30", command=self.choose_color)
        self.btn_color.pack(pady=5, padx=15, anchor="w")
        
        ctk.CTkLabel(self.settings_frame, text="Inner Outline Mode:", font=("Arial", 12, "bold")).pack(pady=(10, 0), anchor="w", padx=15)
        self.inner_mode_frame = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        self.inner_mode_frame.pack(pady=(0, 10), padx=10, fill="x")
        self.rb_inner_black = ctk.CTkRadioButton(self.inner_mode_frame, text="Color", variable=self.inner_outline_mode_var, value=INNER_OUTLINE_BLACK, command=self.update_preview)
        self.rb_inner_black.pack(side="left", padx=5)
        self.rb_inner_shaded = ctk.CTkRadioButton(self.inner_mode_frame, text="Shaded", variable=self.inner_outline_mode_var, value=INNER_OUTLINE_SHADED, command=self.update_preview)
        self.rb_inner_shaded.pack(side="left", padx=5)

        ctk.CTkCheckBox(self.right_frame, text="Mirror Image", variable=self.mirror_var, command=self.update_preview).pack(pady=10, padx=10, anchor="w")

        self.info_label = ctk.CTkLabel(self, text="Ready", font=("Arial", 11))
        self.info_label.grid(row=2, column=0, columnspan=2, pady=5)

    def load_by_nick(self):
        nick = self.nick_entry.get().strip()
        if not nick: return
        self.info_label.configure(text=f"Loading Nick: {nick}...")
        try:
            resp = requests.get(f"https://minotar.net/skin/{nick}", timeout=10)
            if resp.status_code == 200:
                self.current_skin_img = Image.open(BytesIO(resp.content))
                self.info_label.configure(text=f"Loaded nick: {nick}")
                self.generate_preview()
            else: messagebox.showerror("Error", "User not found")
        except: messagebox.showerror("Error", "Network error")

    def update_outline_settings(self):
        st = "disabled" if not self.outer_outline_var.get() else "normal"
        self.rb_inner_black.configure(state=st)
        self.rb_inner_shaded.configure(state=st)
        self.update_preview()

    def choose_color(self):
        color_code = colorchooser.askcolor(title="Outline Color", initialcolor="#000000")
        if color_code[0]:
            self.outline_color = tuple(map(int, color_code[0]))
            self.btn_color.configure(border_color=color_code[1], border_width=2)
            self.update_preview()

    def select_skin(self):
        file_path = filedialog.askopenfilename(filetypes=[("PNG images", "*.png")])
        if file_path:
            self.current_skin_img = Image.open(file_path)
            self.info_label.configure(text=f"File: {os.path.basename(file_path)}")
            self.generate_preview()

    def update_preview(self):
        if self.current_skin_img: self.generate_preview()

    def generate_preview(self):
        res = process_avatar(self.current_skin_img, self.outer_outline_var.get(), self.inner_outline_mode_var.get(), self.outline_color)
        if res:
            if self.mirror_var.get(): res = res.transpose(Image.FLIP_LEFT_RIGHT)
            self.result_image = res
            ups = res.resize((300, 300), Image.NEAREST)
            img = ctk.CTkImage(light_image=ups, dark_image=ups, size=(300, 300))
            self.preview_label.configure(image=img, text="")
            self.btn_save.configure(state="normal")

    def save_avatar(self):
        if self.result_image:
            path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png")], initialfile="avatar.png")
            if path:
                self.result_image.save(path)
                messagebox.showinfo("OK", "Saved!")

if __name__ == "__main__":
    app = AvatarApp()
    app.mainloop()