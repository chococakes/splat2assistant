# did i ever tell you i dont know how to name modules? i don't know how to name modules
import logging
import json
import csv
import requests
import os
from PIL import Image
from io import BytesIO
import connect

BASE_IMAGE_URL = "https://app.splatoon2.nintendo.net"
IMAGE_DIRECTORY = 'static/images/splatoon2/'

def summary(results):
    deaths, kills, specials, assists, victories, defeats = [], [], [], [], 0, 0
    for result in results:
        deaths.append(int(result['player_deaths']))
        kills.append(int(result['player_kills']))
        specials.append(int(result['player_specials']))
        assists.append(int(result['player_assists']))
        if result['outcome'] == 'VICTORY': victories += 1
        else: defeats += 1
    death_average = round(sum(deaths)/len(results))
    kill_average = round(sum(kills)/len(results))
    spec_average = round(sum(specials)/len(results))
    assist_average = round(sum(assists)/len(results))
    victory_percent = str(round(victories / len(results) * 100)) + "%"
    defeat_percent = str(round(defeats / len(results) * 100)) + "%"
    formatstr = """
    (stats shown are out of {6} games)
    Average Deaths Per Game: {0}
    Average Splats Per Game: {1}
    Average Specials Per Game: {2}
    Average Assists Per Game: {3}

    In total, you win {4} of games and lose {5} of them.
    """.format(death_average, kill_average, spec_average, assist_average, victory_percent, defeat_percent, str(len(results)))

    summ = dict(d_average=death_average, k_average=kill_average, sp_average=spec_average, as_average=assist_average,
               vic_percent=victory_percent, def_percent=defeat_percent, total_deaths=sum(deaths), total_kills=sum(kills))
    return summ, formatstr

def weapon_summary(results):
    weapons = []
    total_wins = 0
    total_losses = 0

    for result in results:
        if not any(weapon['name'] == result['player_weapon'] for weapon in weapons):
            weapon = {}
            weapon['name'] = result['player_weapon']
            weapon['plays'] = 1
            weapon['wins'] = 0
            weapon['losses'] = 0
            weapon['kills'] = int(result['player_kills'])
            weapon['deaths'] = int(result['player_deaths'])
            victory = True if result['outcome'].lower() == 'victory' else False
            if victory:
                weapon['wins'] += 1
                total_wins += 1
            else:
                weapon['losses'] += 1
                total_losses += 1
            weapons.append(weapon)
        else:
            for weapon in weapons:
                if weapon['name'] == result['player_weapon']:
                    weapon['kills'] += int(result['player_kills'])
                    weapon['deaths'] += int(result['player_deaths'])
                    victory = True if result['outcome'].lower() == 'victory' else False
                    if victory:
                        weapon['wins'] += 1
                        total_wins += 1
                    else:
                        weapon['losses'] += 1
                        total_losses += 1
                    weapon['plays'] += 1

    for weapon in weapons:
        weapon['win_percent'] = str(round(weapon['wins'] / total_wins * 100, 2)) + "%"
        weapon['loss_percent'] = str(round(weapon['losses'] / total_losses * 100, 2)) + "%"
        weapon['ratio'] = str(round(weapon['wins'] / weapon['plays'] * 100, 2)) + "%"
    return sorted(weapons, key=lambda item: item['name'])

def get_image(url):
    """Returns the file location of an image."""
    # Images are structured /images/<category>/xxxxxxxx.png
    # Link for rendering images, just in case my butt forgets
    # https://stackoverflow.com/questions/33355159/how-can-i-dynamically-render-images-from-my-images-folder-using-jinja-and-flask
    logger = logging.getLogger('splathelper')
    url = url.split('/')
    directory = IMAGE_DIRECTORY + url[2]
    filename = directory + '/' + url[3]
    webfilename = filename[7:]

    if not os.path.isdir(directory):
        os.makedirs(directory)
    if not os.path.exists(filename):
        logger.error("Could not find data for image '{}'. Downloading.".format(url[-1]))
        img = Image.open(BytesIO(requests.get(BASE_IMAGE_URL + '/'.join(url)).content))
        img.save(filename)
        logger.info("Image data created.")
        return webfilename
    return webfilename

def create_result(cookie, id):
    """Formats the json data into a site-friendly format."""
    try:
        # Try to retrieve loaded data
        battle = load_individual_battle_data(cookie, id)
    except:
        # if it doesn't work, retrieve it from the server
        battle = connect.get_individual_battle_data(cookie, id)
    # build the result overview
    result = {
        'stage': battle['stage']['name'],
        'outcome': battle['my_team_result']['name'],
        'mode': battle['game_mode']['name'],
        'type': battle['rule']['name'],
    }
    # if the try block succeeds, the battle is turf, if the except block does, it's ranked/league
    try:
        result['my_team_percentage'] = battle['my_team_percentage']
        result['enemy_team_percentage'] = battle['other_team_percentage']
    except:
        result['my_team_percentage'] = battle['my_team_count']
        result['enemy_team_percentage'] = battle['other_team_count']
        result['rank'] = battle['udemae']['name']
        try:
            # TRY another check to see if it's a league battle
            result['my_league_power'] = battle['my_estimate_league_point']
            result['enemy_league_power'] = battle['other_estimate_league_point']
        except: pass # EXCEPT this time we don't care

    enemies = []
    allies = []

    for e in battle['other_team_members']:
        enemy = {
            'name': e['player']['nickname'],
            'turf_inked': e['game_paint_point'],
            'weapon_name': e['player']['weapon']['name'],
            'weapon_img': get_image(e['player']['weapon']['image']),
            'weapon_sub': get_image(e['player']['weapon']['sub']['image_a']),
            'weapon_special': get_image(e['player']['weapon']['special']['image_a']),
            'deaths': e['death_count'],
            'assists': e['assist_count'],
            'kills': e['kill_count'],
            'specials': e['special_count'],
            'level': e['player']['player_rank']
        }

        # add clothing names, images, skills, and subs to the dictionary
        for item in ['head', 'clothes', 'shoes']:
            enemy[item] = e['player'][item]['name']
            enemy[item + "_img"] = get_image(e['player'][item]['image'])
            enemy[item + "_skill"] = get_image(e['player'][item + "_skills"]['main']['image'])
            enemy[item + "_subs"] = [get_image(skill['image']) for skill in e['player'][item + "_skills"]['subs'] if skill != None]
        enemies.append(enemy)

    # combine player and ally result for uniform viewing
    battle['my_team_members'].append(battle['player_result'])
    for a in battle['my_team_members']:
        ally = {
            'name': a['player']['nickname'],
            'turf_inked': a['game_paint_point'],
            'weapon_name': a['player']['weapon']['name'],
            'weapon_img': get_image(a['player']['weapon']['image']),
            'weapon_sub': get_image(a['player']['weapon']['sub']['image_a']),
            'weapon_special': get_image(a['player']['weapon']['special']['image_a']),
            'deaths': a['death_count'],
            'assists': a['assist_count'],
            'kills': a['kill_count'],
            'specials': a['special_count'],
            'level': a['player']['player_rank']
        }

        # add clothing names, images, skills, and subs to the dictionary
        for item in ['head', 'clothes', 'shoes']:
            ally[item] = a['player'][item]['name']
            ally[item + "_img"] = get_image(a['player'][item]['image'])
            ally[item + "_skill"] = get_image(a['player'][item + "_skills"]['main']['image'])
            ally[item + "_subs"] = [get_image(skill['image']) for skill in a['player'][item + "_skills"]['subs'] if skill != None]
        allies.append(ally)

    return result, enemies, allies


def save_player_data(cookie, results, exempt_keys=['stage', 'my_team_result', 'game_mode', 'rule', 'my_team_percentage', 'other_team_percentage', 'my_team_count', 'other_team_count', 'udemae', 'my_estimate_league_point', 'other_estimate_league_point', 'other_team_members', 'my_team_members', 'player_result']):
    logger = logging.getLogger('splathelper')
    found = False
    player_id = results[0]['player_result']['player']['principal_id']
    pdata_loc = 'playerdata/{0}/'.format(player_id)
    csv_data = []
    logger.info('Searching for player data to update...')
    if not os.path.isdir(pdata_loc): os.makedirs(pdata_loc)
    with open(pdata_loc + "battles.csv", 'a+'): pass # Make sure file exists
    with open(pdata_loc + "battles.csv", 'r+') as f:
        data = list(csv.DictReader(f))
        if data != []:
            [csv_data.append(result) for result in data]
    bnumbers = [int(result['battle_number']) for result in csv_data]
    for r in results:
        if not int(r['battle_number']) in bnumbers:
            logger.info("Adding battle result '{0}' to user {1}'s file.".format(r['battle_number'], player_id))
            pr = r['player_result']
            csv_result = {
                'game_mode': r['game_mode']['name'],
                'type': r['rule']['name'],
                'outcome': r['my_team_result']['name'],
                'turf_inked': pr['game_paint_point'],
                'battle_number': r['battle_number'],
                'player_level': r['player_rank'],
                'player_assists': pr['assist_count'],
                'player_deaths': pr['death_count'],
                'player_kills': pr['kill_count'],
                'player_specials': pr['special_count'],
                'player_weapon': pr['player']['weapon']['name'],
            }
            try:
                csv_result['my_team_percentage'] = r['my_team_percentage']
                csv_result['enemy_team_percentage'] = r['other_team_percentage']
            except KeyError:
                # in this case, the battle is ranked mode
                csv_result['my_team_percentage'] = r['my_team_count']
                csv_result['enemy_team_percentage'] = r['other_team_count']
            csv_data.insert(0, csv_result)
            found = True

            # save needed individual json data
            try:
                result = connect.get_individual_battle_data(cookie, r['battle_number'])
                for k, v in dict(result).items():
                    if k not in exempt_keys:
                        del result[k]
                with open(pdata_loc + r['battle_number'] + ".json", 'w+') as f:
                    json.dump(result, f, indent=4)
            except: pass #in this case there are probably more battles in the battles.csv than there are current results
    with open(pdata_loc + "battles.csv", 'w+') as f:
        if not found: logger.info("Found no extra data.")
        keys = ['battle_number', 'game_mode', 'type', 'outcome', 'my_team_percentage', 'enemy_team_percentage', 'turf_inked', 'player_level',
        'player_assists', 'player_deaths', 'player_kills', 'player_specials', 'player_weapon']
        csv_writer = csv.DictWriter(f, keys)
        csv_writer.writeheader()
        csv_writer.writerows(csv_data)
    return player_id

def load_player_data(player):
    if len(player) == 40:
        data = connect.get_battle_data(player)['results']
        pid = data[0]['player_result']['player']['principal_id']
        save_player_data(player, data)
    else: pid = player
    with open('playerdata/{0}/battles.csv'.format(pid), 'r') as f:
        data = list(csv.DictReader(f))
    return sorted(data, key=lambda item: item['battle_number'], reverse=True), pid

def load_individual_battle_data(cookie, id):
    if len(cookie) == 40: pid = save_player_data(cookie, connect.get_battle_data(cookie)['results'])
    else: _, pid = load_player_data(cookie)
    with open('playerdata/{0}/{1}.json'.format(pid, id), 'r') as f:
        return json.load(f)
