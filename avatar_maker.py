import os
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from PIL import Image

def process_avatar(skin_path):
    try:
        skin = Image.open(skin_path).convert("RGBA")
        canvas = Image.new("RGBA", (37, 37), (0, 0, 0, 0))
        
        parts_grid = [[0 for _ in range(37)] for _ in range(37)]
        color_grid = [[(0,0,0,0) for _ in range(37)] for _ in range(37)]

        def get_texel(x, y):
            if 0 <= x < skin.width and 0 <= y < skin.height:
                return skin.getpixel((x, y))
            return (0, 0, 0, 0)

        def apply_shadow(color, factor):
            if color[3] == 0: return color
            return (int(color[0] * factor), int(color[1] * factor), int(color[2] * factor), color[3])

        for py in range(37):
            for px in range(37):
                x, y = px - 6, py - 5 
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
                    lx, ly = px - 3, py - 5
                    if 0 <= lx < 6 and 17 <= ly < 31:
                        c = get_texel(lx // 2 + 44, (ly - 17) // 2 + 36)
                        if c[3] < 25: c = get_texel(lx // 2 + 44, (ly - 17) // 2 + 20)
                        if c[3] >= 25: final_color, part_id = c, 4

                color_grid[py][px], parts_grid[py][px] = final_color, part_id

        for py in range(37):
            for px in range(37):
                curr_id = parts_grid[py][px]
                if curr_id == 0:
                    is_ext = False
                    for dy in [-1, 0, 1]:
                        for dx in [-1, 0, 1]:
                            if dy == 0 and dx == 0: continue
                            if 0 <= py+dy < 37 and 0 <= px+dx < 37:
                                nb_id = parts_grid[py+dy][px+dx]
                                if nb_id != 0:
                                    if abs(dx) + abs(dy) == 2:
                                        if dy == -1 and nb_id in [1, 3, 4]: is_ext = True
                                    else: is_ext = True
                            if is_ext: break
                        if is_ext: break
                    if is_ext: canvas.putpixel((px, py), (0, 0, 0, 255))
                else:
                    is_outline = False
                    for dy in [-1, 0, 1]:
                        for dx in [-1, 0, 1]:
                            if dy == 0 and dx == 0: continue
                            if 0 <= py+dy < 37 and 0 <= px+dx < 37:
                                nb_id = parts_grid[py+dy][px+dx]
                                if nb_id != 0 and nb_id != curr_id:
                                    if curr_id == 2 and nb_id == 1:
                                        if abs(dx) + abs(dy) == 1: is_outline = True
                                    elif curr_id in [1, 4] and nb_id == 3: is_outline = True
                                    elif nb_id == 2 and curr_id != 2 and curr_id != 1: is_outline = True
                                    if is_outline: break
                        if is_outline: break
                    if is_outline: canvas.putpixel((px, py), (0, 0, 0, 255))
                    else:
                        c = color_grid[py][px]
                        canvas.putpixel((px, py), (c[0], c[1], c[2], 255))
        return canvas
    except Exception as e:
        messagebox.showerror("Error", f"Processing failed: {e}")
        return None

class AvatarApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Avatar Maker")
        self.geometry("450x580")
        self.resizable(False, False)
        ctk.set_appearance_mode("dark")

        self.current_skin_path = None
        self.result_image = None

        self.label = ctk.CTkLabel(self, text="AVATAR GENERATOR", font=("Arial", 20, "bold"))
        self.label.pack(pady=20)

        self.preview_frame = ctk.CTkFrame(self, width=320, height=320)
        self.preview_frame.pack(pady=10)
        self.preview_frame.pack_propagate(False)

        self.preview_label = ctk.CTkLabel(self.preview_frame, text="No Image")
        self.preview_label.pack(expand=True, fill="both")

        self.btn_select = ctk.CTkButton(self, text="Select Skin", command=self.select_skin)
        self.btn_select.pack(pady=10)

        self.btn_save = ctk.CTkButton(self, text="Save Result", command=self.save_avatar, state="disabled")
        self.btn_save.pack(pady=10)

        self.info_label = ctk.CTkLabel(self, text="Ready", font=("Arial", 11))
        self.info_label.pack(side="bottom", pady=10)

    def select_skin(self):
        file_path = filedialog.askopenfilename(filetypes=[("PNG images", "*.png")])
        if file_path:
            self.current_skin_path = file_path
            self.generate_preview()

    def generate_preview(self):
        res = process_avatar(self.current_skin_path)
        if res:
            self.result_image = res
            upscaled_preview = res.resize((300, 300), Image.NEAREST)
            ctk_preview = ctk.CTkImage(light_image=upscaled_preview, 
                                      dark_image=upscaled_preview, 
                                      size=(300, 300))
            self.preview_label.configure(image=ctk_preview, text="")
            self.btn_save.configure(state="normal")
            self.info_label.configure(text=f"Loaded: {os.path.basename(self.current_skin_path)}")

    def save_avatar(self):
        if self.result_image:
            save_path = filedialog.asksaveasfilename(
                defaultextension=".png", 
                filetypes=[("PNG images", "*.png")],
                initialfile="avatar.png"
            )
            if save_path:
                self.result_image.save(save_path)
                messagebox.showinfo("Success", "Avatar saved!")

if __name__ == "__main__":
    app = AvatarApp()
    app.mainloop()