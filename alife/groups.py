from globals import *

import graphics as gfx
import life as lfe

import references
import judgement
import movement
import survival
import memory
import action
import combat
import speech
import events
import chunks
import logic
import sight
import camps
import brain
import stats
import raids
import jobs

import logging

def create_group(life, add_creator=True):
	WORLD_INFO['groupid'] += 1
	_id = str(WORLD_INFO['groupid']-1)
	
	discover_group(life, _id)
	
	if add_creator:
		add_member(life, _id, life['id'])
	
	set_leader(life, _id, life['id'])
	
	return _id

def group_exists(life, group_id):
	return (group_id in life['known_groups'])

def get_group(life, group_id):
	if not group_exists(life, group_id):
		raise Exception('Group does not exist: %s' % group_id)
	
	return life['known_groups'][group_id]

def flag(life, group_id, flag, value):
	get_group(life, group_id)['flags'][flag] = value

def get_flag(life, group_id, flag):
	if not flag in get_group(life, group_id)['flags']:
		return None
	
	return get_group(life, group_id)['flags'][flag]

def discover_group(life, group_id):
	if not group_id in life['known_groups']:
		life['known_groups'][group_id] = {'id': group_id,
		                        'members': [],
		                        'leader': None,
		                        'shelter': None,
		                        'stage': STAGE_FORMING,
		                        'flags': {}}
		
		if 'player' in life:
			gfx.message('You learn about group %s.' % group_id)
		
		return True
	
	return False

def update_group_memory(life, group_id, flag, value):
	_previous_value = life['known_groups'][group_id][flag]
	life['known_groups'][group_id][flag] = value
	
	logging.debug('%s updated group %s\'s memory: %s: %s -> %s' % (' '.join(life['name']), group_id, flag, _previous_value, value))

def get_group_memory(life, group_id, flag):
	return life['known_groups'][group_id][flag]

def get_group_relationships():
	_groups = {grp: {_grp: 0 for _grp in WORLD_INFO['groups'] if not _grp == grp} for grp in WORLD_INFO['groups']}

def add_member(life, group_id, life_id):
	if is_member(life, group_id, life_id):
		raise Exception('%s is already a member of group: %s' % (' '.join(LIFE[life_id]['name']), group_id))
	
	if LIFE[life_id]['group']:
		lfe.memory(LIFE[life_id], 'left group for group', left_group=LIFE[life_id]['group'], group=group_id)
		remove_member(LIFE[life_id]['group'], life_id)
	
	_group = get_group(life, group_id)
	for member in _group['members']:
		brain.meet_alife(LIFE[member], LIFE[life_id])
	
	if _group['shelter']:
		LIFE[life_id]['shelter'] = _group['shelter']
		lfe.memory(LIFE[life_id], 'shelter founder', shelter=_group['shelter'], founder=_group['leader'])
	
	discover_group(LIFE[life_id], group_id)
	LIFE[life_id]['group'] = group_id
	_group['members'].append(life_id)
	
	if _group['leader'] and 'player' in LIFE[_group['leader']]:
		_text = '%s has joined your group.' % ' '.join(LIFE[life_id]['name'])
		gfx.message(_text, style='good')
		
		if sight.can_see_target(LIFE[_group['leader']], life_id):
			logic.show_event(_text, life=LIFE[life_id], delay=1)
	
	if SETTINGS['controlling'] == life_id:
		gfx.message('You join group %s.' % group_id, style='good')
	
	logging.debug('Added %s to group \'%s\'' % (' '.join(LIFE[life_id]['name']), WORLD_INFO['groupid']))

def remove_member(life, group_id, life_id):
	_group = get_group(life, group_id)
	
	if not is_member(life, group_id, life_id):
		raise Exception('%s is not a member of group: %s' % (' '.join(LIFE[life_id]['name']), group_id))
	
	LIFE[life_id]['group'] = None
	_group['members'].remove(life_id)
	
	#reconfigure_group(life, group_id)

def reconfigure_group(life, group_id):
	_group = get_group(life, group_id)
	
	if not is_member(life, group_id, _group['leader']):
		logging.debug('Leader \'%s\' is leaving group #%s' % (' '.join(LIFE[_group['leader']]['name']), group_id))
	
	_successor = find_successor(life, group_id, assign=True)
	
	if _successor:
		logging.debug('\'%s\' is now leader of group #%s' % (' '.join(LIFE[_successor]['name']), group_id))
	else:
		logging.error('No successor could be found for group #%s (THIS SHOULD NOT HAPPEN)' % group_id)

def find_successor(life, group_id, assign=False):
	_group = get_group(life, group_id)
	_members = {l: 0 for l in _group['members']}
	
	for member1 in _group['members']:
		for member2 in _group['members']:
			if member1 == member2:
				continue
			
			_members[member2] += brain.knows_alife_by_id(LIFE[member1], member2)['trust']
	
	_highest = {'score': 0, 'id': None}
	for entry in _members:
		if not _highest['id'] or _members[entry] > _highest['score']:
			_highest['id'] = entry
			_highest['score'] = _members[entry]
	
	if _highest['id'] and assign:
		set_leader(group_id, _highest['id'])
	elif assign:
		raise Exception('No successor found, but `assign` is True. Stopping.')
	
	return _highest['id']

def distribute(life, message, filter_by=[], **kvargs):
	_group = get_group(life, life['group'])
	
	for member in _group['members']:
		if member in filter_by:
			continue
		
		speech.communicate(life, message, radio=True, matches=[{'id': member}], **kvargs)

def add_job(life, group_id, job_id):
	_group = get_group(life, group_id)
	
	#TODO: Remove
	if not 'jobs' in _group:
		_group['jobs'] = []
	
	_group['jobs'].append(job_id)
	
	logging.debug('Registered job %s with group %s' % (job_id, group_id))

def add_event(life, group_id, event):
	_group = get_group(life, group_id)
	
	_group['events'][str(_group['event_id'])] = event
	_group['event_id'] += 1
	
	return str(_group['event_id']-1)

def get_event(life, group_id, event_id):
	return get_group(life, group_id)['events'][event_id]

def process_events(life, group_id):
	_group = get_group(life, group_id)
	
	for event in _group['events'].values():
		events.process_event(event)

def get_motive(life, group_id):
	return get_group(life, group_id)['claimed_motive']

def announce(life, group_id, gist, message='', order=False, consider_motive=False, filter_if=[], **kwargs):
	_group = get_group(life, group_id)
	
	if consider_motive:
		if _group['claimed_motive'] == 'wealth':
			_announce_to = []
			
			for life_id in LIFE.keys():
				if life_id == life['id']:
					continue
				
				if stats.is_same_species(life, life_id):
					_announce_to.append(life_id)
		elif _group['claimed_motive'] == 'crime':
			_announce_to = judgement.get_trusted(life, visible=False)

			for life_id in _announce_to[:]:
				if not stats.is_same_species(life, life_id):
					_announce_to.remove(life_id)
			
		elif _group['claimed_motive'] == 'survival':
			_announce_to = []
			
			for life_id in LIFE.keys():
				if life_id == life['id']:
					continue
				
				if stats.is_same_species(life, life_id):
					_announce_to.append(life_id)
			
	else:
		_announce_to = _group['members'][:]
		_announce_to.remove(life['id'])
	#TODO: Could have an option here to form an emergency "combat" group
	
	for life_id in _announce_to:
		if filter_if and filter_if(LIFE[life_id]):
			continue
		
		#_sent = speech.has_sent(life, life_id, gist)
		#if _sent and WORLD_INFO['ticks']-_sent<15:
		#	continue
		
		if order:
			memory.create_order(life, life_id, gist, message, **kwargs)
		else:
			memory.create_question(life, life_id, gist, **kwargs)

def get_shelter(life, group_id):
	return get_group_memory(life, group_id, 'shelter')

def set_shelter(life, group_id, shelter):
	update_group_memory(life, group_id, 'shelter', shelter)

def find_shelter(life, group_id):
	_group = get_group(life, group_id)
	_shelter = judgement.get_best_shelter(life)
	
	if _shelter:
		set_shelter(life, group_id, chunks.get_chunk(_shelter)['reference'])
		announce(life, group_id, 'found_shelter')
	else:
		if get_stage(life, group_id) < STAGE_SETTLING:
			set_stage(life, group_id, STAGE_SETTLING)
			announce(life, group_id, 'update_group_stage',
				    filter_if=lambda alife: get_stage(alife, group_id)>=STAGE_SETTLING)

def find_and_announce_shelter(life, group_id):
	_shelter = get_shelter(life, group_id)
	
	if _shelter:
		if references.is_in_reference(life['pos'], references.get_reference(_shelter)):
			announce(life, group_id, 'update_group_shelter',
				    filter_if=lambda alife: get_shelter(alife, group_id)==_shelter)
	else:
		find_shelter(life, group_id)

def get_leader(life, group_id):
	return get_group(life, group_id)['leader']

def set_leader(life, group_id, life_id):
	_group = get_group(life, group_id)
	_group['leader'] = life_id
	
	set_motive(life, group_id, stats.get_group_motive(LIFE[life_id]))
	
	lfe.memory(LIFE[life_id], 'claimed to be the leader of group', group=group_id)
	logging.debug('%s claims to be the leader of group #%s' % (' '.join(LIFE[life_id]['name']), group_id))

def set_motive(life, group_id, motive):
	get_group(life, group_id)['claimed_motive'] = motive

def get_stage(life, group_id):
	return get_group_memory(life, group_id, 'stage')

def set_stage(life, group_id, stage):
	update_group_memory(life, group_id, 'stage', stage)

def get_combat_score(life, group_id, potential=False):
	_group = get_group(life, group_id)
	_score = 0
	
	for member in [LIFE[l] for l in _group['members']]:
		if combat.get_best_weapon(member):
			if not potential and not combat.weapon_equipped_and_ready(member):
				continue
			
			_score += 1
	
	return _score

def get_potential_combat_score(life, group_id):
	return get_combat_score(life, group_id, potential=True)

def get_status(life, group_id):
	_group = get_group(life, group_id)
	
	_total_trust = 0
	_total_danger = 0
	for member1 in _group['members']:
		for member2 in _group['members']:
			if member1 == member2:
				continue
			
			if not brain.knows_alife_by_id(LIFE[member1], member2):
				continue
			
			if judgement.can_trust(LIFE[member1], member2):
				_total_trust += judgement.get_trust(LIFE[member1], member2)
			else:
				_total_danger += LIFE[member1]['know'][member2]['danger']
	
	return _total_trust,_total_danger

def get_total_trust(group_id):
	return get_status(group_id)[0]

def get_total_danger(group_id):
	return get_status(group_id)[1]

def get_unwanted_members_with_perspective(life, group_id):
	_group = get_group(life, group_id)
	_untrusted = []
	
	for member in [m for m in _group['members'] if not life['id'] == m]:
		if judgement.can_trust(life, member):
			continue
		
		_untrusted.append(member)
	
	return _untrusted

def has_camp(group_id):
	for camp in WORLD_INFO['camps']:
		if camps.get_controlling_group_global(camp) == group_id:
			return camp
	
	return None

def get_jobs(life, group_id):
	_group = get_group(life, group_id)
	_jobs = []
	_leader = LIFE[_group['leader']]
	
	if not has_camp(group_id):
		_nearest_camp = camps.get_nearest_known_camp(_leader)
		
		if _leader['known_camps']:
			_j = jobs.create_job(_leader, 'Raid', gist='start_raid', description='Raid camp %s.' % _nearest_camp['id'])
			_pos = lfe.get_current_chunk(_leader)['pos']
			_chunk_key = lfe.get_current_chunk_id(_leader)
		
			jobs.add_task(_j, '0', 'announce_to_group',
			              action.make_small_script(function='announce_to_group',
			                                       kwargs={'group_id': group_id,
			                                               'gist': 'announce_group_job',
			                                               'message': jobs.get_job(_j)['description'],
			                                               'job_id': _j}),
			              player_action=action.make_small_script(function='always'),
			              description='Gather group members.')
			jobs.add_task(_j, '1', 'move_to_chunk',
			              action.make_small_script(function='travel_to_position',
			                                       kwargs={'pos': _pos}),
			              player_action=action.make_small_script(function='is_in_chunk',
	                                           kwargs={'chunk_key': _chunk_key}),
			              description='Travel to position %s, %s' % (_pos[0], _pos[1]),
				          delete_on_finish=False)
			jobs.add_task(_j, '2', 'wait_for_number_of_group_members_in_chunk',
			              action.make_small_script(function='number_of_alife_in_chunk_matching',
			                                       kwargs={'amount': 2,
			                                               'chunk_key': _chunk_key,
			                                               'matching': {'group': _leader['group']}}),
			              description='Wait until everyone arrives.')
			#jobs.add_task(_j, '3', 'talk',
			#              action.make_small_script(function='travel_to_position',
			#                                       kwargs={'pos': chunks.get_nearest_chunk_in_list(_leader['pos'], camps.get_camp(_nearest_camp['id'])['reference'])}),
			#              requires=['1'],
			#              delete_on_finish=False)
			
			_jobs.append(_j)
	
	if len(_leader['known_groups'])>1:
		_lowest = {'score': 0, 'group': None}
		for group_id in [g for g in _leader['known_groups'] if not g==_leader['group']]:
			_score = judgement.judge_group(_leader, group_id)
			
			if not _lowest['group'] or _score < _lowest['score']:
				_lowest['score'] = _score
				_lowest['group'] = group_id
			
		
		print 'RAID', _lowest
	else:
		print 'ony one'
	
	return _jobs

def manage_resources(life, group_id):
	_group = get_group(life, group_id)
	_last_resource_check = get_flag(life, group_id, 'last_resource_count')
	
	if _last_resource_check and WORLD_INFO['ticks']-_last_resource_check<=100:
		return True
	
	announce(life, group_id, 'resource_check',
	         filter_if=lambda alife: WORLD_INFO['ticks']-speech.has_sent(life, alife['id'], 'resource_check')<=500)
	
	flag(life, group_id, 'last_resource_count', WORLD_INFO['ticks'])

def is_member(life, group_id, life_id):
	_group = get_group(life, group_id)
	
	if life_id in _group['members']:
		return True
	
	return False

def order_to_loot(life, group_id, add_leader=False):
	#TODO: We should really consider moving the needs portion of this code outside of this function
	#Because this function really only does something on the first run, rendering it into just another
	#announce loop...
	
	_group = get_group(life, group_id)
	
	_requirements = [action.make_small_script(function='has_number_of_items_matching',
	                                          args={'matching': [{'type': 'drink'}], 'amount': 1})]
	
	_j = jobs.create_job(life, 'Loot for group %s.' % life['group'],
	                     gist='loot_for_group',
	                     description='Collect loot for group.',
	                     group=life['group'],
	                     requirements=_requirements)
	
	if _j:
		for member in _group['members']:
			if member == _group['leader'] and not add_leader:
				continue
			
			survival.add_needed_item(LIFE[member],
				                    {'type': 'drink'},
				                    amount=1,
			                         pass_if=_requirements,
				                    satisfy_if=action.make_small_script(function='group_needs_resources',
				                                                        args={'group_id': group_id}),
				                    satisfy_callback=action.make_small_script(return_function='pass'))
		
		jobs.add_task(_j, '0', 'bring_back_loot',
		              action.make_small_script(function='find_target',
		                                       kwargs={'target': _group['leader'],
		                                               'distance': 5,
		                                               'follow': False}),
		              player_action=action.make_small_script(function='can_see_target',
		                                                     kwargs={'target_id': _group['leader']}),
		              description='Drop the item off at the camp',
		              delete_on_finish=False)
		
		jobs.add_task(_j, '1', 'flag_item',
		              action.make_small_script(function='flag_item_matching',
		                                       kwargs={'matching': {'type': 'drink'},
		                                               'flag': 'ignore'}),
		              player_action=action.make_small_script(function='always'),
		              description='Ignore this',
		              delete_on_finish=False)
		
		jobs.add_task(_j, '2', 'drop_item',
		              action.make_small_script(function='drop_item_matching',
		                                       kwargs={'matching': {'type': 'drink'}}),
		              player_action=action.make_small_script(function='never'),
		              description='Drop the item off at the camp',
		              delete_on_finish=False)
		
		flag(group_id, 'loot', _j)
	
	if lfe.ticker(life, 'resource_announce', 10):
		_job_id = get_flag(group_id, 'loot')
		
		announce(life, life['group'],
			     'job',
			     'We need more resources.',
			     job_id=_job_id,
		         order=True,
			     filter_if=[action.make_small_script(function='has_needs_to_meet')])

def is_leader(life, group_id, life_id):
	_group = get_group(life, group_id)
	
	if life_id == _group['leader']:
		return True
	
	return False

def is_leader_of_any_group(life):
	if not life['group']:
		return False
	
	return is_leader(life, life['group'], life['id'])