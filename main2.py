from BeautifulSoup import BeautifulSoup
from models import Session, Game, GamePlayed, Player
import dbutils
import gspread
import urllib2 #@UnresolvedImport
import logging #@UnresolvedImport

logging.basicConfig()
logger = logging.getLogger('stats')

headers = { 'User-Agent' : 'Mozilla/5.0' }
base_game_details_url = 'http://www.easportsworld.com/en_US/clubs/partial/401A0001/273/match-results/details?match_id=%s&type=all'

def check_games():
#    games_list_req = urllib2.Request('https://dl.dropbox.com/u/6996716/simple_games_list.htm', None, headers)
    games_list_req = urllib2.Request('http://www.easportsworld.com/en_US/clubs/partial/401A0001/273/match-results/', None, headers)

    try:
        logger.info('Fetching games list . . .')
        games_list_html = urllib2.urlopen(games_list_req, None, 30).read()
    except Exception, e:
        logger.exception('Timed out fetching games list')
        games_list_html = ''
    games_list_soup = BeautifulSoup(games_list_html)

    games = games_list_soup.findAll('div', id=lambda x: x and x.startswith('match-detail-container'))
    should_update_spreadsheet = False
    for game in games:
        try:
            game_id = game['id'][23:]#strips game id from match-detail-container-36028797029524422
            game = Session().query(Game).filter_by(match_id=game_id).first()
            if game is None:
                logger.info('New game detected %s; archiving. . .' % game_id)
                process_game(game_id)
                should_update_spreadsheet = True
            else: #we have already processed the game, ignore it
                logger.debug('Already archived this game')
                pass
        except:
            pass

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
            game_played = GamePlayed(player.id, game.id)
            session.add(game_played)
        session.flush()
        session.commit()
        Session.remove()
        pass
    except Exception, e:
        print('Game request failed for %s' % game_id)

def update_monthly_games_played():
    gc = gspread.login('xtremerunnerars@gmail.com', 'muatkienjwxfpnxn')
    player_cell_locations = {'thewarmth00':'B51',
                                'rob_chainsaw':'B53',
                                'mashley93':'B55',
                                'peachy36west':'B57',
                                'm_sibs':'B59',
                                'rc_van':'B61',
                                'soviet_canuck':'B63',
                                'undertheblanket':'B65',
                                'vsmewen':'B67',
                                'hokagesama1':'B69',
                                'lnferno31':'H86'}
    sheet = gc.open_by_key('0Ak-m4uT6aXL1dExuUHdLV0x2aTNFSGNRMTV2WWdLX2c').get_worksheet(9)
    session = Session()
    our_players = session.query(Player).all()
    for player in our_players:
        cell_location = player_cell_locations[player.username.lower()]
        games_played = len(session.query(GamePlayed).filter_by(player_id=player.id).all())
        value = sheet.acell(cell_location).value
        sheet.update_acell(cell_location, str(games_played))
        if sheet.acell(cell_location).value != value:
            pass
        else:
            pass

need_to_update_google_doc = check_games()
if need_to_update_google_doc:
    update_monthly_games_played()

