    def handle(self, events):
        for e in events:
            if e.type == pygame.KEYDOWN:
                # ESC sempre alterna pausa
                if e.key == pygame.K_ESCAPE:
                    self.paused = not self.paused
                    return
                # Se estiver pausado, navega no menu de pausa
                if self.paused:
                    if e.key in (pygame.K_UP, pygame.K_w):
                        self.pause_sel = (self.pause_sel - 1) % len(self.pause_tabs)
                    elif e.key in (pygame.K_DOWN, pygame.K_s):
                        self.pause_sel = (self.pause_sel + 1) % len(self.pause_tabs)
                    elif e.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self._exec_pause()
