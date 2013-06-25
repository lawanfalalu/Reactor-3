from globals import *

import combat

import logging

def create_group(life, add_creator=True):
	_group = {'creator': life['id'],
	    'leader': None,
	    'members': [],
	    'camp': None}
	
	SETTINGS['groupid'] += 1
	GROUPS[SETTINGS['groupid']] = _group
	
	logging.debug('%s created group: %s' % (' '.join(life['name']), SETTINGS['groupid']))
	
	if add_creator:
		add_member(SETTINGS['groupid'], life['id'])
		_group['leader'] = life['id']

def add_member(group_id, life_id):
	if is_member(group_id, life_id):
		raise Exception('%s is already a member of group: %s' % (' '.join(LIFE[life_id]['name']), group_id))
	
	LIFE[life_id]['group'] = group_id
	get_group(group_id)['members'].append(life_id)
	
	logging.debug('Added %s to group \'%s\'' % (' '.join(LIFE[life_id]['name']), SETTINGS['groupid']-1))

def get_group(group_id):
	if not group_id in GROUPS:
		raise Exception('Group does not exist: %s' % group_id)
	
	return GROUPS[group_id]

def get_camp(group_id):
	return get_group(group_id)['camp']

def set_camp(group_id, camp_id):
	get_group(group_id)['camp'] = camp_id

def get_combat_score(group_id, potential=False):
	_group = get_group(group_id)
	_score = 0
	
	for member in [LIFE[l] for l in _group['members']]:
		if combat.get_best_weapon(member):
			if not potential and not combat.weapon_equipped_and_ready(member):
				continue
			
			_score += 1
	
	return _score

def get_potential_combat_score(group_id):
	return get_combat_score(group_id, potential=True)

def is_member(group_id, life_id):
	_group = get_group(group_id)
	
	if life_id in _group['members']:
		return True
	
	return False

def is_leader(group_id, life_id):
	_group = get_group(group_id)
	
	if life_id == _group['leader']:
		return True
	
	return False

def remove_member(group_id, life_id):
	_group = get_group(group_id)
	
	if not is_member(group_id, life_id):
		raise Exception('%s is not a member of group: %s' % (' '.join(LIFE[life_id]), group_id))
	
def delete_group(group_id):
	for member in get_group(group_id)['members']:
		remove_member(group_id, member)
		LIFE[member]['group'] = None
	
	del GROUPS[group_id]