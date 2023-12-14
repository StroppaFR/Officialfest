import xml.etree.ElementTree as ET

class Item:
    def __init__(self, item_id, rarity):
        self.item_id = item_id
        self.rarity = rarity
        self.name = 'UNKNOWN ITEM'

class Quest:
    def __init__(self, quest_id):
        self.quest_id = quest_id
        self.requires = []
        self.name = 'UNKNOWN QUEST'
        self.description = 'UNKNOWN QUEST DESCRIPTION'

class Family:
    def __init__(self, family_id):
        self.family_id = family_id
        self.items = []
        self.name = 'UNKNOWN FAMILY'

ALL_ITEMS = {}
ALL_FAMILIES = {}
ALL_QUESTS = {}

def load_data(app, lang):
    # Load all quests and items
    # Items (first special items then score items)
    for xml in ['xml/specialItems.xml', 'xml/scoreItems.xml']:
        with app.open_resource(xml, 'r') as items_f:
            items_tree = ET.parse(items_f).getroot()
            assert items_tree.tag == 'items'
            # Parse all <family> elements
            for family_elem in items_tree:
                new_family = Family(int(family_elem.get('id')))
                # Parse all <item> elements of a <family>
                for child in family_elem:
                    if child.tag != 'item':
                        continue
                    new_item = Item(int(child.get('id')), int(child.get('rarity')))
                    new_family.items.append(new_item)
                    ALL_ITEMS[new_item.item_id] = new_item
                ALL_FAMILIES[new_family.family_id] = new_family
    # Quests
    with app.open_resource('xml/quests.xml', 'r') as quests_f:
        quests_tree = ET.parse(quests_f).getroot()
        assert quests_tree.tag == 'quests'
        # Parse all <quest> elements
        for quest_elem in quests_tree:
            new_quest = Quest(int(quest_elem.get('id')))
            # Parse all <require> elements of a <quest>
            for child in quest_elem:
                if child.tag != 'require':
                    continue
                require = (int(child.get('item')), int(child.get('qty')))
                new_quest.requires.append(require)
            ALL_QUESTS[new_quest.quest_id] = new_quest
    # Translations (lang dependant)
    with app.open_resource(f'xml/lang/{lang}.xml', 'r') as lang_f:
        lang_tree = ET.parse(lang_f).getroot()
        assert lang_tree.tag == 'lang'
        items = lang_tree.find('items')
        families = lang_tree.find('families')
        quests = lang_tree.find('quests')
        assert items is not None and families is not None and quests is not None
        for item in items:
            ALL_ITEMS[int(item.get('id'))].name = item.get('name')
        for family in families:
            ALL_FAMILIES[int(family.get('id'))].name = family.get('name')
        for quest in quests:
            ALL_QUESTS[int(quest.get('id'))].name = quest.get('title')
            ALL_QUESTS[int(quest.get('id'))].description = quest.text
