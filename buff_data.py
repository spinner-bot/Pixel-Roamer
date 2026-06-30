"""
Buff 数据定义 — 57 个 buff。高质量 24×24 矢量图标。
"""
from buff_system import BuffType, register, CAT_POSITIVE, CAT_NEUTRAL, CAT_NEGATIVE
G = 24

# Proto helpers
def F(r,g,b): return ("fill",(r,g,b))
def R(x,y,w,h,c): return ("rect",x,y,w,h,c)
def C(x,y,r,c): return ("circle",x,y,r,c)

# Icon builders
def heart(): return [('fill', (40, 20, 50)), ('circle', 12, 12, 5, (255, 100, 140)), ('rect', 10, 10, 2, 3, (255, 100, 140)), ('rect', 8, 8, 2, 3, (255, 100, 140)), ('rect', 7, 7, 2, 2, (255, 255, 255)), ('rect', 14, 7, 2, 2, (255, 255, 255))]

def shield(): return [('fill', (30, 25, 40)), ('rect', 7, 2, 10, 14, (100, 180, 255)), ('rect', 9, 4, 6, 10, (140, 220, 295)), ('rect', 5, 7, 14, 2, (100, 180, 255)), ('rect', 10, 6, 4, 6, (255, 255, 255))]

def fire(): return [('fill', (40, 15, 10)), ('circle', 12, 14, 4, (255, 180, 30)), ('circle', 10, 10, 2, (255, 200, 60)), ('rect', 11, 5, 2, 4, (255, 120, 20)), ('circle', 14, 12, 2, (255, 140, 30)), ('rect', 13, 4, 2, 5, (255, 160, 40)), ('circle', 13, 16, 2, (200, 100, 10))]

def drop(): return [('fill', (20, 25, 45)), ('circle', 12, 16, 3, (80, 150, 255)), ('rect', 11, 8, 2, 6, (140, 210, 315)), ('rect', 10, 10, 4, 2, (80, 150, 255)), ('circle', 12, 9, 2, (255, 255, 255))]

def web(): return [('fill', (25, 20, 35)), ('circle', 12, 12, 7, (180, 180, 200)), ('circle', 12, 12, 4, (210, 210, 230)), ('rect', 12, 5, 1, 14, (150, 150, 170)), ('rect', 5, 12, 14, 1, (150, 150, 170)), ('rect', 7, 7, 10, 1, (150, 150, 170)), ('rect', 7, 16, 10, 1, (150, 150, 170))]

def wing(): return [('fill', (30, 35, 60)), ('rect', 4, 8, 7, 8, (200, 220, 255)), ('rect', 11, 8, 2, 5, (200, 220, 255)), ('rect', 13, 6, 3, 3, (200, 220, 255)), ('rect', 11, 12, 2, 4, (160, 180, 215)), ('circle', 15, 6, 2, (255, 255, 255))]

def bolt(): return [('fill', (40, 30, 15)), ('rect', 12, 3, 2, 6, (255, 220, 50)), ('rect', 9, 8, 4, 2, (255, 220, 50)), ('rect', 10, 10, 2, 4, (255, 220, 50)), ('rect', 10, 14, 4, 2, (195, 160, -10)), ('rect', 12, 16, 2, 6, (195, 160, -10)), ('circle', 13, 8, 2, (255, 255, 255))]

def skull(): return [('fill', (20, 18, 30)), ('circle', 12, 12, 6, (220, 200, 180)), ('circle', 9, 10, 2, (40, 30, 40)), ('circle', 15, 10, 2, (40, 30, 40)), ('rect', 10, 16, 4, 2, (220, 200, 180)), ('rect', 11, 15, 2, 1, (40, 30, 40))]

def eye(): return [('fill', (20, 20, 35)), ('circle', 12, 12, 6, (255, 255, 200)), ('circle', 12, 12, 3, (40, 30, 60)), ('circle', 12, 12, 1, (255, 255, 255)), ('rect', 8, 10, 8, 1, (205, 205, 150)), ('rect', 8, 14, 8, 1, (205, 205, 150))]

def sword(): return [('fill', (30, 25, 35)), ('rect', 11, 3, 2, 14, (200, 200, 220)), ('rect', 10, 2, 4, 1, (240, 240, 260)), ('rect', 10, 17, 4, 2, (100, 70, 40)), ('rect', 13, 14, 2, 3, (100, 70, 40)), ('rect', 7, 14, 2, 3, (100, 70, 40))]

def feather(): return [('fill', (30, 28, 40)), ('rect', 11, 3, 2, 17, (220, 210, 180)), ('rect', 8, 5, 5, 2, (220, 210, 180)), ('rect', 9, 8, 4, 1, (190, 180, 150)), ('rect', 8, 10, 3, 1, (190, 180, 150)), ('rect', 9, 13, 2, 1, (190, 180, 150))]

def star(): return [('fill', (30, 25, 20)), ('circle', 12, 12, 8, (40, 35, 25)), ('circle', 12, 12, 5, (255, 240, 100)), ('circle', 12, 12, 2, (255, 255, 255))]

def clock(): return [('fill', (25, 25, 40)), ('circle', 12, 12, 8, (200, 200, 230)), ('circle', 12, 12, 6, (160, 160, 190)), ('rect', 12, 8, 1, 5, (120, 120, 150)), ('rect', 12, 7, 4, 1, (120, 120, 150)), ('circle', 12, 12, 1, (255, 255, 255))]

def chain(): return [('fill', (30, 25, 30)), ('circle', 7, 7, 3, (180, 170, 150)), ('circle', 17, 17, 3, (180, 170, 150)), ('rect', 9, 6, 6, 2, (180, 170, 150)), ('rect', 15, 15, 6, 2, (180, 170, 150)), ('circle', 12, 12, 3, (140, 130, 110))]

def cross(): return [('fill', (35, 20, 25)), ('rect', 8, 2, 8, 4, (255, 80, 80)), ('rect', 10, 6, 4, 12, (255, 80, 80)), ('rect', 8, 14, 8, 4, (255, 80, 80)), ('rect', 8, 6, 2, 8, (215, 40, 40))]

def arrow_up(): return [('fill', (25, 30, 25)), ('rect', 11, 4, 2, 16, (100, 255, 100)), ('rect', 8, 7, 5, 2, (100, 255, 100)), ('rect', 13, 5, 2, 6, (100, 255, 100)), ('rect', 10, 0, 4, 6, (100, 255, 100))]

def arrow_down(): return [('fill', (25, 25, 30)), ('rect', 11, 4, 2, 16, (255, 100, 100)), ('rect', 8, 12, 5, 2, (255, 100, 100)), ('rect', 13, 10, 2, 6, (255, 100, 100)), ('rect', 10, 16, 4, 6, (255, 100, 100))]

def wall(): return [('fill', (30, 28, 35)), ('rect', 2, 6, 20, 12, (150, 150, 170)), ('rect', 2, 6, 20, 2, (170, 170, 190)), ('rect', 6, 8, 4, 4, (120, 120, 140)), ('rect', 14, 8, 4, 4, (120, 120, 140)), ('rect', 10, 10, 4, 4, (120, 120, 140))]

def snail(): return [('fill', (30, 30, 20)), ('circle', 16, 10, 5, (200, 180, 150)), ('circle', 16, 10, 3, (230, 210, 180)), ('rect', 6, 12, 8, 3, (200, 180, 150)), ('circle', 7, 12, 2, (40, 30, 20)), ('rect', 5, 13, 1, 2, (40, 30, 20))]

def spiral(): return [('fill', (30, 25, 40)), ('circle', 12, 12, 8, (40, 35, 50)), ('circle', 12, 6, 2, (255, 220, 80)), ('circle', 18, 12, 2, (255, 220, 80)), ('circle', 12, 18, 2, (255, 220, 80)), ('circle', 6, 12, 2, (255, 220, 80)), ('circle', 16, 8, 2, (195, 160, 20)), ('circle', 8, 16, 2, (195, 160, 20))]

def magnet(): return [('fill', (25, 25, 40)), ('rect', 6, 4, 12, 5, (200, 100, 100)), ('rect', 4, 9, 4, 10, (140, 40, 40)), ('rect', 16, 9, 4, 10, (200, 100, 100)), ('rect', 7, 4, 10, 3, (230, 130, 130))]

def anchor(): return [('fill', (25, 25, 35)), ('rect', 11, 2, 2, 16, (150, 140, 180)), ('rect', 8, 7, 8, 2, (150, 140, 180)), ('rect', 6, 16, 12, 3, (150, 140, 180)), ('circle', 8, 5, 2, (150, 140, 180)), ('circle', 16, 5, 2, (150, 140, 180))]

def antenna(): return [('fill', (25, 25, 35)), ('rect', 11, 4, 2, 14, (180, 200, 240)), ('circle', 12, 4, 4, (210, 230, 270)), ('circle', 4, 8, 3, (210, 230, 270)), ('circle', 20, 8, 3, (210, 230, 270)), ('rect', 4, 8, 16, 1, (180, 200, 240))]

def xmouth(): return [('fill', (30, 20, 25)), ('circle', 12, 8, 7, (220, 180, 150)), ('circle', 9, 7, 2, (40, 30, 40)), ('circle', 15, 7, 2, (40, 30, 40)), ('rect', 8, 14, 3, 1, (200, 100, 100)), ('rect', 13, 14, 3, 1, (200, 100, 100)), ('rect', 9, 13, 6, 2, (200, 100, 100)), ('rect', 9, 15, 2, 3, (200, 100, 100)), ('rect', 14, 15, 2, 3, (200, 100, 100))]

def aura(): return [('fill', (40, 35, 20)), ('circle', 12, 12, 9, (155, 120, 0)), ('circle', 12, 12, 5, (255, 220, 100)), ('circle', 12, 12, 2, (255, 255, 255)), ('rect', 7, 7, 10, 10, (255, 220, 100)), ('circle', 12, 12, 3, (275, 240, 120))]

def blood(): return [('fill', (30, 15, 15)), ('circle', 11, 14, 4, (200, 30, 30)), ('circle', 10, 12, 2, (240, 70, 70)), ('rect', 10, 16, 2, 4, (200, 30, 30)), ('circle', 13, 17, 1, (255, 255, 255))]

def zzz(): return [('fill', (20, 22, 35)), ('rect', 10, 3, 4, 2, (160, 180, 210)), ('rect', 8, 3, 2, 1, (120, 140, 170)), ('rect', 14, 3, 2, 1, (120, 140, 170)), ('rect', 8, 8, 4, 2, (160, 180, 210)), ('rect', 13, 13, 4, 2, (160, 180, 210))]

def cracked_heart(): return [('fill', (25, 15, 20)), ('circle', 8, 9, 3, (200, 40, 40)), ('circle', 16, 9, 3, (200, 40, 40)), ('rect', 7, 8, 10, 2, (200, 40, 40)), ('rect', 9, 10, 6, 2, (200, 40, 40)), ('rect', 10, 12, 4, 4, (200, 40, 40)), ('rect', 11, 14, 2, 2, (200, 40, 40)), ('rect', 12, 4, 1, 8, (30, 5, 5)), ('rect', 14, 7, 1, 4, (30, 5, 5)), ('rect', 11, 9, 3, 1, (30, 5, 5))]

def snowflake(): return [('fill', (20, 30, 50)), ('rect', 11, 2, 2, 20, (200, 230, 255)), ('rect', 2, 11, 20, 2, (200, 230, 255)), ('rect', 8, 7, 8, 1, (200, 230, 255)), ('rect', 13, 3, 1, 10, (200, 230, 255)), ('rect', 10, 13, 4, 1, (200, 230, 255)), ('circle', 12, 12, 2, (255, 255, 255))]

def hourglass(): return [('fill', (25, 22, 35)), ('rect', 8, 2, 8, 2, (200, 180, 150)), ('rect', 9, 4, 6, 6, (200, 180, 150)), ('rect', 11, 10, 2, 4, (200, 180, 150)), ('rect', 9, 14, 6, 6, (200, 180, 150)), ('rect', 8, 20, 8, 2, (200, 180, 150)), ('circle', 12, 12, 2, (255, 255, 255))]

def target(): return [('fill', (25, 25, 30)), ('circle', 12, 12, 8, (255, 80, 80)), ('circle', 12, 12, 5, (195, 20, 20)), ('circle', 12, 12, 2, (255, 80, 80)), ('rect', 11, 12, 2, 1, (255, 255, 255)), ('rect', 12, 11, 1, 2, (255, 255, 255))]

def bat(): return [('fill', (30, 25, 40)), ('rect', 10, 8, 4, 4, (80, 70, 100)), ('rect', 8, 5, 2, 6, (80, 70, 100)), ('rect', 15, 5, 2, 6, (80, 70, 100)), ('rect', 6, 9, 4, 3, (50, 40, 70)), ('rect', 15, 9, 4, 3, (50, 40, 70))]

def clover(): return [('fill', (20, 30, 25)), ('circle', 8, 8, 3, (50, 200, 80)), ('circle', 8, 8, 1, (110, 260, 140)), ('circle', 16, 8, 3, (50, 200, 80)), ('circle', 16, 16, 3, (50, 200, 80)), ('circle', 8, 16, 3, (50, 200, 80)), ('rect', 11, 14, 2, 8, (30, 180, 60))]

def phoenix(): return [('fill', (35, 15, 10)), ('circle', 12, 14, 5, (255, 150, 30)), ('circle', 10, 10, 3, (255, 200, 80)), ('rect', 10, 4, 2, 5, (255, 150, 30)), ('rect', 14, 6, 3, 3, (255, 220, 100)), ('rect', 8, 7, 8, 2, (255, 200, 80)), ('circle', 16, 8, 2, (255, 255, 255))]

def shadow(): return [('fill', (15, 10, 25)), ('circle', 12, 14, 6, (60, 50, 80)), ('circle', 12, 14, 3, (100, 90, 120)), ('rect', 13, 7, 1, 6, (40, 30, 60))]

def mirror(): return [('fill', (25, 25, 40)), ('circle', 7, 8, 4, (150, 200, 240)), ('circle', 17, 8, 4, (150, 200, 240)), ('rect', 11, 11, 2, 6, (150, 200, 240)), ('circle', 7, 15, 2, (150, 200, 240)), ('circle', 17, 15, 2, (150, 200, 240))]

def rock(): return [('fill', (25, 22, 30)), ('rect', 4, 8, 16, 10, (140, 130, 120)), ('rect', 6, 6, 12, 4, (160, 150, 140)), ('rect', 3, 10, 6, 3, (120, 110, 100)), ('rect', 15, 12, 4, 4, (120, 110, 100))]

def vial(): return [('fill', (20, 30, 25)), ('rect', 10, 2, 4, 4, (40, 195, 60)), ('rect', 9, 6, 6, 14, (100, 255, 120)), ('rect', 10, 7, 4, 8, (130, 285, 150)), ('circle', 12, 12, 2, (40, 195, 60))]

def cloud(): return [('fill', (40, 38, 50)), ('circle', 10, 10, 5, (200, 200, 220)), ('circle', 16, 10, 4, (180, 180, 200)), ('circle', 13, 8, 4, (200, 200, 220)), ('circle', 8, 8, 3, (180, 180, 200)), ('rect', 9, 9, 8, 8, (200, 200, 220))]

# ====== 37 existing buffs (redesigned icons) ======

# Composite icons
shield_fire = [('fill', (30, 25, 40)), ('rect', 7, 2, 10, 14, (255, 140, 50)), ('rect', 9, 4, 6, 10, (295, 180, 90)), ('rect', 5, 7, 14, 2, (255, 140, 50)), ('rect', 10, 6, 4, 6, (255, 255, 255)), ('rect', 9, 9, 6, 6, (255, 200, 50))]
shield_spike = [('fill', (30, 25, 40)), ('rect', 7, 2, 10, 14, (180, 200, 100)), ('rect', 9, 4, 6, 10, (220, 240, 140)), ('rect', 5, 7, 14, 2, (180, 200, 100)), ('rect', 10, 6, 4, 6, (255, 255, 255)), ('rect', 10, 8, 4, 8, (100, 140, 40)), ('rect', 8, 9, 8, 2, (100, 140, 40)), ('rect', 9, 12, 6, 2, (100, 140, 40))]
soaked = [('fill', (20, 25, 45)), ('circle', 12, 16, 3, (100, 160, 240)), ('rect', 11, 8, 2, 6, (160, 220, 300)), ('rect', 10, 10, 4, 2, (100, 160, 240)), ('circle', 12, 9, 2, (255, 255, 255)), ('rect', 8, 10, 8, 4, (120, 200, 255))]
blood_drop = [('fill', (30, 15, 15)), ('circle', 11, 14, 4, (200, 30, 30)), ('circle', 10, 12, 2, (240, 70, 70)), ('rect', 10, 16, 2, 4, (200, 30, 30)), ('circle', 13, 17, 1, (255, 255, 255)), ('rect', 8, 12, 8, 1, (255, 60, 60))]
reverse = [('fill', (25, 25, 35)), ('rect', 4, 9, 6, 2, (255, 150, 100)), ('rect', 14, 9, 6, 2, (100, 150, 255)), ('rect', 8, 8, 2, 4, (255, 150, 100)), ('rect', 14, 8, 2, 4, (100, 150, 255)), ('rect', 9, 7, 6, 1, (255, 200, 150)), ('rect', 9, 16, 6, 1, (150, 200, 255))]
blinded = [('fill', (20, 20, 35)), ('circle', 12, 12, 6, (255, 240, 50)), ('circle', 12, 12, 3, (40, 30, 60)), ('circle', 12, 12, 1, (255, 255, 255)), ('rect', 8, 10, 8, 1, (205, 190, 0)), ('rect', 8, 14, 8, 1, (205, 190, 0)), ('rect', 9, 10, 6, 2, (200, 0, 0)), ('rect', 10, 9, 4, 4, (200, 0, 0))]
tunnel = [('fill', (10, 10, 20)), ('circle', 12, 12, 7, (40, 40, 60)), ('circle', 12, 12, 4, (100, 100, 130)), ('circle', 12, 12, 2, (180, 180, 200))]
armor_break = [('fill', (30, 25, 40)), ('rect', 7, 2, 10, 14, (100, 100, 100)), ('rect', 9, 4, 6, 10, (140, 140, 140)), ('rect', 5, 7, 14, 2, (100, 100, 100)), ('rect', 10, 6, 4, 6, (255, 255, 255)), ('rect', 7, 9, 10, 2, (200, 40, 40)), ('rect', 9, 7, 2, 10, (200, 40, 40))]
sword_x = [('fill', (30, 25, 35)), ('rect', 11, 3, 2, 14, (200, 200, 220)), ('rect', 10, 2, 4, 1, (240, 240, 260)), ('rect', 10, 17, 4, 2, (100, 70, 40)), ('rect', 13, 14, 2, 3, (100, 70, 40)), ('rect', 7, 14, 2, 3, (100, 70, 40)), ('rect', 7, 7, 10, 2, (200, 60, 60)), ('rect', 9, 7, 2, 10, (200, 60, 60))]
hopping = [('fill', (25, 30, 25)), ('rect', 11, 4, 2, 16, (255, 200, 100)), ('rect', 8, 7, 5, 2, (255, 200, 100)), ('rect', 13, 5, 2, 6, (255, 200, 100)), ('rect', 10, 0, 4, 6, (255, 200, 100)), ('rect', 7, 7, 10, 2, (200, 40, 40)), ('rect', 9, 7, 2, 10, (200, 40, 40))]
phys_immune = [('fill', (30, 25, 35)), ('rect', 11, 3, 2, 14, (255, 200, 100)), ('rect', 10, 2, 4, 1, (295, 240, 140)), ('rect', 10, 17, 4, 2, (100, 70, 40)), ('rect', 13, 14, 2, 3, (100, 70, 40)), ('rect', 7, 14, 2, 3, (100, 70, 40)), ('circle', 12, 12, 2, (255, 255, 180)), ('circle', 12, 12, 1, (255, 255, 255))]
mag_immune = [('fill', (30, 25, 20)), ('circle', 12, 12, 8, (40, 35, 25)), ('circle', 12, 12, 5, (255, 240, 100)), ('circle', 12, 12, 2, (255, 255, 255)), ('circle', 12, 12, 2, (255, 255, 180)), ('circle', 12, 12, 1, (255, 255, 255))]
djump = [('fill', (30, 35, 60)), ('rect', 4, 8, 7, 8, (200, 220, 255)), ('rect', 11, 8, 2, 5, (200, 220, 255)), ('rect', 13, 6, 3, 3, (200, 220, 255)), ('rect', 11, 12, 2, 4, (160, 180, 215)), ('circle', 15, 6, 2, (255, 255, 255)), ('circle', 12, 16, 2, (255, 255, 255)), ('circle', 8, 14, 2, (255, 255, 255))]
shadow_blue = [('fill', (15, 10, 25)), ('circle', 12, 14, 6, (100, 140, 200)), ('circle', 12, 14, 3, (160, 200, 240)), ('rect', 13, 7, 1, 6, (60, 100, 160))]
stone_body = [('fill', (25, 22, 30)), ('rect', 4, 8, 16, 10, (160, 150, 140)), ('rect', 6, 6, 12, 4, (180, 170, 160)), ('rect', 3, 10, 6, 3, (140, 130, 120)), ('rect', 15, 12, 4, 4, (140, 130, 120)), ('rect', 10, 10, 4, 6, (120, 110, 100))]
iron_heart = [('fill', (25, 22, 30)), ('rect', 4, 8, 16, 10, (180, 160, 100)), ('rect', 6, 6, 12, 4, (200, 180, 120)), ('rect', 3, 10, 6, 3, (160, 140, 80)), ('rect', 15, 12, 4, 4, (160, 140, 80)), ('rect', 10, 9, 4, 6, (255, 240, 80)), ('circle', 12, 12, 2, (255, 255, 255))]
berserk_icon = [('fill', (20, 18, 30)), ('circle', 12, 12, 6, (255, 100, 40)), ('circle', 9, 10, 2, (40, 30, 40)), ('circle', 15, 10, 2, (40, 30, 40)), ('rect', 10, 16, 4, 2, (255, 100, 40)), ('rect', 11, 15, 2, 1, (40, 30, 40)), ('circle', 12, 16, 3, (255, 200, 50)), ('rect', 9, 7, 2, 5, (255, 150, 60)), ('rect', 13, 7, 2, 5, (255, 150, 60))]
slick_icon = [('fill', (30, 30, 40)), ('rect', 5, 10, 14, 4, (150, 200, 255)), ('rect', 7, 8, 10, 2, (200, 230, 255)), ('rect', 10, 2, 4, 8, (180, 210, 255)), ('rect', 6, 12, 3, 1, (255, 255, 255)), ('rect', 16, 12, 3, 1, (255, 255, 255))]
sticky_icon = [('fill', (30, 25, 20)), ('rect', 6, 6, 12, 8, (200, 160, 80)), ('rect', 8, 5, 2, 10, (180, 140, 60)), ('rect', 14, 5, 2, 10, (180, 140, 60)), ('rect', 7, 7, 10, 1, (255, 220, 140))]

register(BuffType(id=1, name="regen", name2="恢复", category=CAT_POSITIVE,
    desc="每秒恢复 {0} 点生命值",
    icon=("vector",(G,G),heart()),
    max_stacks=3, tick="regen",
))

register(BuffType(id=2, name="shield_regen", name2="护佑", category=CAT_POSITIVE,
    desc="每秒获得 {0} 点护盾",
    icon=("vector",(G,G),shield()),
    max_stacks=3, tick="shield_regen",
))

register(BuffType(id=3, name="swiftness", name2="迅捷", category=CAT_POSITIVE,
    desc="移动速度 +{0}%",
    icon=("vector",(G,G),wing()),
    max_stacks=2, tick="swiftness",
))

register(BuffType(id=4, name="leaping", name2="轻身", category=CAT_POSITIVE,
    desc="跳跃高度 +{0}%",
    icon=("vector",(G,G),arrow_up()),
    max_stacks=2, tick="leaping",
))

register(BuffType(id=5, name="vigor", name2="活力", category=CAT_POSITIVE,
    desc="体力恢复速度 +{0}%",
    icon=("vector",(G,G),bolt()),
    max_stacks=2, tick="vigor",
))

register(BuffType(id=6, name="endurance", name2="坚忍", category=CAT_POSITIVE,
    desc="体力消耗 -{0}%",
    icon=("vector",(G,G),rock()),
    max_stacks=1, tick="endurance",
))

register(BuffType(id=7, name="fortify", name2="坚守", category=CAT_POSITIVE,
    desc="受到伤害 -{0}%",
    icon=("vector",(G,G),wall()),
    max_stacks=2, tick="fortify",
))

register(BuffType(id=8, name="clarity", name2="清明", category=CAT_POSITIVE,
    desc="免疫方向反转和视野干扰",
    icon=("vector",(G,G),eye()),
    max_stacks=1, tick="clarity",
    conflicts=(23, 24, 25), cleanup_by=()))

register(BuffType(id=9, name="fire_resist", name2="耐火", category=CAT_POSITIVE,
    desc="免疫火焰和熔岩伤害",
    icon=("vector",(G,G),shield_fire),
    max_stacks=1, tick="fire_resist",
    conflicts=(), cleanup_by=(15,)))

register(BuffType(id=10, name="thornmail", name2="荆棘", category=CAT_POSITIVE,
    desc="反弹 {0}% 受到的伤害",
    icon=("vector",(G,G),shield_spike),
    max_stacks=3, tick="thornmail",
))

register(BuffType(id=11, name="lifesteal", name2="嗜血", category=CAT_POSITIVE,
    desc="造成伤害时回复其 {0}% 为生命",
    icon=("vector",(G,G),blood()),
    max_stacks=3, tick="lifesteal",
))

register(BuffType(id=12, name="cleansing", name2="净化", category=CAT_POSITIVE,
    desc="每 {0} 秒移除一个负面效果",
    icon=("vector",(G,G),drop()),
    max_stacks=1, tick="cleansing",
))

register(BuffType(id=13, name="feather", name2="轻羽", category=CAT_POSITIVE,
    desc="重力降低 {0}%",
    icon=("vector",(G,G),feather()),
    max_stacks=1, tick="feather",
))

register(BuffType(id=14, name="magnetic", name2="磁引", category=CAT_NEUTRAL,
    desc="自动吸引附近掉落物",
    icon=("vector",(G,G),magnet()),
    max_stacks=1, tick="magnetic",
))

register(BuffType(id=15, name="soaked", name2="浸湿", category=CAT_NEUTRAL,
    desc="处于潮湿状态（清除着火）",
    icon=("vector",(G,G),soaked),
    max_stacks=1, tick="soaked",
    conflicts=(16,), cleanup_by=()))

register(BuffType(id=16, name="burning", name2="着火", category=CAT_NEGATIVE,
    desc="每秒损失 {0} 点生命值，遇水清除",
    icon=("vector",(G,G),fire()),
    max_stacks=3, tick="burning",
    conflicts=(), cleanup_by=(15,)))

register(BuffType(id=17, name="bleeding", name2="流血", category=CAT_NEGATIVE,
    desc="每秒损失当前生命值的 {0}%",
    icon=("vector",(G,G),blood_drop),
    max_stacks=5, tick="bleeding",
))

register(BuffType(id=18, name="weakened", name2="脱力", category=CAT_NEGATIVE,
    desc="体力消耗速度 ×{0}",
    icon=("vector",(G,G),chain()),
    max_stacks=1, tick="weakened",
))

register(BuffType(id=19, name="fatigue", name2="疲倦", category=CAT_NEGATIVE,
    desc="体力恢复速度 -{0}%",
    icon=("vector",(G,G),zzz()),
    max_stacks=2, tick="fatigue",
))

register(BuffType(id=20, name="grievous_wound", name2="重伤", category=CAT_NEGATIVE,
    desc="受到的治疗效果 -{0}%",
    icon=("vector",(G,G),cracked_heart()),
    max_stacks=2, tick="grievous_wound",
))

register(BuffType(id=21, name="rooted", name2="定身", category=CAT_NEGATIVE,
    desc="无法左右移动",
    icon=("vector",(G,G),web()),
    max_stacks=1, tick="rooted",
))

register(BuffType(id=22, name="slowed", name2="缓步", category=CAT_NEGATIVE,
    desc="移动速度 -{0}%",
    icon=("vector",(G,G),snail()),
    max_stacks=3, tick="slowed",
))

register(BuffType(id=23, name="reversed", name2="反向", category=CAT_NEGATIVE,
    desc="操作方向左右反转",
    icon=("vector",(G,G),reverse),
    max_stacks=1, tick="reversed",
))

register(BuffType(id=24, name="blinded", name2="失明", category=CAT_NEGATIVE,
    desc="屏幕变亮黄色，仅能看清主角",
    icon=("vector",(G,G),blinded),
    max_stacks=1, tick="blinded",
))

register(BuffType(id=25, name="narrow_vision", name2="视野受限", category=CAT_NEGATIVE,
    desc="视野缩小为半径 {0} 格",
    icon=("vector",(G,G),tunnel),
    max_stacks=1, tick="narrow_vision",
))

register(BuffType(id=26, name="armor_break", name2="破甲", category=CAT_NEGATIVE,
    desc="无视所有免伤属性",
    icon=("vector",(G,G),armor_break),
    max_stacks=1, tick="armor_break",
))

register(BuffType(id=27, name="grounded", name2="压制", category=CAT_NEGATIVE,
    desc="无法跳跃",
    icon=("vector",(G,G),anchor()),
    max_stacks=1, tick="grounded",
))

register(BuffType(id=28, name="stunned", name2="晕眩", category=CAT_NEGATIVE,
    desc="无法移动、跳跃、交互",
    icon=("vector",(G,G),spiral()),
    max_stacks=1, tick="stunned",
))

register(BuffType(id=29, name="pierced", name2="穿甲", category=CAT_NEGATIVE,
    desc="伤害优先消耗血量，无视护盾",
    icon=("vector",(G,G),arrow_down()),
    max_stacks=1, tick="pierced",
))

register(BuffType(id=30, name="disarmed", name2="缴械", category=CAT_NEGATIVE,
    desc="无法使用道具",
    icon=("vector",(G,G),sword_x),
    max_stacks=1, tick="disarmed",
))

register(BuffType(id=31, name="interfered", name2="干扰", category=CAT_NEGATIVE,
    desc="无法使用技能",
    icon=("vector",(G,G),antenna()),
    max_stacks=1, tick="interfered",
))

register(BuffType(id=32, name="silenced_debuff", name2="沉默", category=CAT_NEGATIVE,
    desc="无法交互",
    icon=("vector",(G,G),xmouth()),
    max_stacks=1, tick="silenced_debuff",
))

register(BuffType(id=33, name="hopping", name2="跳跃锁定", category=CAT_NEGATIVE,
    desc="只能跳跃攀爬，无法水平移动",
    icon=("vector",(G,G),hopping),
    max_stacks=1, tick="hopping",
))

register(BuffType(id=34, name="physical_immune", name2="物理免疫", category=CAT_POSITIVE,
    desc="免疫物理伤害",
    icon=("vector",(G,G),phys_immune),
    max_stacks=1, tick="physical_immune",
))

register(BuffType(id=35, name="magic_immune", name2="法术免疫", category=CAT_POSITIVE,
    desc="免疫法术伤害",
    icon=("vector",(G,G),mag_immune),
    max_stacks=1, tick="magic_immune",
))

register(BuffType(id=36, name="full_immune", name2="完全免疫", category=CAT_POSITIVE,
    desc="免疫所有伤害（包括环境伤害）",
    icon=("vector",(G,G),aura()),
    max_stacks=1, tick="full_immune",
))

register(BuffType(id=37, name="double_jump", name2="二段跳", category=CAT_POSITIVE,
    desc="可在空中再跳跃一次",
    icon=("vector",(G,G),djump),
    max_stacks=1, tick="double_jump",
))

register(BuffType(id=38, name="stealth", name2="隐身", category=CAT_POSITIVE,
    desc="不会被敌人发现，持续 {0} 秒",
    icon=("vector",(G,G),shadow_blue),
    max_stacks=1, tick="stealth",
))

register(BuffType(id=39, name="stone_skin", name2="石肤", category=CAT_POSITIVE,
    desc="移动速度大幅下降，但免疫击退",
    icon=("vector",(G,G),stone_body),
    max_stacks=1, tick="stone_skin",
))

register(BuffType(id=40, name="iron_will", name2="铁意", category=CAT_POSITIVE,
    desc="免疫定身、晕眩、压制、混乱",
    icon=("vector",(G,G),iron_heart),
    max_stacks=1, tick="iron_will",
    conflicts=(21, 27, 28, 23), cleanup_by=()))

register(BuffType(id=41, name="surefooted", name2="稳足", category=CAT_POSITIVE,
    desc="免疫风力、水流、磁力等环境位移",
    icon=("vector",(G,G),anchor()),
    max_stacks=1, tick="surefooted",
))

register(BuffType(id=42, name="slick", name2="滑腻", category=CAT_NEUTRAL,
    desc="地面摩擦力大幅降低，如同在冰面上",
    icon=("vector",(G,G),slick_icon),
    max_stacks=1, tick="slick",
))

register(BuffType(id=43, name="sticky", name2="黏着", category=CAT_NEUTRAL,
    desc="地面摩擦力大幅增加，不易滑动",
    icon=("vector",(G,G),sticky_icon),
    max_stacks=1, tick="sticky",
))

register(BuffType(id=44, name="drowsy", name2="困倦", category=CAT_NEGATIVE,
    desc="每 {0} 秒有概率短暂晕眩",
    icon=("vector",(G,G),zzz()),
    max_stacks=1, tick="drowsy",
))

register(BuffType(id=45, name="electrified", name2="带电", category=CAT_NEUTRAL,
    desc="接触水体时持续受到伤害",
    icon=("vector",(G,G),bolt()),
    max_stacks=1, tick="electrified",
))

register(BuffType(id=46, name="inflamed", name2="发炎", category=CAT_NEGATIVE,
    desc="受到的治疗效果减半，火焰伤害翻倍",
    icon=("vector",(G,G),fire()),
    max_stacks=1, tick="inflamed",
))

register(BuffType(id=47, name="berserk", name2="狂暴", category=CAT_POSITIVE,
    desc="攻击力大幅提升，但持续损失生命值",
    icon=("vector",(G,G),berserk_icon),
    max_stacks=1, tick="berserk",
))

register(BuffType(id=48, name="ghostly", name2="幽灵", category=CAT_POSITIVE,
    desc="可以穿过单层薄墙，持续 {0} 秒",
    icon=("vector",(G,G),shadow()),
    max_stacks=1, tick="ghostly",
))

register(BuffType(id=49, name="magnetized", name2="磁化", category=CAT_NEUTRAL,
    desc="被附近的磁矿石吸引或排斥",
    icon=("vector",(G,G),magnet()),
    max_stacks=1, tick="magnetized",
))

register(BuffType(id=50, name="glowing", name2="发光", category=CAT_POSITIVE,
    desc="自身发出光芒照亮周围",
    icon=("vector",(G,G),star()),
    max_stacks=1, tick="glowing",
))

register(BuffType(id=51, name="chilled", name2="寒冷", category=CAT_NEGATIVE,
    desc="移动速度降低，入水后冻结加倍",
    icon=("vector",(G,G),snowflake()),
    max_stacks=3, tick="chilled",
))

register(BuffType(id=52, name="lucky", name2="幸运", category=CAT_POSITIVE,
    desc="效果结束时随机清除一个负面状态",
    icon=("vector",(G,G),clover()),
    max_stacks=2, tick="lucky",
))

register(BuffType(id=53, name="wind_walk", name2="风步", category=CAT_POSITIVE,
    desc="连续移动时获得越来越快的加速",
    icon=("vector",(G,G),cloud()),
    max_stacks=1, tick="wind_walk",
))

register(BuffType(id=54, name="anchored", name2="定锚", category=CAT_POSITIVE,
    desc="重力大幅增加，不会被水流风力移动",
    icon=("vector",(G,G),arrow_down()),
    max_stacks=1, tick="anchored",
))

register(BuffType(id=55, name="parasitic", name2="寄生", category=CAT_NEGATIVE,
    desc="每秒损失生命，被治愈时额外扣除等量生命",
    icon=("vector",(G,G),blood()),
    max_stacks=3, tick="parasitic",
))

register(BuffType(id=56, name="echo", name2="回声", category=CAT_NEUTRAL,
    desc="行动时发出声响，可能惊动敌人",
    icon=("vector",(G,G),antenna()),
    max_stacks=1, tick="echo",
))

register(BuffType(id=57, name="cursed", name2="诅咒", category=CAT_NEGATIVE,
    desc="无法获得任何有益状态",
    icon=("vector",(G,G),skull()),
    max_stacks=1, tick="cursed",
))
