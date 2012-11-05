from BeautifulSoup import BeautifulSoup
from models import Session, Game, GamePlayed, Player
import dbutils
import urllib2 #@UnresolvedImport


headers = { 'User-Agent' : 'Mozilla/5.0' }
base_game_details_url = 'http://www.easportsworld.com/en_US/clubs/partial/401A0001/273/match-results/details?match_id=%s&type=all'

def check_games():
    games_list_req = urllib2.Request('https://dl.dropbox.com/u/6996716/simple_games_list.htm', None, headers)
    games_list_html = urllib2.urlopen(games_list_req, None, 30).read()
    games_list_soup = BeautifulSoup(games_list_html)

    games = games_list_soup.findAll('div', id=lambda x: x and x.startswith('match-detail-container'))

    for game in games:
        game_id = game['id'][23:]#strips game id from match-detail-container-36028797029524422
        game = Session().query(Game).filter(matchid=game_id).first()
        if game is None:
            process_game(game_id)
        else: #we have already processed the game, ignore it
            continue

def process_game(game_id):
    game_url = base_game_details_url % game_id
    game_req = urllib2.Request(game_url, None, headers)
    try:
        game_result_html = urllib2.urlopen(game_req, None, 30).read()
        game_soup = BeautifulSoup(game_result_html)
        our_stats = game_soup.find('div', {"class":'yui-u first'})
        guys_who_played = our_stats.findAll('a', {"title":lambda x: x and x.startswith('View'), "class":None})
        session = Session()
        game = Game(match_id=game_id)
        session.add(game)
        session.flush()
        for teammate in guys_who_played:
            player = dbutils.get_or_create(session, Player, username=teammate.contents[0])
            player.games_played.append(game)
        session.flush()
        session.commit()
        pass
    except:
        print('Game request failed for %s' % game_id)
