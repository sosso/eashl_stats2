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
    games_list_req = urllib2.Request('https://dl.dropbox.com/u/6996716/simple_games_list.htm', None, headers)
#    games_list_req = urllib2.Request('http://www.easportsworld.com/en_US/clubs/partial/401A0001/273/match-results/', None, headers)

    try:
        logger.info('Fetching games list . . .')
        games_list_html = urllib2.urlopen(games_list_req, None, 30).read()
    except Exception, e:
        logger.exception('Timed out fetching games list')
        games_list_html = ''
    games_list_soup = BeautifulSoup(games_list_html)

    games = games_list_soup.findAll('div', id=lambda x: x and x.startswith('match-detail-container'))
    game_times = games_list_soup.findAll('div', {'class':lambda x: x and x.startswith('strong small')})
    #parent(match detail) == parent(parent(parent(parent(time))))
    should_update_spreadsheet = False
    nightly_end = None
    start_index = None
    end_index = None
    have_updated_nightly_totals = False
    for game in games:
        index = games.index(game)
        game.game_time = filter(lambda gametime: gametime.parent.parent.parent.parent.parent == game.parent, game_times)[0].contents[0][6:]#strips the Time: from Time: #:## AM
        game_score = game.parent.findAll('div', {'class':lambda x: x and x.startswith('match-result-score')})[0].contents[0].split(" - ")
        game.our_score = int(game_score[0])
        game.their_score = int(game_score[1])
        if int(game_score[0]) > int(game_score[1]):
            game.win = True
        else:
            game.win = False
        if nightly_end is None:
            nightly_end = game.game_time
            end_index = index
        elif not have_updated_nightly_totals:
            if index > 0:
                previous_gametime = games[index - 1].game_time
                if int(game.game_time.split(":")[0]) > int(previous_gametime.split(":")[0]):
                    start_index = games.index(game) - 1
                    nightly_games = games[end_index:start_index]
                    process_nightly_games(nightly_games)
                    pass

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

def process_nightly_games(nightly_games_list):
    games_played = len(nightly_games_list)
    if games_played > 0:
        wins = 0
        losses = 0
        overtime_losses = '?'
        goals_for = 0
        goals_against = 0

        for game in games_played:
            if game.win: wins += 1
            goals_for += game.our_score
            goals_against += game.their_score
        losses = games_played - wins
        diff = goals_for - goals_against
        try: win_percentage = float(wins / games_played)
        except: win_percentage = 0
        gc = gspread.login('xtremerunnerars@gmail.com', 'muatkienjwxfpnxn')
        stats = [games_played, wins, losses, overtime_losses, goals_for, goals_against, diff, win_percentage]

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

