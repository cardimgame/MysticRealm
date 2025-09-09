# gameplay/character/scene_create_v2.py
from __future__ import annotations
import math, pygame
from core.settings import load_settings
from core.strings import t
from ui.theme import get_font, COLORS
from core.ui_fx import make_vignette, make_grain, tint
from gameplay.character import schema, builder, compute, portraits

STEP_GENDER = 0
STEP_RACE = 1
STEP_CLASS = 2
STEP_CONST = 3
STEP_SKILLS = 4
STEP_NAME = 5
STEP_SUMMARY = 6

PALETTE = getattr(__import__('ui.theme', fromlist=['PALETTE']), 'PALETTE', {
    'bg_deep': (12,16,24), 'panel': (18,20,28), 'edge': (70,90,120),
    'text_hi': (235,235,235), 'text_md': (210,210,220), 'accent': (230,210,160), 'accent2': (74,94,120)
})
ANIM = getattr(__import__('ui.theme', fromlist=['ANIM']), 'ANIM', {'step_fade_ms': 180,'step_slide_px': 10})

LABEL_PT = {'STR':'Força','DEX':'Destreza','INT':'Inteligência','CON':'Constituição'}
LABEL_EN = {'STR':'Strength','DEX':'Dexterity','INT':'Intelligence','CON':'Constitution'}

class SceneCreateV2:
    def __init__(self, mgr, on_complete=None):
        self.mgr = mgr
        self.on_complete = on_complete
        st = load_settings(); self.lang = st.get('language','en-US')
        self.h1 = get_font(42); self.h2 = get_font(28); self.body = get_font(22); self.small = get_font(18)
        self._fx_size = None; self.vignette = None; self.grain = None
        self.step = STEP_GENDER; self.sel_idx = 0; self.builder = builder.Builder()
        self._races = schema.race_keys(); self._classes = schema.class_keys(); self._consts = schema.const_keys(); self._skills = schema.skill_keys()
        self.skill_cursor = 0
        self._trans_t = 0.0; self._trans_dur = max(0.001, ANIM.get('step_fade_ms',180)/1000.0)

    def _ensure_fx(self, screen):
        size = screen.get_size()
        if self._fx_size != size:
            self._fx_size = size
            self.vignette = make_vignette(size, strength=0.75)
            self.grain = make_grain(size, intensity=22)

    def handle(self, events):
        for e in events:
            if e.type == pygame.QUIT: self.mgr.running = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    if self.step > STEP_GENDER: self._go_to(self.step - 1)
                    else:
                        from gameplay.scene_campaign import SceneCampaign
                        self.mgr.switch_to(SceneCampaign(self.mgr))
                elif e.key in (pygame.K_LEFT, pygame.K_a): self._left()
                elif e.key in (pygame.K_RIGHT, pygame.K_d): self._right()
                elif e.key in (pygame.K_RETURN, pygame.K_SPACE): self._confirm()
                elif self.step == STEP_NAME:
                    if e.key == pygame.K_BACKSPACE: self.builder.set_name(self.builder.s.name[:-1])
                    else:
                        ch = getattr(e, 'unicode', '')
                        if ch and (ch.isalnum() or ch in ' _-') and len(self.builder.s.name) < 16:
                            self.builder.set_name(self.builder.s.name + ch)

    def update(self, dt):
        if self._trans_t < self._trans_dur:
            self._trans_t = min(self._trans_dur, self._trans_t + dt)

    def _go_to(self, step: int):
        self.step = max(STEP_GENDER, min(STEP_SUMMARY, step)); self._trans_t = 0.0

    def _left(self):
        if self.step == STEP_GENDER:
            self.builder.set_gender(self.builder.s.gender_idx - 1)
        elif self.step == STEP_RACE and self._races:
            self.sel_idx = (self.sel_idx - 1) % len(self._races); self.builder.set_race(self._races[self.sel_idx])
        elif self.step == STEP_CLASS and self._classes:
            self.sel_idx = (self.sel_idx - 1) % len(self._classes); self.builder.set_class(self._classes[self.sel_idx])
        elif self.step == STEP_CONST and self._consts:
            self.sel_idx = (self.sel_idx - 1) % len(self._consts); self.builder.set_const(self._consts[self.sel_idx])
        elif self.step == STEP_SKILLS and self._skills:
            self.skill_cursor = (self.skill_cursor - 1) % len(self._skills)

    def _right(self):
        if self.step == STEP_GENDER:
            self.builder.set_gender(self.builder.s.gender_idx + 1)
        elif self.step == STEP_RACE and self._races:
            self.sel_idx = (self.sel_idx + 1) % len(self._races); self.builder.set_race(self._races[self.sel_idx])
        elif self.step == STEP_CLASS and self._classes:
            self.sel_idx = (self.sel_idx + 1) % len(self._classes); self.builder.set_class(self._classes[self.sel_idx])
        elif self.step == STEP_CONST and self._consts:
            self.sel_idx = (self.sel_idx + 1) % len(self._consts); self.builder.set_const(self._consts[self.sel_idx])
        elif self.step == STEP_SKILLS and self._skills:
            self.skill_cursor = (self.skill_cursor + 1) % len(self._skills)

    def _confirm(self):
        if self.step == STEP_GENDER:
            self._go_to(STEP_RACE); self.sel_idx = 0
            if self._races: self.builder.set_race(self._races[self.sel_idx])
        elif self.step == STEP_RACE and self.builder.valid_race():
            self._go_to(STEP_CLASS); self.sel_idx = 0
            if self._classes: self.builder.set_class(self._classes[self.sel_idx])
        elif self.step == STEP_CLASS and self.builder.valid_class():
            self._go_to(STEP_CONST); self.sel_idx = 0
            if self._consts: self.builder.set_const(self._consts[self.sel_idx])
        elif self.step == STEP_CONST and self.builder.valid_const():
            self._go_to(STEP_SKILLS); self.skill_cursor = 0
        elif self.step == STEP_SKILLS:
            curr = self._skills[self.skill_cursor]
            self.builder.toggle_skill(curr, max_skills=2)
            if self.builder.valid_skills(2): self._go_to(STEP_NAME)
        elif self.step == STEP_NAME and self.builder.valid_name():
            self._go_to(STEP_SUMMARY)
        elif self.step == STEP_SUMMARY:
            profile = compute.finalize(self.builder.snapshot())
            if callable(self.on_complete): self.on_complete(profile)
            else:
                from gameplay.scene_game import SceneGame
                self.mgr.switch_to(SceneGame(self.mgr, profile=profile))

    def _ease(self, t: float) -> float: return 0.5 - 0.5*math.cos(min(1.0,max(0.0,t)) * math.pi)
    def _anim_params(self):
        a = self._ease(self._trans_t / max(0.001, self._trans_dur)); alpha = int(255 * a); slide = int((1.0 - a) * 10)
        return alpha, slide

    def draw(self, screen):
        screen.fill((12,14,18)); self._ensure_fx(screen)
        tint(screen, color=(20,28,42), alpha=42)
        if self.vignette: screen.blit(self.vignette,(0,0))
        if self.grain: screen.blit(self.grain,(0,0))
        w, h = screen.get_size()
        title = self.h1.render(self._step_title(), True, PALETTE['text_hi'])
        screen.blit(title, title.get_rect(center=(w//2, int(h*0.14))))
        alpha, slide = self._anim_params()
        left = pygame.Rect(int(w*0.08), int(h*0.24)+slide, int(w*0.50), int(h*0.58))
        right= pygame.Rect(int(w*0.62), int(h*0.24)+slide, int(w*0.30), int(h*0.58))
        self._panel(screen, left, alpha); self._panel(screen, right, alpha)
        if self.step == STEP_GENDER: self._draw_gender(screen, left, right)
        elif self.step == STEP_RACE: self._draw_race(screen, left, right)
        elif self.step == STEP_CLASS: self._draw_class(screen, left, right)
        elif self.step == STEP_CONST: self._draw_const(screen, left, right)
        elif self.step == STEP_SKILLS: self._draw_skills(screen, left, right)
        elif self.step == STEP_NAME: self._draw_name(screen, left, right)
        elif self.step == STEP_SUMMARY: self._draw_summary(screen, left, right)
        hint = self.small.render(self._hint(), True, PALETTE['text_md'])
        step_txt = self.small.render(f"{self.step+1}/7", True, PALETTE['text_md'])
        screen.blit(hint, (int(w*0.08), int(h*0.86)))
        screen.blit(step_txt, step_txt.get_rect(topright=(int(w*0.92), int(h*0.86))))

    def _panel(self, screen, rect, alpha):
        p = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(p, (*PALETTE['panel'], 255), p.get_rect(), border_radius=10)
        pygame.draw.rect(p, (*PALETTE['edge'], 255), p.get_rect(), 1, border_radius=10)
        p.set_alpha(alpha); screen.blit(p, rect)

    def _step_title(self) -> str:
        keys = t('charv2.titles', self.lang)
        try: return keys[self.step]
        except Exception: return 'Create'

    def _hint(self) -> str:
        if self.step == STEP_NAME: return t('charv2.hint.name', self.lang)
        elif self.step == STEP_SUMMARY: return t('charv2.hint.summary', self.lang)
        elif self.step == STEP_SKILLS: return t('charv2.hint.skills', self.lang)
        return t('charv2.hint.nav', self.lang)

    def _label_map(self):
        return LABEL_PT if self.lang.startswith('pt') else LABEL_EN

    def _format_attrs(self, attrs: dict) -> str:
        lm = self._label_map(); parts = []
        for k in ('STR','DEX','INT','CON'):
            v = attrs.get(k,0)
            if v: parts.append(f"+{v} {lm[k]}")
        return ", ".join(parts)

    def _draw_paragraph(self, screen, text, rect, line_h=24, color=None):
        color = color or PALETTE['text_md']; y = rect.top
        words = (text or '').split(); cur = ''
        while words:
            test = (cur + ' ' + words[0]).strip(); w, _ = self.body.size(test)
            if w <= rect.width: cur = test; words.pop(0)
            else:
                if cur:
                    img = self.body.render(cur, True, color); screen.blit(img, (rect.left, y)); y += line_h
                cur = ''
                if not words: break
        if cur:
            img = self.body.render(cur, True, color); screen.blit(img, (rect.left, y)); y += line_h
        return y

    def _draw_gender(self, screen, left, right):
        g = builder.GENDERS[self.builder.s.gender_idx]
        head = self.h2.render(t('charv2.gender', self.lang), True, PALETTE['accent'])
        screen.blit(head, (left.left+18, left.top+16))
        txt = t('charv2.gender.desc', self.lang)
        self._draw_paragraph(screen, txt, pygame.Rect(left.left+18, left.top+60, left.width-36, left.height-80))
        choice = self.h2.render(g, True, PALETTE['text_hi'])
        screen.blit(choice, choice.get_rect(center=(right.centerx, right.centery)))

    def _draw_race(self, screen, left, right):
        if not self._races: return
        key = self._races[self.sel_idx]; self.builder.set_race(key)
        name = schema.race_label(key); lore = schema.race_lore(key)
        head = self.h2.render(name, True, PALETTE['accent'])
        screen.blit(head, (left.left+18, left.top+16))
        # BÔNUS DA RAÇA (novo)
        race_attrs = schema.race_info(key).attrs
        bonus_line = self._format_attrs(race_attrs)
        y = left.top + 56
        if bonus_line:
            screen.blit(self.body.render(bonus_line, True, (210,230,210)), (left.left+18, y)); y += 26
        # Lore abaixo
        self._draw_paragraph(screen, lore, pygame.Rect(left.left+18, y+6, left.width-36, left.height-120))
        # Retrato
        portr = portraits.get_portrait(key, builder.GENDERS[self.builder.s.gender_idx], (right.width-24, right.height-24))
        screen.blit(portr, portr.get_rect(center=right.center))

    def _draw_class(self, screen, left, right):
        if not self._classes: return
        key = self._classes[self.sel_idx]; self.builder.set_class(key)
        name = schema.class_label(key); lore = schema.class_lore(key)
        head = self.h2.render(name, True, PALETTE['accent'])
        screen.blit(head, (left.left+18, left.top+16))
        focus = schema.class_info(key).focus
        screen.blit(self.body.render(focus, True, (200,220,255)), (left.left+18, left.top+56))
        class_attrs = schema.class_info(key).attrs
        bonus_line = self._format_attrs(class_attrs)
        y = left.top + 84
        if bonus_line:
            screen.blit(self.body.render(bonus_line, True, (210,230,210)), (left.left+18, y)); y += 26
        else:
            y += 8
        self._draw_paragraph(screen, lore, pygame.Rect(left.left+18, y+6, left.width-36, left.height-160))

    def _draw_const(self, screen, left, right):
        if not self._consts: return
        key = self._consts[self.sel_idx]; self.builder.set_const(key)
        name = schema.const_label(key); lore = schema.const_lore(key)
        head = self.h2.render(name, True, PALETTE['accent'])
        screen.blit(head, (left.left+18, left.top+16))
        bonus = schema.const_info(key).bonus; perk = schema.const_info(key).perk
        y = left.top + 56
        bonus_line = self._format_attrs(bonus)
        if bonus_line:
            screen.blit(self.body.render(bonus_line, True, (210,230,210)), (left.left+18, y)); y += 26
        if perk:
            screen.blit(self.body.render(perk, True, (210,220,255)), (left.left+18, y)); y += 8
        self._draw_paragraph(screen, lore, pygame.Rect(left.left+18, y+10, left.width-36, left.height-160))

    def _draw_skills(self, screen, left, right):
        head = self.h2.render(t('charv2.skills', self.lang), True, PALETTE['accent'])
        screen.blit(head, (left.left+18, left.top+16))
        tip = self.small.render(t('charv2.hint.skills', self.lang), True, PALETTE['text_md'])
        screen.blit(tip, (left.left+18, left.top+56))
        y = left.top + 92
        for i,k in enumerate(self._skills):
            label = schema.skill_label(k)
            chosen = (k in self.builder.s.chosen_skills); cur = (i == self.skill_cursor)
            color = PALETTE['accent'] if cur else ((200,230,200) if chosen else PALETTE['text_md'])
            screen.blit(self.body.render(("[ "+label+" ]") if chosen else label, True, color), (left.left+18, y))
            y += 28
        # Detalhe da skill selecionada com bônus logo abaixo da descrição
        k = self._skills[self.skill_cursor]
        desc = schema.skill_desc(k)
        y2 = self._draw_paragraph(screen, desc, pygame.Rect(right.left+18, right.top+18, right.width-36, right.height-80))
        bonus_line = self._format_attrs(schema.skill_info(k).bonus)
        if bonus_line:
            screen.blit(self.body.render(bonus_line, True, (210,230,210)), (right.left+18, y2+6))

    def _draw_name(self, screen, left, right):
        head = self.h2.render(t('charv2.name', self.lang), True, PALETTE['accent'])
        screen.blit(head, (left.left+18, left.top+16))
        box = pygame.Rect(0,0, max(360, left.width//2), 54); box.center = (left.centerx, left.centery)
        pygame.draw.rect(screen, (24,24,32), box, border_radius=8)
        pygame.draw.rect(screen, (90,90,120), box, 2, border_radius=8)
        txt = self.h2.render(self.builder.s.name or '', True, (240,220,160))
        screen.blit(txt, txt.get_rect(midleft=(box.left+14, box.centery)))
        tip = self.small.render(t('charv2.hint.name', self.lang), True, PALETTE['text_md'])
        screen.blit(tip, (left.left+18, left.bottom-36))

    def _draw_summary(self, screen, left, right):
        s = self.builder.s; prof = compute.finalize(self.builder.snapshot())
        y = left.top + 16
        def L(key): return t(key, self.lang)
        lines = [
            (L('charv2.summary.name'), prof['name']),
            (L('charv2.summary.gender'), builder.GENDERS[s.gender_idx] if s else ''),
            (L('charv2.summary.race'), prof['race']),
            (L('charv2.summary.class'), prof['clazz']),
            (L('charv2.summary.sign'), prof['sign']),
            (L('charv2.summary.skills'), ', '.join(prof['skills'])),
        ]
        for lab, val in lines:
            screen.blit(self.body.render(f"{lab}: {val}", True, (230,230,230)), (left.left+18, y)); y += 26
        y += 8
        screen.blit(self.h2.render(L('charv2.summary.attributes'), True, PALETTE['accent']), (left.left+18, y)); y += 34
        for k,label in (("STR","Força"),("DEX","Destreza"),("INT","Inteligência"),("CON","Constituição")):
            screen.blit(self.body.render(f"{label}: {prof['stats'].get(k,0)}", True, (220,220,220)), (left.left+28, y)); y += 24
        y += 6
        screen.blit(self.h2.render(L('charv2.summary.derived'), True, PALETTE['accent']), (left.left+18, y)); y += 34
        derived = f"HP: {prof['stats'].get('HP',0)}  •  MP: {prof['stats'].get('MP',0)}  •  STA: {prof['stats'].get('STA',0)}"
        screen.blit(self.body.render(derived, True, (220,220,220)), (left.left+28, y)); y += 24
        if s and s.race_key is not None:
            portr = portraits.get_portrait(s.race_key, builder.GENDERS[s.gender_idx], (right.width-24, right.height-24))
            screen.blit(portr, portr.get_rect(center=right.center))
