__author__ = 'matt'

class GCVars(object):
    passwd = "passwd"
    uuid = "uuid"
    guid = "guid"
    lang = "lang"
    type = "type"
    version = "version"
    token = "token"
    itid = "itid"
    inid = "inid"
    name = "name"
    name2 = "name2"
    image = "image"
    image2 = "image2"
    level = "level"
    location = "location"
    amount = "amount"
            
    info = "info"
    state = "state"

    all = "all"
    building = "building"
    challenge = "challenge"
    accept = "accept"
    challenges = "challenges"
    racetype = "racetype"
    advisor = "advisor"
    opponent = "opponent"
    cars = "cars"
    transui = "transui"
    upgrades = "upgrades"
    racewinnings = "racewinnings"
    config = "config"
            
    track = "track"
    uid1 = "uid1"
    uid2 = "uid2"
    toid = "toid"
    fbids = "fbids"
            
    checklist = "checklist"
            
    car = "car"
    crid = "crid"
    cuid = "cuid"
    upid = "upid"
            
    chid = "chid"
    laptime = "laptime"
    laptime2 = "laptime2"
    replay = "replay"
    events = "events"
    events2 = "events2"
    cardata = "cardata"
    
    # finishrace
    scores = "scores"
    score_drift = "score_drift"
    score_shift = "score_shift"
    score_start = "score_start"
    score_prize = "score_prize"
            
    # player state
    cash = "cash"
    advice_checklist = "advice_checklist"
    current_car = "current_car"
    updated = "updated"
    results = "results"
    total_wins = "total_wins"
    total_races = "total_races"
    total_ai_wins = "total_ai_wins"
    total_ai_races = "total_ai_races"
    gold = "gold"


class GCErrors(object):
    dup_login = "dup_login"

class GCWarnings(object):
    building_not_owned = "building_not_owned"
    building_finished = "building_finished"
    building_under_construction = "building_under_construction"
    player_not_found = "player_not_found"
    item_max_level_reached = "item_max_level_reached"
    cash_not_enough = "cash_not_enough"
    gold_not_enough = "gold_not_enough"


class GCWarningMessages (object):
    building_not_owned = "Player does not have required building to buy upgrade."
