import life as lfe
import weapons

def _weapon_equipped_and_ready(life):
	_wep = lfe.get_held_items(life,matches=[{'type': 'gun'}])
	
	if not _wep:
		return False
	
	#TODO: More than one weapon
	_wep = lfe.get_inventory_item(life,_wep[0])
	_feed = weapons.get_feed(_wep)
	
	if not _feed:
		return False
	
	if not _feed['rounds']:
		print 'feed in gun with no ammo'
		return False
	
	return True

def _get_feed(life,weapon):
	_feeds = lfe.get_all_inventory_items(life,matches=[{'type': weapon['feed'],'ammotype': weapon['ammotype']}])

	_highest_feed = {'rounds': -1,'feed': None}
	for feed in [lfe.get_inventory_item(life,_feed['id']) for _feed in _feeds]:
		if feed['rounds']>_highest_feed['rounds']:
			_highest_feed['rounds'] = feed['rounds']
			_highest_feed['feed'] = feed
	
	return _highest_feed['feed']

def _refill_feed(life,feed):
	if not lfe.is_holding(life, feed['id']) and not lfe.can_hold_item(life):
		logging.warning('No hands free to load ammo!')
		
		return False
	
	if not lfe.get_held_items(life,matches=[{'id': feed['id']}]):
		_hold = lfe.add_action(life,{'action': 'removeandholditem',
			'item': feed['id']},
			200,
			delay=0)
	
	#logging.info('%s is refilling ammo.' % life['name'][0])

	#TODO: No check for ammo type.
	
	_loading_rounds = len(lfe.find_action(life,matches=[{'action': 'refillammo'}]))
	if _loading_rounds >= len(lfe.get_all_inventory_items(life,matches=[{'type': 'bullet', 'ammotype': feed['ammotype']}])):
		if not _loading_rounds:
			return True
		return False
	
	if len(lfe.find_action(life,matches=[{'action': 'refillammo'}])):
		return False
	
	_rounds = len(feed['rounds'])
	
	if _rounds>=feed['maxrounds']:
		print 'Full?'
		return True
	
	_ammo_count = len(lfe.get_all_inventory_items(life,matches=[{'type': 'bullet', 'ammotype': feed['ammotype']}]))
	_ammo_count += len(feed['rounds'])
	_rounds_to_load = numbers.clip(_ammo_count,0,feed['maxrounds'])
	for ammo in lfe.get_all_inventory_items(life,matches=[{'type': 'bullet', 'ammotype': feed['ammotype']}])[:_rounds_to_load]:		
		lfe.add_action(life,{'action': 'refillammo',
			'ammo': feed,
			'round': ammo},
			200,
			delay=5)
		
		_rounds += 1

def _equip_weapon(life):
	_best_wep = get_best_weapon(life)
	
	if not _best_wep:
		return False
	
	_weapon = _best_wep['weapon']
	
	#TODO: Need to refill ammo?
	if not weapons.get_feed(_weapon):
		_feed = _best_wep['feed']
		
		if _feed:
			#TODO: How much time should we spend loading rounds if we're in danger?
			if _refill_feed(life,_feed):
				lfe.add_action(life,{'action': 'reload',
					'weapon': _weapon,
					'ammo': _feed},
					200,
					delay=0)
		else:
			print 'No feed!'
			
			return False
		
		return False
	else:
		lfe.add_action(life,{'action': 'equipitem',
			'item': _weapon['id']},
			300,
			delay=0)
		
		print 'Loaded!'
		return True
	
	return True

def is_weapon_equipped(life):
	_weapon = lfe.get_held_items(life,matches=[{'type': 'gun'}])
	
	if not _weapon:
		return False
	
	return lfe.get_inventory_item(life,_weapon[0])

def has_weapon(life):
	return lfe.get_all_inventory_items(life,matches=[{'type': 'gun'}])

def has_usable_weapon(life):
	for weapon in lfe.get_all_inventory_items(life,matches=[{'type': 'gun'}]):
		if lfe.get_all_inventory_items(life, matches=[{'type': weapon['feed'],'ammotype': weapon['ammotype']}]):
			return True
	
	return False

def get_best_weapon(life):
	_weapons = lfe.get_all_inventory_items(life,matches=[{'type': 'gun'}])
	
	#TODO: See issue #64
	_best_wep = {'weapon': None,'rounds': 0}
	for _wep in _weapons:
		
		_feeds = lfe.get_all_inventory_items(life,
			matches=[{'type': _wep['feed'],'ammotype': _wep['ammotype']}])
		
		#TODO: Not *really* the best weapon, just already loaded
		if weapons.get_feed(_wep):
			_best_wep['weapon'] = _wep
			break

		#print _feeds
		_best_feed = {'feed': None, 'rounds': -1}
		for _feed in _feeds:
			
			#TODO: Check to make sure this isn't picking up the rounds already in the mag/clip
			_rounds = len(lfe.get_all_inventory_items(life,
				matches=[{'type': 'bullet', 'ammotype': _wep['ammotype']}]))
			_rounds += len(_feed['rounds'])
			
			if len(_feed['rounds']) > _best_feed['rounds']:
				_best_feed['rounds'] = len(_feed['rounds'])
				_best_feed['feed'] = _feed

			if _rounds > _best_wep['rounds']:
				_best_wep['weapon'] = _wep
				_best_wep['rounds'] = _rounds

		if not _best_feed['feed']:
			_best_wep['weapon'] = None
			#print 'No feed for weapon.',life['name']
			return False
		else:
			_best_wep['feed'] = _best_feed['feed']
	
	if not _best_wep['weapon']:
		return False
	
	return _best_wep

def combat(life,target,source_map):
	_pos_for_combat = position_for_combat(life,target,target['last_seen_at'],source_map)
	
	if not target['escaped'] and not _pos_for_combat:
		return False
	elif _pos_for_combat:
		lfe.clear_actions(life,matches=[{'action': 'move'}])
	
	if not lfe.can_see(life,target['life']['pos']):
		if not target['escaped'] and not travel_to_target(life,target,target['last_seen_at'],source_map):
			lfe.memory(life,'lost sight of %s' % (' '.join(target['life']['name'])),target=target['life']['id'])
			target['escaped'] = True
		elif target['escaped']:
			search_for_target(life,target,source_map)
		
		return False
	
	if not len(lfe.find_action(life,matches=[{'action': 'shoot'}])):
		lfe.add_action(life,{'action': 'shoot','target': target['life']['pos'][:]},50,delay=15)

def handle_potential_combat_encounter(life,target,source_map):
	if not has_considered(life,target['life'],'resist'):
		if not combat.is_weapon_equipped(target['life']) and lfe.can_see(life,target['life']['pos']):
			communicate(life,'comply',target=target['life']) #HOSTILE
			lfe.clear_actions(life)
			
			return True
	
	if combat.is_weapon_equipped(life):
		combat(life,target,source_map)
	else:
		handle_hide_and_decide(life,target,source_map)