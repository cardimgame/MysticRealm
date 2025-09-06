
class StateManager:
    def __init__(self):
        self.current_scene = None
        self.running = True
    def switch_to(self, new_scene):
        if self.current_scene and hasattr(self.current_scene, 'exit'):
            try: self.current_scene.exit()
            except Exception: pass
        self.current_scene = new_scene
        if hasattr(self.current_scene, 'enter'):
            try: self.current_scene.enter()
            except Exception: pass
