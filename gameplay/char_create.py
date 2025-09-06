
import pygame
from systems.stats import RACES, CLASSES, build_stats
from core.config import SCREEN_SIZE
from core.asset_manager import get as assets_get
from core.settings import load_settings
from core.strings import t
from core.ui_fx import blit_cover
from ui.theme import get_font

GENDERS = ['Masculino', 'Feminino']

# Bonus application helpers
SIGN_BONUS = {
    'The Blade': {'STR': 1, 'MP%': 0, 'STA%': 0, 'DMG%': 0.10},
    'The Veil':  {'DEX': 1, 'MP%': 0, 'STA%': 0, 'STEALTH%': 0.10},
    'The Aether':{'INT': 1, 'MP%': 0.10, 'STA%': 0, 'DMG%': 0},
    'The Beast': {'END': 1, 'MP%': 0, 'STA%': 0.10, 'DMG%': 0},
}
SKILL_LIST = ['One-Handed','Two-Handed','Archery','Stealth','Conjuration','Elemental Magic']
SKILL_BONUS = {
    'One-Handed': {'STR': 1},
    'Two-Handed': {'STR': 1},
    'Archery': {'DEX': 1},
    'Stealth': {'DEX': 1},
    'Conjuration': {'INT': 1},
    'Elemental Magic': {'INT': 1},
}

class SceneCharCreate:
    def __init__(self, mgr, on_complete):
        self.mgr = mgr
        self.on_complete = on_complete
        self.font = get_font(36)
        self.small = get_font(22)
        self.bg = assets_get('ui.selection_player')
        st = load_settings()
        self.lang = st.get('language','en-US')
        # Steps: 0 Gender, 1 Race, 2 Class, 3 Sign, 4 Skills(2), 5 Name, 6 Summary
        self.step = 0
        self.sel_gender = 0
        self.races = list(RACES.keys())
        self.classes = list(CLASSES.keys())
        self.sel_race = 0
        self.sel_class = 0
        self.sel_sign = 0
        self.sel_skill_idx = 0
        self.chosen_skills: list[str] = []
        self.name = ''
        self._anim_t = 0.0
        self._anim_idx = 0

    def handle(self, events):
        for e in events:
            if e.type == pygame.KEYDOWN:
                if self.step in (0,1,2,3):
                    if e.key in (pygame.K_LEFT, pygame.K_a):
                        if self.step == 0: self.sel_gender = (self.sel_gender - 1) % len(GENDERS)
                        elif self.step == 1: self.sel_race = (self.sel_race - 1) % len(self.races)
                        elif self.step == 2: self.sel_class = (self.sel_class - 1) % len(self.classes)
                        else: self.sel_sign = (self.sel_sign - 1) % len(self._signs())
                    elif e.key in (pygame.K_RIGHT, pygame.K_d):
                        if self.step == 0: self.sel_gender = (self.sel_gender + 1) % len(GENDERS)
                        elif self.step == 1: self.sel_race = (self.sel_race + 1) % len(self.races)
                        elif self.step == 2: self.sel_class = (self.sel_class + 1) % len(self.classes)
                        else: self.sel_sign = (self.sel_sign + 1) % len(self._signs())
                    elif e.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.step += 1
                    elif e.key == pygame.K_ESCAPE:
                        if self.step > 0: self.step -= 1
                        else:
                            from gameplay.scene_mainmenu import SceneMainMenu
                            self.mgr.switch_to(SceneMainMenu(self.mgr))
                elif self.step == 4:  # skills (use localized list consistently)
                    skills = self._skills_localized()
                    if e.key in (pygame.K_LEFT, pygame.K_a):
                        self.sel_skill_idx = (self.sel_skill_idx - 1) % len(skills)
                    elif e.key in (pygame.K_RIGHT, pygame.K_d):
                        self.sel_skill_idx = (self.sel_skill_idx + 1) % len(skills)
                    elif e.key in (pygame.K_RETURN, pygame.K_SPACE):
                        cur = skills[self.sel_skill_idx]
                        if cur in self.chosen_skills:
                            self.chosen_skills.remove(cur)
                        elif len(self.chosen_skills) < 2:
                            self.chosen_skills.append(cur)
                        if len(self.chosen_skills) == 2:
                            self.step += 1
                    elif e.key == pygame.K_ESCAPE:
                        self.step -= 1
                elif self.step == 5:  # name
                    if e.key == pygame.K_RETURN and self.name.strip(): self.step = 6
                    elif e.key == pygame.K_BACKSPACE: self.name = self.name[:-1]
                    elif e.key == pygame.K_ESCAPE: self.step = 4
                    else:
                        ch = e.unicode
                        if ch and (ch.isalnum() or ch in ' _-') and len(self.name) < 16: self.name += ch
                elif self.step == 6:
                    if e.key in (pygame.K_RETURN, pygame.K_SPACE):
                        race = self.races[self.sel_race]
                        clazz = self.classes[self.sel_class]
                        stats = self._build_final_stats(race, clazz)
                        profile = {
                            'name': self.name.strip(),
                            'gender': GENDERS[self.sel_gender],
                            'race': race,
                            'clazz': clazz,
                            'sign': self._signs()[self.sel_sign],
                            'skills': list(self.chosen_skills),
                            'stats': stats,
                        }
                        self.on_complete(profile)
                    elif e.key == pygame.K_ESCAPE:
                        self.step = 5

    def _signs(self):
        return list(t('signs.list', self.lang))

    def _skills_localized(self):
        return list(t('skills.list', self.lang))

    def _build_final_stats(self, race, clazz):
        st = build_stats(race, clazz)
        # Map localized sign -> canonical by aligned index using the en-US list from t()
        signs_loc = self._signs()
        en_signs = list(t('signs.list', 'en-US'))
        try:
            idx = self.sel_sign % len(en_signs)
            canonical = en_signs[idx]
        except Exception:
            canonical = 'The Blade'
        sb = SIGN_BONUS.get(canonical, {})
        # attribute ups
        for k in ('STR','DEX','INT','VIT','END','WIS'):
            inc = sb.get(k, 0)
            if inc:
                setattr(st, k, getattr(st, k) + inc)
        # skills bonuses (map localized -> canonical by index)
        skills_loc = self._skills_localized()
        for s in self.chosen_skills:
            try:
                idx = skills_loc.index(s)
                canonical_s = SKILL_LIST[idx]
            except Exception:
                canonical_s = s
            b = SKILL_BONUS.get(canonical_s, {})
            for k, inc in b.items():
                setattr(st, k, getattr(st, k) + inc)
        # rebuild derived with percentages
        st.HP = 30 + st.VIT * 8
        st.MP = int((10 + st.INT * 8 + st.WIS * 4) * (1.0 + sb.get('MP%',0)))
        st.STA = int((20 + st.END * 6) * (1.0 + sb.get('STA%',0)))
        return st.__dict__

    def update(self, dt):
        self._anim_t += dt
        if self._anim_t >= 0.20:
            self._anim_t -= 0.20
            self._anim_idx = (self._anim_idx + 1) % 4

    def draw(self, screen):
        if self.bg: blit_cover(screen, self.bg)
        else: screen.fill((10,12,18))
        w,h = SCREEN_SIZE
        panel = pygame.Surface((int(w*0.80), int(h*0.70)), pygame.SRCALPHA)
        panel.fill((0,0,0,120))
        screen.blit(panel, (int(w*0.10), int(h*0.15)))
        titles = t('char.titles', self.lang)
        head = self.font.render(titles[self.step], True, (230,230,230))
        screen.blit(head, head.get_rect(center=(w//2, int(h*0.22))))
        if self.step == 0:
            opt = self.font.render(GENDERS[self.sel_gender], True, (240,220,160))
            screen.blit(opt, opt.get_rect(center=(w//2, int(h*0.45))))
            hint = t('char.hint.nav', self.lang)
            screen.blit(self.small.render(hint, True, (180,180,180)), (int(w*0.12), int(h*0.78)))
        elif self.step == 1:
            race = self.races[self.sel_race]
            race_label = t(f'race.{race}.name', self.lang)
            opt = self.font.render(race_label, True, (240,220,160))
            screen.blit(opt, opt.get_rect(center=(w//2, int(h*0.40))))
            desc = t(f'race.{race}.desc', self.lang)
            screen.blit(self.small.render(desc, True, (210,210,210)), (int(w*0.12), int(h*0.50)))
            hint = t('char.hint.nav', self.lang)
            screen.blit(self.small.render(hint, True, (180,180,180)), (int(w*0.12), int(h*0.78)))
        elif self.step == 2:
            clazz = self.classes[self.sel_class]
            label = t(f'class.{clazz}.name', self.lang)
            opt = self.font.render(label, True, (240,220,160))
            screen.blit(opt, opt.get_rect(center=(w//2, int(h*0.40))))
            desc = t(f'class.{clazz}.desc', self.lang)
            screen.blit(self.small.render(desc, True, (210,210,210)), (int(w*0.12), int(h*0.50)))
            hint = t('char.hint.nav', self.lang)
            screen.blit(self.small.render(hint, True, (180,180,180)), (int(w*0.12), int(h*0.78)))
        elif self.step == 3:
            signs = self._signs()
            sign = signs[self.sel_sign]
            opt = self.font.render(sign, True, (240,220,160))
            screen.blit(opt, opt.get_rect(center=(w//2, int(h*0.40))))
            # Map by index to canonical and translate description key properly
            en_signs = list(t('signs.list', 'en-US'))
            try:
                canonical = en_signs[self.sel_sign % len(en_signs)]
            except Exception:
                canonical = 'The Blade'
            desc = t('signs.desc.' + canonical, self.lang)
            screen.blit(self.small.render(desc, True, (210,210,210)), (int(w*0.12), int(h*0.50)))
            hint = t('char.hint.nav', self.lang)
            screen.blit(self.small.render(hint, True, (180,180,180)), (int(w*0.12), int(h*0.78)))
        elif self.step == 4:
            skills = self._skills_localized()
            cur = skills[self.sel_skill_idx]
            msg = f"{t('char.hint.skills', self.lang)}"
            screen.blit(self.small.render(msg, True, (180,180,180)), (int(w*0.12), int(h*0.78)))
            # Show full list and mark selected
            y = int(h*0.36)
            list_text = '  '.join([('['+s+']') if s in self.chosen_skills else s for s in skills])
            surf = self.small.render(list_text, True, (230,230,230))
            screen.blit(surf, surf.get_rect(center=(w//2, y)))
            cur_s = self.font.render(cur, True, (240,220,160))
            screen.blit(cur_s, cur_s.get_rect(center=(w//2, int(h*0.46))))
        elif self.step == 5:
            box = pygame.Rect(0,0, max(360, w//3), 52); box.center = (w//2, int(h*0.48))
            pygame.draw.rect(screen, (24,24,32), box, border_radius=6); pygame.draw.rect(screen, (90,90,120), box, 2, border_radius=6)
            txt = self.font.render(self.name or '', True, (240,220,160))
            screen.blit(txt, txt.get_rect(midleft=(box.left+12, box.centery)))
            hint = t('char.hint.name', self.lang)
            screen.blit(self.small.render(hint, True, (180,180,180)), (int(w*0.12), int(h*0.78)))
        else:
            race = self.races[self.sel_race]; clazz = self.classes[self.sel_class]
            st = self._build_final_stats(race, clazz)
            sign = self._signs()[self.sel_sign]
            lines = [
                f"Name: {self.name}",
                f"Gender: {GENDERS[self.sel_gender]}",
                f"Race: {t(f'race.{race}.name', self.lang)}",
                f"Class: {t(f'class.{clazz}.name', self.lang)}",
                f"Sign: {sign}",
                f"Skills: {', '.join(self.chosen_skills)}",
                f"HP: {st['HP']} MP: {st['MP']} STA: {st['STA']}",
                f"STR: {st['STR']} DEX: {st['DEX']} INT: {st['INT']}",
                f"VIT: {st['VIT']} END: {st['END']} WIS: {st['WIS']}",
                t('char.hint.summary', self.lang)
            ]
            y = int(h*0.30)
            for ln in lines:
                surf = self.small.render(ln, True, (230,230,230)); screen.blit(surf, (int(w*0.12), y)); y += 28
