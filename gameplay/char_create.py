import pygame
from typing import Any, Tuple
from systems.stats import RACES, CLASSES, build_stats
from core.asset_manager import get as assets_get
from core.settings import load_settings
from core.strings import t
from core.ui_fx import blit_fit
from ui.theme import get_font
from systems.stats_alias import canon_class
from core.asset import load_image_strict


def _wrap_text(text: str, font: Any, max_w: int):
    text = (text or "").replace('\r', '').strip()
    text = text.strip(',')
    if not text:
        return []
    words = text.split()
    lines = []
    cur = ""
    for w in words:
        test = (cur + " " + w).strip()
        try:
            width = font.size(test)[0]
        except Exception:
            width = len(test) * 8
        if width <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def _draw_paragraph(screen: pygame.Surface, text: str, font: Any, color: Tuple[int, int, int], rect: pygame.Rect, line_h: int = 24):
    y = rect.top
    for line in _wrap_text(text, font, rect.width):
        if y > rect.bottom:
            break
        try:
            img = font.render(line, True, color)
        except Exception:
            fallback = pygame.font.Font(None, font.get_height())
            img = fallback.render(line, True, color)
        screen.blit(img, (rect.left, y))
        y += line_h
    return min(y, rect.bottom)


def _fmt_bonus_lines(bonus: dict, namef=lambda k: k) -> list[str]:
    if not bonus:
        return []
    lines = []
    for k, v in (bonus or {}).items():
        name = namef(k)
        try:
            if isinstance(v, (int, float)) and "%" in k:
                lines.append(f"+{int(v * 100)}% {name}" if v else f"±0% {name}")
            else:
                vi = int(v)
                sign = "+" if vi >= 0 else ""
                lines.append(f"{sign}{vi} {name}")
        except Exception:
            lines.append(f"{v} {name}")
    return lines


GENDERS = ['Masculino', 'Feminino']
SIGN_BONUS = {
    'The Blade': {'STR': 1, 'MP%': 0.00, 'STA%': 0.00, 'DMG%': 0.10},
    'The Veil': {'DEX': 1, 'MP%': 0.00, 'STA%': 0.00, 'STEALTH%': 0.10},
    'The Aether': {'INT': 1, 'MP%': 0.10, 'STA%': 0.00, 'DMG%': 0.00},
    'The Beast': {'END': 1, 'MP%': 0.00, 'STA%': 0.10, 'DMG%': 0.00},
}
SKILL_LIST = ['One-Handed', 'Two-Handed', 'Archery', 'Stealth', 'Conjuration', 'Elemental Magic']
SKILL_BONUS = {
    'One-Handed': {'STR': 1},
    'Two-Handed': {'STR': 1},
    'Archery': {'DEX': 1},
    'Stealth': {'DEX': 1},
    'Conjuration': {'INT': 1},
    'Elemental Magic': {'INT': 1},
}


class SceneCharCreate:
    """Steps: 0 Gender 1 Race 2 Class 3 Sign 4 Skills 5 Name 6 Summary"""

    def __init__(self, mgr, on_complete):
        self.mgr = mgr
        self.on_complete = on_complete
        self.font = get_font(36)
        self.small = get_font(22)
        self.bg = assets_get('ui.selection_player')
        st = load_settings()
        self.lang = st.get('language', 'en-US')
        self.step = 0
        self.sel_gender = 0
        self.races = list(RACES.keys()) if RACES else []
        self.classes = list(CLASSES.keys()) if CLASSES else []
        self.sel_race = 0
        self.sel_class = 0
        self.sel_sign = 0
        self.sel_skill_idx = 0
        self.chosen_skills: list[str] = []
        self.name = ''
        # caches / slugs
        self._portrait_cache: dict[str, pygame.Surface] = {}
        self._RACE_SLUGS = {'Norther': 'humano', 'Valen': 'elfo', 'Durn': 'anao', 'Serathi': 'felino', 'Aetherborn': 'aetherborn'}
        self._GENDER_SLUGS = {'Masculino': 'masculino', 'Feminino': 'feminino'}
        self._PORTRAITS_DIR = 'player'
        self._portrait_margin = 18

    # === Helpers de i18n/UI ===
    def _L(self, key: str, pt: str, en: str) -> str:
        """Tenta localizar via t(key, lang). Se falhar, fallback por idioma (PT/EN)."""
        try:
            lbl = t(key, self.lang)
            if lbl:
                return str(lbl)
        except Exception:
            pass
        return pt if self.lang.lower().startswith('pt') else en

    def _attr_label(self, key: str) -> str:
        # Tenta via tabela de strings (seguindo padrão já implementado)
        for tk in (f'attr.{key}.short', f'attr.{key}.name', f'attr.{key}'):
            try:
                lbl = t(tk, self.lang)
            except Exception:
                lbl = None
            if lbl:
                return str(lbl)
        # Fallback por idioma (PT/EN)
        pt = {
            'STR': 'Força', 'DEX': 'Destreza', 'INT': 'Inteligência', 'WIS': 'Sabedoria', 'VIT': 'Vitalidade', 'END': 'Vigor',
            'HP': 'HP', 'MP': 'MP', 'STA': 'Stamina',
            'DMG%': 'Dano%', 'STEALTH%': 'Furtividade%', 'MP%': 'Mana%', 'STA%': 'Stamina%'
        }
        en = {
            'STR': 'STR', 'DEX': 'DEX', 'INT': 'INT', 'WIS': 'WIS', 'VIT': 'VIT', 'END': 'END',
            'HP': 'HP', 'MP': 'MP', 'STA': 'STA',
            'DMG%': 'Damage%', 'STEALTH%': 'Stealth%', 'MP%': 'Mana%', 'STA%': 'Stamina%'
        }
        return pt.get(key, key) if self.lang.lower().startswith('pt') else en.get(key, key)

    def _gender_display(self, idx: int) -> str:
        try:
            glist = list(t('gender.list', self.lang))
            if len(glist) > idx:
                return str(glist[idx])
        except Exception:
            pass
        return GENDERS[idx]

    def handle(self, events):
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    if self.step > 0:
                        self.step -= 1
                    else:
                        from gameplay.scene_mainmenu import SceneMainMenu
                        self.mgr.switch_to(SceneMainMenu(self.mgr))
                    return
                if self.step in (0, 1, 2, 3):
                    signs = self._signs()
                    signs_len = len(signs) if signs else 1
                    if e.key in (pygame.K_LEFT, pygame.K_a):
                        if self.step == 0:
                            self.sel_gender = (self.sel_gender - 1) % len(GENDERS)
                        elif self.step == 1:
                            if self.races:
                                self.sel_race = (self.sel_race - 1) % len(self.races)
                        elif self.step == 2:
                            if self.classes:
                                self.sel_class = (self.sel_class - 1) % len(self.classes)
                        else:
                            self.sel_sign = (self.sel_sign - 1) % signs_len
                    elif e.key in (pygame.K_RIGHT, pygame.K_d):
                        if self.step == 0:
                            self.sel_gender = (self.sel_gender + 1) % len(GENDERS)
                        elif self.step == 1:
                            if self.races:
                                self.sel_race = (self.sel_race + 1) % len(self.races)
                        elif self.step == 2:
                            if self.classes:
                                self.sel_class = (self.sel_class + 1) % len(self.classes)
                        else:
                            self.sel_sign = (self.sel_sign + 1) % signs_len
                    elif e.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.step = min(self.step + 1, 6)
                elif self.step == 4:
                    skills = self._skills_localized()
                    if not skills:
                        self.step += 1
                        return
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
                elif self.step == 5:
                    if e.key == pygame.K_RETURN and self.name.strip():
                        self.step = 6
                    elif e.key == pygame.K_BACKSPACE:
                        self.name = self.name[:-1]
                    else:
                        ch = getattr(e, 'unicode', '')
                        if ch and (ch.isalnum() or ch in ' _-') and len(self.name) < 16:
                            self.name += ch
                elif self.step == 6:
                    if e.key in (pygame.K_RETURN, pygame.K_SPACE):
                        profile = self._make_profile()
                        self.on_complete(profile)

    def _signs(self):
        try:
            return list(t('signs.list', self.lang))
        except Exception:
            return []

    def _skills_localized(self):
        try:
            return list(t('skills.list', self.lang))
        except Exception:
            return []

    def _current_choices(self):
        race = self.races[self.sel_race] if self.races else ''
        clazz_raw = self.classes[self.sel_class] if self.classes else ''
        clazz = canon_class(clazz_raw) if clazz_raw else ''
        signs_loc = self._signs()
        sign_loc = signs_loc[self.sel_sign % len(signs_loc)] if signs_loc else ''
        try:
            en_signs = list(t('signs.list', 'en-US'))
        except Exception:
            en_signs = []
        sign_canon = en_signs[self.sel_sign % len(en_signs)] if en_signs else ''
        skills_loc = self._skills_localized()
        chosen_canon = []
        if skills_loc:
            try:
                en_skills = list(t('skills.list', 'en-US'))
            except Exception:
                en_skills = []
            for s in self.chosen_skills:
                try:
                    idx = skills_loc.index(s)
                    chosen_canon.append(en_skills[idx])
                except Exception:
                    chosen_canon.append(s)
        return race, clazz, sign_loc, sign_canon, chosen_canon

    def _calc_step_stats(self, step: int):
        race, clazz, _, sign_canon, chosen_canon = self._current_choices()
        stats = {k: 0 for k in ('STR', 'DEX', 'INT', 'VIT', 'END', 'WIS')}
        derived = {'HP': 0, 'MP': 0, 'STA': 0}
        bonuses = {'race': {}, 'class': {}, 'sign': {}, 'skills': {}}
        if step >= 1 and race:
            base = build_stats(race, '')
            for k in stats:
                stats[k] = getattr(base, k, 0)
            bonuses['race'] = RACES.get(race, {}).get('bonus', {})
        if step >= 2 and clazz:
            base_class = build_stats('', clazz)
            for k in stats:
                stats[k] += getattr(base_class, k, 0)
            bonuses['class'] = CLASSES.get(clazz, {}).get('base', {})
        if step >= 3 and sign_canon:
            sb = SIGN_BONUS.get(sign_canon, {})
            for k in stats:
                stats[k] += int(sb.get(k, 0))
            bonuses['sign'] = sb
        if step >= 4:
            for sc in chosen_canon:
                b = SKILL_BONUS.get(sc, {})
                for k, inc in b.items():
                    stats[k] += int(inc)
                bonuses['skills'][sc] = b
        if step >= 1:
            mp_pct = float(bonuses['sign'].get('MP%', 0.0))
            sta_pct = float(bonuses['sign'].get('STA%', 0.0))
            derived['HP'] = 30 + stats['VIT'] * 8
            derived['MP'] = int((10 + stats['INT'] * 8 + stats['WIS'] * 4) * (1.0 + mp_pct))
            derived['STA'] = int((20 + stats['END'] * 6) * (1.0 + sta_pct))
        return stats, derived, bonuses

    def _make_profile(self):
        race, clazz, sign_loc, _sign_canon, _chosen_canon = self._current_choices()
        stats, derived, _sb, _chosen = self._calc_preview_stats()
        final = dict(stats)
        final.update(derived)
        default_name = self._L('char.default_name', 'Aventureiro', 'Adventurer')
        return {
            'name': self.name.strip() or default_name,
            'gender': self._gender_display(self.sel_gender),
            'race': race,
            'clazz': clazz,
            'sign': sign_loc,
            'skills': list(self.chosen_skills),
            'stats': final,
        }

    def _get_portrait(self, race: str, gender: str, clazz: str, max_size: Tuple[int, int]) -> pygame.Surface:
        rslug = self._RACE_SLUGS.get(race, race).lower()
        gslug = self._GENDER_SLUGS.get(gender, gender).lower()
        cslug = (clazz or '').lower()
        key_class = f"{rslug}_{gslug}_{cslug}"
        key_generic = f"{rslug}_{gslug}"
        if key_class in self._portrait_cache:
            return self._portrait_cache[key_class]
        if key_generic in self._portrait_cache:
            return self._portrait_cache[key_generic]
        rel_class = f"{self._PORTRAITS_DIR}/{rslug}_{gslug}_{cslug}.png"
        surf = load_image_strict(rel_class)
        if surf is None:
            rel = f"{self._PORTRAITS_DIR}/{rslug}_{gslug}.png"
            surf = load_image_strict(rel)
        cache_key = key_class if surf is not None and cslug else key_generic
        if surf is None:
            w, h = max_size
            ph = pygame.Surface((w, h), pygame.SRCALPHA)
            ph.fill((255, 0, 255, 70))
            self._portrait_cache[cache_key] = ph
            return ph
        iw, ih = surf.get_size()
        scale = min(max_size[0] / max(1, iw), max_size[1] / max(1, ih), 1.0)
        if scale < 1.0:
            surf = pygame.transform.smoothscale(surf, (int(iw * scale), int(ih * scale)))
        self._portrait_cache[cache_key] = surf
        return surf

    def _draw_stats_block(self, screen: pygame.Surface, x: int, y: int, stats: dict, derived: dict, sb: dict, chosen_canon: list):
        title = self._L('char.labels.attributes', 'Atributos', 'Attributes')
        title2 = self._L('char.labels.derived', 'Derivados', 'Derived')
        sign_bonus_label = self._L('char.labels.sign_bonuses', 'Bônus do Signo:', 'Sign Bonuses:')
        skills_bonus_label = self._L('char.labels.skill_bonuses', 'Bônus de Perícias:', 'Skill Bonuses:')
        screen.blit(self.small.render(title, True, (220, 220, 240)), (x, y)); y += 26
        col_left = x
        col_mid = x + 120

        def line(lbl_key, val, ypos):
            nm = self._attr_label(lbl_key)
            screen.blit(self.small.render(f"{nm}:", True, (200, 200, 210)), (col_left, ypos))
            screen.blit(self.small.render(str(val), True, (240, 220, 160)), (col_mid, ypos))

        for k in ('STR', 'DEX', 'INT', 'WIS', 'VIT', 'END'):
            line(k, stats.get(k, 0), y); y += 22
        y += 6
        screen.blit(self.small.render(title2, True, (220, 220, 240)), (x, y)); y += 26
        for k in ('HP', 'MP', 'STA'):
            line(k, derived.get(k, 0), y); y += 22
        y += 6
        if sb:
            screen.blit(self.small.render(sign_bonus_label, True, (210, 230, 210)), (x, y)); y += 22
            for key in ('STR', 'DEX', 'INT', 'VIT', 'END', 'WIS', 'MP%', 'STA%', 'DMG%', 'STEALTH%'):
                v = sb.get(key, 0)
                if v:
                    name = self._attr_label(key)
                    vv = f"+{int(v)}" if isinstance(v, int) else f"+{int(v * 100)}%"
                    screen.blit(self.small.render(f"{name}: {vv}", True, (200, 220, 200)), (x + 12, y)); y += 20
        if chosen_canon:
            screen.blit(self.small.render(skills_bonus_label, True, (210, 230, 210)), (x, y)); y += 22
            for sc in chosen_canon:
                b = SKILL_BONUS.get(sc, {})
                for kk, inc in b.items():
                    name = self._attr_label(kk)
                    screen.blit(self.small.render(f"{sc}: +{inc} {name}", True, (200, 220, 200)), (x + 12, y)); y += 20
        return y

    def draw(self, screen: pygame.Surface):
        if self.bg:
            blit_fit(screen, self.bg)
        else:
            screen.fill((10, 12, 18))
        w, h = screen.get_size()
        panel_x, panel_y = int(w * 0.10), int(h * 0.15)
        panel_w, panel_h = int(w * 0.80), int(h * 0.70)
        panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 120))
        screen.blit(panel, (panel_x, panel_y))
        # Título da etapa
        try:
            titles = t('char.titles', self.lang)
            head_txt = titles[self.step]
        except Exception:
            head_txt = self._L('char.title', 'Criar Personagem', 'Create Character')
        head = self.font.render(head_txt, True, (230, 230, 230))
        screen.blit(head, head.get_rect(center=(w // 2, int(h * 0.22))))

        # Estatísticas da etapa corrente
        stats, derived, bonuses = self._calc_step_stats(self.step)
        sb = bonuses.get('sign', {})
        chosen_canon = list(bonuses.get('skills', {}).keys())
        stats_x = panel_x + 24
        stats_y = panel_y + int(panel_h * 0.46)  # ligeiramente mais alto para mais respiro
        stats_w = int(panel_w * 0.36)
        stats_h = panel_h - (stats_y - panel_y) - 24
        stats_surf = pygame.Surface((stats_w, stats_h), pygame.SRCALPHA)
        stats_surf.fill((0, 0, 0, 0))

        def _draw_stats_to_surface():
            stats_surf.fill((0, 0, 0, 0))
            self._draw_stats_block(stats_surf, 0, 0, stats, derived, sb, chosen_canon)

        # STEP 0: Gênero
        if self.step == 0:
            opt = self.font.render(self._gender_display(self.sel_gender), True, (240, 220, 160))
            screen.blit(opt, opt.get_rect(center=(w // 2, int(h * 0.45))))
            return

        # STEP 1: Raça
        if self.step == 1:
            race = self.races[self.sel_race] if self.races else ''
            gender = self._gender_display(self.sel_gender)
            try:
                race_label = t(f'race.{race}.name', self.lang)
            except Exception:
                race_label = race
            try:
                desc = t(f'race.{race}.desc', self.lang)
            except Exception:
                desc = ''
            screen.blit(self.font.render(race_label, True, (240, 220, 160)), (panel_x + 24, panel_y + 24))
            desc_end_y = panel_y + 70
            if desc:
                desc_end_y = _draw_paragraph(
                    screen, desc, self.small, (210, 210, 210),
                    pygame.Rect(panel_x + 24, panel_y + 70, int(panel_w * 0.46), 120), 24
                )
            race_bonus = RACES.get(race, {}).get('bonus', {})
            y_bonus = (desc_end_y + 12) if desc else (panel_y + 160)
            for ln in _fmt_bonus_lines(race_bonus, self._attr_label):
                screen.blit(self.small.render("• " + ln, True, (220, 220, 240)), (panel_x + 24, y_bonus)); y_bonus += 22
            clazz = canon_class(self.classes[self.sel_class]) if self.classes else ''
            max_w = int(panel_w * 0.32)
            max_h = int(panel_h * 0.62)
            portrait = self._get_portrait(race, gender, clazz, (max_w, max_h))
            dst = portrait.get_rect()
            dst.right = panel_x + panel_w - self._portrait_margin
            dst.centery = panel_y + int(panel_h * 0.55)
            screen.blit(portrait, dst)
            _draw_stats_to_surface()
            screen.blit(stats_surf, (stats_x, stats_y))
            return

        # STEP 2: Classe
        if self.step == 2:
            clazz = canon_class(self.classes[self.sel_class]) if self.classes else ''
            try:
                label = t(f'class.{clazz}.name', self.lang)
                desc = t(f'class.{clazz}.desc', self.lang)
            except Exception:
                label, desc = clazz, ''
            screen.blit(self.font.render(label, True, (240, 220, 160)), (panel_x + 24, panel_y + 24))
            y_after_desc = panel_y + 70
            if desc:
                y_after_desc = _draw_paragraph(
                    screen, desc, self.small, (210, 210, 210),
                    pygame.Rect(panel_x + 24, panel_y + 70, int(panel_w * 0.70), 100), 24
                )
            # UX: manter o bloco de bônus de classe logo abaixo da descrição (dinâmico)
            y_cls = y_after_desc + 12
            class_bonus_label = self._L('char.labels.class_bonuses', 'Bônus de Classe:', 'Class Bonuses:')
            screen.blit(self.small.render(class_bonus_label, True, (200, 220, 255)), (panel_x + 24, y_cls)); y_cls += 26
            base_bonus = CLASSES.get(clazz, {}).get('base', {}) if clazz else {}
            for ln in _fmt_bonus_lines(base_bonus, self._attr_label):
                screen.blit(self.small.render("• " + ln, True, (220, 220, 240)), (panel_x + 24, y_cls)); y_cls += 22
            _draw_stats_to_surface()
            screen.blit(stats_surf, (stats_x, stats_y))
            return

        # STEP 3: Signo
        if self.step == 3:
            signs_loc = self._signs()
            if signs_loc:
                sign = signs_loc[self.sel_sign % len(signs_loc)]
                screen.blit(self.font.render(sign, True, (240, 220, 160)), (panel_x + 24, panel_y + 24))
            _draw_stats_to_surface()
            screen.blit(stats_surf, (stats_x, stats_y))
            return

        # STEP 4: Perícias
        if self.step == 4:
            skills = self._skills_localized()
            if skills:
                y = panel_y + 24
                tip = t('char.hint.skills', self.lang)
                surf = self.small.render(tip, True, (210, 210, 210))
                screen.blit(surf, (panel_x + 24, y)); y += 28
                list_text = ' '.join(['[' + s + ']' if s in self.chosen_skills else s for s in skills])
                surf2 = self.small.render(list_text, True, (230, 230, 230))
                screen.blit(surf2, (panel_x + 24, y))
            _draw_stats_to_surface()
            screen.blit(stats_surf, (stats_x, stats_y))
            return

        # STEP 5: Nome
        if self.step == 5:
            box = pygame.Rect(0, 0, max(360, w // 3), 52); box.center = (w // 2, int(h * 0.48))
            pygame.draw.rect(screen, (24, 24, 32), box, border_radius=6)
            pygame.draw.rect(screen, (90, 90, 120), box, 2, border_radius=6)
            txt = self.font.render(self.name or '', True, (240, 220, 160))
            screen.blit(txt, txt.get_rect(midleft=(box.left + 12, box.centery)))
            _draw_stats_to_surface()
            screen.blit(stats_surf, (stats_x, stats_y))
            return

        # STEP 6: Resumo
        if self.step == 6:
            race, clazz, sign_loc, _, _ = self._current_choices()
            y = panel_y + 24
            label_name = self._L('char.summary.name', 'Nome', 'Name')
            label_gender = self._L('char.summary.gender', 'Gênero', 'Gender')
            label_race = self._L('char.summary.race', 'Raça', 'Race')
            label_class = self._L('char.summary.class', 'Classe', 'Class')
            label_sign = self._L('char.summary.sign', 'Signo', 'Sign')
            label_skills = self._L('char.summary.skills', 'Perícias', 'Skills')

            screen.blit(self.small.render(f"{label_name}: {self.name or self._L('char.default_name','Aventureiro','Adventurer')}", True, (230, 230, 230)), (panel_x + 24, y)); y += 24
            screen.blit(self.small.render(f"{label_gender}: {self._gender_display(self.sel_gender)}", True, (230, 230, 230)), (panel_x + 24, y)); y += 24
            screen.blit(self.small.render(f"{label_race}: {race}", True, (230, 230, 230)), (panel_x + 24, y)); y += 24
            screen.blit(self.small.render(f"{label_class}: {clazz}", True, (230, 230, 230)), (panel_x + 24, y)); y += 24
            if sign_loc:
                screen.blit(self.small.render(f"{label_sign}: {sign_loc}", True, (230, 230, 230)), (panel_x + 24, y)); y += 24
            if self.chosen_skills:
                screen.blit(self.small.render(f"{label_skills}: {', '.join(self.chosen_skills)}", True, (230, 230, 230)), (panel_x + 24, y)); y += 24
            y += 10

            # Descrição da Raça
            try:
                race_desc = t(f'race.{race}.desc', self.lang)
            except Exception:
                race_desc = RACES.get(race, {}).get('desc', '')
            if race_desc:
                race_desc_label = self._L('char.summary.headers.race_desc', 'Descrição da Raça:', 'Race Description:')
                screen.blit(self.small.render(race_desc_label, True, (200, 220, 255)), (panel_x + 24, y)); y += 24
                y = _draw_paragraph(
                    screen, race_desc, self.small, (210, 210, 210),
                    pygame.Rect(panel_x + 24, y, int(panel_w * 0.70), 72), 22
                ) + 6

            # Bônus de Raça
            race_bonus = RACES.get(race, {}).get('bonus', {})
            for ln in _fmt_bonus_lines(race_bonus, self._attr_label):
                screen.blit(self.small.render("• " + ln, True, (220, 220, 240)), (panel_x + 24, y)); y += 22
            y += 6

            # Descrição da Classe
            try:
                class_desc = t(f'class.{clazz}.desc', self.lang)
            except Exception:
                class_desc = CLASSES.get(clazz, {}).get('desc', '')
            if class_desc:
                class_desc_label = self._L('char.summary.headers.class_desc', 'Descrição da Classe:', 'Class Description:')
                screen.blit(self.small.render(class_desc_label, True, (200, 220, 255)), (panel_x + 24, y)); y += 24
                y = _draw_paragraph(
                    screen, class_desc, self.small, (210, 210, 210),
                    pygame.Rect(panel_x + 24, y, int(panel_w * 0.70), 72), 22
                ) + 6

            # Bônus de Classe
            base_bonus = CLASSES.get(clazz, {}).get('base', {})
            if base_bonus:
                class_bonus_label = self._L('char.labels.class_bonuses', 'Bônus de Classe:', 'Class Bonuses:')
                screen.blit(self.small.render(class_bonus_label, True, (200, 220, 255)), (panel_x + 24, y)); y += 24
                for ln in _fmt_bonus_lines(base_bonus, self._attr_label):
                    screen.blit(self.small.render("• " + ln, True, (220, 220, 240)), (panel_x + 24, y))
                    y += 22

            _draw_stats_to_surface()
            screen.blit(stats_surf, (stats_x, stats_y))
            return

    def _calc_preview_stats(self):
        stats, derived, bonuses = self._calc_step_stats(6)
        sb = bonuses.get('sign', {})
        chosen = list(bonuses.get('skills', {}).keys())
        return stats, derived, sb, chosen
