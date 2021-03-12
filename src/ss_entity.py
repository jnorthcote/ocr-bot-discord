import re

from ss_types import SystemType

def entity_factory(classname):
     # cls = getattr('ss_entity', classname)
     cls = globals()[classname]
     return cls

class Player():
    def __init__(self, player):
        self.fields = {}
        if player[0] == 'LEADER':
            self.leader = True
            # self.fields['power'] = power[2]
            player.pop(0)
        else:
            self.leader = False
            # self.fields['power'] = power[1]

        self.fields['level'] = player.pop(0)

        next = re.search(r'\[(.*?)\]',player[0])
        if next:
            self.fields['alliance'] = next.group(1)
        else:
            self.fields['alliance'] = None

        self.fields['name']  = ' '.join(player)

    def __repr__(self):
        return "<Player player:%s>" % (self.fields['name'])

    def __str__(self):
        return "player:%s" % (self.fields['name'])

    def as_embed_field(self, embed, name):
        name = self.fields['name']
        value = []
        value.append("level: %s" % (self.fields['level']))
        # value.append("power: %s" % (self.fields['power']))
        embed.add_field(name=name, value='\n'.join(value), inline=True)

class System():
    def __init__(self, system):
        fields = {'name': [], 'when':[]}
        field = 'name'
        for s in system:
            if s == 'BATTLE':
                break
            if s == '-':
                field = 'when'
            fields[field].append(s)
        self.name = ' '.join(fields['name'])
        self.sys_type = SystemType.fromName(self.name)

    def as_embed_field(self, embed, name):
        # value = "System: %s When: %s" % (' '.join(self.fields['name']), ' '.join(self.fields['when']))
        value = "%s\n%s" % (self.name, self.sys_type.label)
        embed.add_field(name=name, value=value, inline=True)
        embed.colour(self.sys_type.color)

class Rewards():
    def __init__(self, rewards):
        self.name = []
        self.cargo_lost = True
        self.color = 0x0cff00
        for r in rewards:
            if r == 'REWARDS':
                self.cargo_lost = False
                self.color = 0xff0000
                continue
            self.name.append(r)
        self.value = ' '.join(self.name)

    def as_embed_field(self, embed, name):
        embed.add_field(name=name, value=self.value, inline=False)
        embed.colour(self.color)

class Status():
    def __init__(self, status):
        self.name = []
        self.victory = False
        self.defeat  = False
        self.diff    = False
        for s in status:
            self.name.append(s)
            if s == 'VICTORY':
                self.victory = True
            elif s == 'DEFEAT':
                self.defeat = True
            else:
                self.diff = True
        self.value = ' '.join(self.name)

    def as_embed_field(self, embed, name):
        embed.add_field(name=name, value=self.value, inline=False)
