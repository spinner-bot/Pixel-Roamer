"""Small pixel ice cue and finite status countdown; rendering only."""
import math
import pygame
import game_text as gt


def draw_frozen_feedback(surface, actor, camera):
    if not actor.alive:
        return None
    effect = next((b for b in actor.buffs if b.buff_type and b.buff_type.tick == 'frozen'
                   and (b.duration is None or b.duration > 0)), None)
    if effect is None:
        return None
    body = camera.game_rect_to_screen_rect(actor.get_game_rect())
    if body.w <= 0 or body.h <= 0 or not body.colliderect(surface.get_rect()):
        return None
    pixel = max(1, min(3, round(camera.scale / 16)))
    # Allocate only the visible body, even when developer zoom makes the
    # projected actor much larger than the viewport.
    bounds = body.inflate(pixel * 2, pixel * 2).clip(surface.get_rect())
    ice = pygame.Surface(bounds.size, pygame.SRCALPHA)
    width, height = bounds.size
    corner = min(pixel * 2, (width - 1) // 2, (height - 1) // 2)
    outline = [(corner,0),(width-1-corner,0),(width-1,corner),
               (width-1,height-1-corner),(width-1-corner,height-1),
               (corner,height-1),(0,height-1-corner),(0,corner)]
    pygame.draw.polygon(ice,(136,220,244,45),outline)
    pygame.draw.lines(ice,(93,183,225,210),True,outline,pixel)
    pygame.draw.line(ice,(229,254,255,235),(corner,0),(width-1-corner,0),pixel)
    if width >= 7 and height >= 12:
        pygame.draw.line(ice,(185,239,251,145),(pixel*2,height//2),
                         (min(width-2,pixel*4),max(1,height//2-pixel*3)),pixel)
    surface.blit(ice,bounds.topleft)

    name = (effect.buff_type.name2 or '冻结')[:8]
    duration = effect.duration
    if duration is None:
        text = name
    elif not math.isfinite(duration) or duration >= 1000:
        text = name + ' 999+s'
    else:
        # Never claim0.0 while a finite lock still has a physical tick left.
        text = f'{name} {max(.1,math.ceil(duration*10-1e-9)/10):.1f}s'
    text_layer = pygame.Surface((192,24),pygame.SRCALPHA)
    text_width, _ = gt.draw(text_layer,text,0,0,14,(218,249,255),'mono')
    label = pygame.Surface((min(192,max(40,text_width+12)),24),pygame.SRCALPHA)
    label.fill((17,40,62,220))
    pygame.draw.rect(label,(98,180,213,235),label.get_rect(),1)
    label.blit(text_layer,(6,4))
    x = max(0,min(surface.get_width()-label.get_width(),body.centerx-label.get_width()//2))
    y = max(0,min(surface.get_height()-24,body.top-30))
    label_rect = surface.blit(label,(x,y))
    return {'body':bounds,'label':label_rect,'text':text}
