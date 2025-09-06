import pygame
from gameplay.scene_game import SceneGame

GENDERS=['Masculino','Feminino']
RACES=[
    ('Valdyr','Nativos das Montanhas Cinzentas; vigorosos e resilientes.'),
    ('Eldran','Antigos eruditos dos Bosques Pálidos; afinidade arcana.'),
    ('Karuun','Povos das Planícies de Bronze; força e disciplina.'),
    ('Sildor','Caçadores do Vale Verde; rápidos e precisos.'),
    ('Aeliri','Errantes das Brumas Azuis; mente ágil e curiosa.'),
    ('Morvak','Clãs da Pedra Profunda; pele espessa e vigor.'),
    ('Tirren','Mercadores do Deserto Dourado; adaptáveis e astutos.'),
    ('Orruk','Tribo do Ferro Negro; potência bruta, pouca sutileza.'),
    ('Shaqat','Nômades de Jade; passos silenciosos e olhos atentos.'),
    ('Nereen','Filhos da Névoa; intuição e talento místico.'),
]
CLASSES=[
    ('Guerreiro','Combate corpo a corpo, alta resistência, controle de espaço.'),
    ('Arcanista','Magias ofensivas e utilitárias; frágil no início.'),
    ('Viajante','Versátil, mobilidade e exploração; equilíbrio geral.'),
    ('Arqueiro','Ataques à distância, alta precisão e kiting.'),
    ('Sombra','Furtividade, golpes críticos e evasão.'),
    ('Trovador','Suporte e buffs; controle leve de campo.'),
    ('Guardião','Tanque; proteção, bloqueio e presença.'),
]

class CharacterCreation:
    def __init__(self, mgr):
        self.mgr=mgr
        self.font=pygame.font.SysFont('serif',42)
        self.small=pygame.font.SysFont('serif',24)
        self.step=0
        self.name=''
        self.gen=0
        self.race=0
        self.clazz=0
    def handle(self, events):
        for e in events:
            if e.type==pygame.KEYDOWN:
                if self.step==0:
                    if e.key==pygame.K_RETURN and self.name.strip(): self.step=1
                    elif e.key==pygame.K_BACKSPACE: self.name=self.name[:-1]
                    else:
                        ch=e.unicode
                        if ch and (ch.isalnum() or ch in ' _-') and len(self.name)<16: self.name+=ch
                elif self.step==1:
                    if e.key in (pygame.K_LEFT,pygame.K_a): self.gen=(self.gen-1)%len(GENDERS)
                    elif e.key in (pygame.K_RIGHT,pygame.K_d): self.gen=(self.gen+1)%len(GENDERS)
                    elif e.key in (pygame.K_RETURN,pygame.K_SPACE): self.step=2
                    elif e.key==pygame.K_ESCAPE: self.step=0
                elif self.step==2:
                    if e.key in (pygame.K_LEFT,pygame.K_a): self.race=(self.race-1)%len(RACES)
                    elif e.key in (pygame.K_RIGHT,pygame.K_d): self.race=(self.race+1)%len(RACES)
                    elif e.key in (pygame.K_RETURN,pygame.K_SPACE): self.step=3
                    elif e.key==pygame.K_ESCAPE: self.step=1
                elif self.step==3:
                    if e.key in (pygame.K_LEFT,pygame.K_a): self.clazz=(self.clazz-1)%len(CLASSES)
                    elif e.key in (pygame.K_RIGHT,pygame.K_d): self.clazz=(self.clazz+1)%len(CLASSES)
                    elif e.key in (pygame.K_RETURN,pygame.K_SPACE):
                        profile={'name':self.name.strip(),'gender':GENDERS[self.gen],'race':RACES[self.race][0],'clazz':CLASSES[self.clazz][0]}
                        self.mgr.scene = SceneGame(self.mgr, profile)
                    elif e.key==pygame.K_ESCAPE: self.step=2
    def update(self, dt): pass
    def draw(self, screen):
        screen.fill((12,12,18))
        w,h=screen.get_size()
        if self.step==0:
            head=self.font.render('Nome do personagem', True, (236,200,120)); screen.blit(head, head.get_rect(center=(w//2,int(h*0.2))))
            box=pygame.Rect(0,0, max(400,w//3), 50); box.center=(w//2,h//2)
            pygame.draw.rect(screen,(24,24,32),box,border_radius=6); pygame.draw.rect(screen,(90,90,120),box,2,border_radius=6)
            txt=self.font.render(self.name,True,(240,220,160)); screen.blit(txt, txt.get_rect(midleft=(box.left+12, box.centery)))
        elif self.step==1:
            head=self.font.render('Gênero',True,(236,200,120)); screen.blit(head, head.get_rect(center=(w//2,int(h*0.2))))
            opt=self.font.render(GENDERS[self.gen],True,(240,220,160)); screen.blit(opt,opt.get_rect(center=(w//2,h//2)))
        elif self.step==2:
            head=self.font.render('Raça',True,(236,200,120)); screen.blit(head, head.get_rect(center=(w//2,int(h*0.18))))
            nm,desc=RACES[self.race]
            opt=self.font.render(nm,True,(240,220,160)); screen.blit(opt,opt.get_rect(center=(w//2,int(h*0.42))))
            wrap = self.small.render(desc, True, (210,210,210))
            screen.blit(wrap, wrap.get_rect(center=(w//2,int(h*0.55))))
        elif self.step==3:
            head=self.font.render('Classe',True,(236,200,120)); screen.blit(head, head.get_rect(center=(w//2,int(h*0.18))))
            nm,desc=CLASSES[self.clazz]
            opt=self.font.render(nm,True,(240,220,160)); screen.blit(opt,opt.get_rect(center=(w//2,int(h*0.42))))
            wrap = self.small.render(desc, True, (210,210,210))
            screen.blit(wrap, wrap.get_rect(center=(w//2,int(h*0.55))))
