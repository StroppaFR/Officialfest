from flask import Blueprint, redirect, render_template
from itertools import chain
from officialfest.db import get_db

bp = Blueprint('user', __name__, url_prefix='/user.html')

ITEMS_PER_FAMILY = {
    0: [0, 3, 4, 7, 13, 21, 24, 64, 74, 77, 84, 102, 113, 115, 116, 117],
    1: [1, 5, 8, 11, 18, 22, 23, 25, 27, 28, 38, 39, 65, 66, 69, 71, 82, 106, 107],
    2: [2, 6, 9, 12, 19, 30, 31, 36, 70, 72, 73, 75, 76, 80, 81, 86, 87, 88, 89, 90, 93, 95, 96, 99, 101, 112],
    3: [14, 15, 16, 17],
    4: [32, 33, 34, 35],
    5: [40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51],
    6: [52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63],
    7: [103],
    8: [104],
    9: [105],
    10: [20, 78, 79, 91, 94],
    11: [83, 97, 98, 100, 108],
    12: [29, 37, 67, 85, 92],
    13: [68],
    14: [26],  
    15: [109],  
    16: [110],
    17: [111],
    18: [10],
    19: [114],
    1000: [1000, 1003, 1008, 1013, 1017, 1027, 1041, 1043, 1047, 1048, 1049, 1050, 1051, 1169, 1185],
    1001: [1022, 1024, 1025, 1026, 1028, 1040, 1069, 1070, 1071, 1073, 1074, 1075, 1077, 1078, 1079, 1080, 1081, 1082],
    1002: [1002, 1004, 1005, 1006, 1007, 1012, 1014, 1015, 1016, 1018, 1019, 1023, 1045, 1046],
    1003: [1009, 1010, 1011],
    1004: [1001, 1021, 1042, 1055, 1056, 1057, 1142, 1149, 1166],
    1005: [1020, 1039, 1044, 1060, 1061, 1062, 1076, 1161, 1162, 1163, 1167],
    1006: [1029, 1030, 1031, 1032, 1033, 1034, 1035, 1036, 1037, 1038, 1164],
    1007: [1052, 1053, 1054],
    1008: [1091, 1092, 1093, 1094, 1095, 1096, 1097, 1098, 1099],
    1009: [1063, 1064, 1065, 1066, 1067, 1068],
    1010: [1083, 1084, 1085, 1086, 1087, 1088, 1089, 1090],
    1011: [1106, 1107, 1108, 1109, 1110, 1111],
    1012: [1100, 1101, 1102, 1103, 1104, 1105, 1168],
    1013: [1112, 1113, 1114, 1115, 1116, 1117, 1118, 1119, 1120, 1121, 1122, 1123, 1124, 1125, 1126, 1127, 1128, 1129, 1130, 1131, 1132, 1133, 1134, 1135, 1136],
    1014: [1141, 1143],
    1015: [1137, 1138, 1139, 1140],
    1016: [1144, 1145, 1146, 1147, 1148, 1150, 1151, 1152, 1153, 1154, 1155, 1159, 1160],
    1017: [1058, 1059, 1072, 1156, 1157, 1158, 1165],
    1018: [1170, 1171, 1172, 1173, 1174, 1175, 1176, 1177],
    1019: [1178, 1179, 1180, 1181, 1182, 1183, 1184],
    1020: [1190, 1191, 1194, 1197, 1198, 1199, 1200],
    1021: [1193],
    1022: [1196],
    1023: [1192, 1195],
    1024: [1201, 1202, 1203, 1204, 1205, 1206, 1207, 1208],
    1025: [1209, 1210, 1211, 1212, 1213],
    1026: [1214, 1215, 1216, 1217, 1218],
    1027: [1219, 1220, 1225, 1226, 1227, 1237, 1238],
    1028: [1221, 1222, 1223, 1224],
    1029: [1228, 1236],
    1030: [1229, 1230, 1231, 1232, 1233, 1234, 1235]
}

SORTED_PROFILE_ITEMS = list(chain(*[ITEMS_PER_FAMILY[key] for key in sorted(ITEMS_PER_FAMILY.keys())]))

# TODO: centralize this somewhere
# TODO: translations
QUEST_NAMES = [
    'Les constellations',
    'Mixtures du zodiaque',
    'Premiers pas',
    'L\'aventure commence',
    'Une destinée épique',
    'Persévérance',
    'Gourmandise',
    'Du sucre !',
    'Malnutrition',
    'Goût raffiné',
    'Avancée technologique',
    'Le petit guide des Champignons',
    'Trouver les pièces d\'or secrètes !',
    'Le grimoire des Etoiles',
    'Armageddon',
    'Régime MotionTwin',
    'Créateur de jeu en devenir',
    'La vie est une boîte de chocolats',
    'Le trésor Oune-difaïned',
    'Super size me !',
    'Maître joaillier',
    'Grand prédateur',
    'Expert en salades et potages',
    'Festin d\'Hammerfest',
    'Goûter d\'anniversaire',
    'Bon vivant',
    'Fondue norvégienne',
    'Mystère de Guu',
    'Friandises divines',
    'Igor et Cortex',
    'Affronter l\'obscurité',
    'Et la lumière fût !',
    'Noël sur Hammerfest !',
    'Joyeux anniversaire Igor',
    'Cadeau céleste',
    'Achat de parties amélioré',
    'Exterminateur de Sorbex',
    'Désamorceur de Bombinos',
    'Tueur de poires',
    'Mixeur de Tagadas',
    'Kiwi frotte s\'y pique',
    'Chasseur de Bondissantes',
    'Tronçonneur d\'Ananargeddons',
    'Roi de Hammerfest',
    'Chapelier fou',
    'Poney éco-terroriste',
    'Le Pioupiouz est en toi',
    'Chasseur de champignons',
    'Successeur de Tuberculoz',
    'La première clé !',
    'Rigor Dangerous',
    'La Méluzzine perdue',
    'Enfin le Bourru !',
    'Congélation',
    'Une clé rouillée',
    'Laissez passer !',
    'Les mondes ardus',
    'Viiiite !',
    'Faire les poches à Tubz',
    'Tuberculoz, seigneur des enfers',
    'L\'eau ferrigineuneuse',
    'Paperasse administrative',
    'Meilleur joueur',
    'Miroir, mon beau miroir',
    'Mode cauchemar',
    'L\'aventure continue !',
    'Joyau d\'Ankhel',
    'Sandy commence l\'aventure !',
    'Miroir, NOTRE beau miroir',
    'Mode double cauchemar',
    'Une grande Amitié',
    'Apprentissage des canifs volants',
    'Shinobi do !',
    'Rapide comme l\'éclair !',
    'Maître des Bombes',
    'Tombeau de Tuberculoz'
]

@bp.app_context_processor
def inject_profile_items():
    return dict(SORTED_PROFILE_ITEMS=SORTED_PROFILE_ITEMS)

@bp.route('/', methods=['GET'])
def get_user_account():
    return render_template('user/user-account.html')

@bp.route('/godChildren', methods=['GET'])
def get_godChildren():
    return render_template('user/godChildren.html')

@bp.route('/changeEmail', methods=['POST'])
@bp.route('/changeEmailPublic', methods=['POST'])
@bp.route('/passwd', methods=['POST'])
@bp.route('/raz', methods=['POST'])
@bp.route('/unsubscribe', methods=['POST'])
def post_update_user():
    return redirect('/user.html')

@bp.route('/<int:user_id>', methods=['GET'])
def show_profile(user_id):
    db = get_db()
    # Fetch user information
    user = db.execute('SELECT users.*, hof_messages.message as "hof_message", hof_messages.written_at as "hof_message_date", user_weekly_scores.weekly_score \
                       FROM users LEFT OUTER JOIN hof_messages ON user_id = author LEFT OUTER JOIN user_weekly_scores USING (user_id) \
                       WHERE user_id = ?', (user_id,)).fetchone()
    if user is None:
        # TODO: translations
        return render_template('evni.html', error='404 : Utilisateur introuvable'), 404
    # Fetch user quests
    user_quests = db.execute('SELECT quest_id, completed \
                              FROM user_quests INNER JOIN users USING (user_id) \
                              WHERE user_id = ?', (user_id,)).fetchall()
    completed_quests = []
    current_quests = []
    for user_quest in user_quests:
        quest_id = user_quest['quest_id']
        # TODO: translations
        quest_name = QUEST_NAMES[quest_id] if quest_id < len(QUEST_NAMES) else 'Quête inconnue'
        if user_quest['completed']:
            completed_quests.append(quest_name)
        else:
            current_quests.append(quest_name)
    # Fetch user unlocked items
    user_unlocked_items = db.execute('SELECT item_id \
                              FROM user_unlocked_items INNER JOIN users USING (user_id) \
                              WHERE user_id = ?', (user_id,)).fetchall()
    user_items = set(item['item_id'] for item in user_unlocked_items)
    # Render the profile page
    return render_template('user/user.html', user=user, user_items=user_items,
                           completed_quests=completed_quests, current_quests=current_quests)
