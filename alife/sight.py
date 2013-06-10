from globals import *

import life as lfe

import judgement
import brain

import render_fast_los
import render_los
import numbers
import logging
import time

def look(life):
	life['seen'] = []
	
	if not 'CAN_SEE' in life['life_flags']:
		return False
	
	for ai in [LIFE[i] for i in LIFE if not i == life['id']]:
		if not can_see_target(life, ai['id']):
			continue
		
		if not lfe.can_see(life, ai['pos']):
			if ai['id'] in life['know']:
				life['know'][ai['id']]['last_seen_time'] += 1
				
				#TODO: havent_seen_in_a_while?
				#if life['know'][ai['id']]['last_seen_time'] >= 300:
				#	life['know'][ai['id']]['escaped'] = True
			continue
		
		life['seen'].append(ai['id'])
		
		#TODO: Don't pass entire life, just id
		if ai['id'] in life['know']:
			life['know'][ai['id']]['last_seen_time'] = 0
			life['know'][ai['id']]['last_seen_at'] = ai['pos'][:]
			
			_chunk_id = lfe.get_current_chunk_id(ai)
			judgement.judge_chunk(life, _chunk_id)
			
			continue
		
		brain.meet_alife(life, ai)
	
	for item in [ITEMS[item] for item in ITEMS]:
		if item.has_key('id') or item.has_key('parent'):
			continue
		
		_can_see = lfe.can_see(life,item['pos'])
		if _can_see:
			_item_chunk_key = '%s,%s' % ((item['pos'][0]/SETTINGS['chunk size'])*SETTINGS['chunk size'],
				(item['pos'][1]/SETTINGS['chunk size'])*SETTINGS['chunk size'])
			judgement.judge_chunk(life, _item_chunk_key)
		
			if not item['uid'] in life['know_items']:
				brain.remember_item(life, item)

			life['know_items'][item['uid']]['last_seen_time'] = 0
			life['know_items'][item['uid']]['score'] = judgement.judge_item(life, item)
		elif item['uid'] in life['know_items']:
			life['know_items'][item['uid']]['last_seen_time'] += 1

def get_vision(life):
	if not 'CAN_SEE' in life['life_flags']:
		return 0
	
	#TODO: Fog? Smoke? Light?
	return life['vision_max']

def can_see_target(life, target_id):
	_knows = brain.knows_alife_by_id(life, target_id)
	_dist = numbers.distance(life['pos'], _knows['life']['pos'])
	
	if _dist >= get_vision(life):
		return False
	
	return True

def generate_los(life, target, at, source_map, score_callback, invert=False, ignore_starting=False):
	_stime = time.time()
	_cover = {'pos': None,'score': 9000}
	
	_x = numbers.clip(at[0]-(SETTINGS['los']/2),0,MAP_SIZE[0]-(SETTINGS['los']/2))
	_y = numbers.clip(at[1]-(SETTINGS['los']/2),0,MAP_SIZE[1]-(SETTINGS['los']/2))
	_top_left = (_x,_y,at[2])
	
	target_los = render_fast_los.render_fast_los(at,
		SETTINGS['los'],
		source_map)
	
	for pos in render_los.draw_circle(life['pos'][0],life['pos'][1],30):
		x = pos[0]-_top_left[0]
		y = pos[1]-_top_left[1]
		
		if pos[0]<0 or pos[1]<0 or pos[0]>=MAP_SIZE[0] or pos[1]>=MAP_SIZE[0]:
			continue
		
		if x<0 or y<0 or x>=target_los.shape[1] or y>=target_los.shape[0]:
			continue
		
		if life['pos'][0]-_top_left[0]>=target_los.shape[1] or life['pos'][1]-_top_left[1]>=target_los.shape[0]:
			continue
		
		if target_los[life['pos'][1]-_top_left[1],life['pos'][0]-_top_left[0]]==invert and not ignore_starting:
			_cover['pos'] = life['pos'][:]
			return False
		
		if source_map[pos[0]][pos[1]][at[2]+1] or source_map[pos[0]][pos[1]][at[2]+2]:
			continue
		
		if target_los[y,x] == invert:
			#TODO: Additional scores, like distance from target
			_score = score_callback(life,target['life'],pos)
			
			if _score<_cover['score']:
				_cover['score'] = _score
				_cover['pos'] = list(pos)
	
	#print time.time()-_stime
	if not _cover['pos']:
		print 'Nowhere to hide', target['life']['name'], _top_left
				
		return False
	
	return _cover

def _generate_los(life,target,at,source_map,score_callback,invert=False,ignore_starting=False):
	#Destktop
	#New: 0.0127160549164
	#Old: 0.0237522125244
	
	#Laptop:
	#New: 0.0139999389648
	#Old: 0.0350000858307
	
	#Step 1: Locate cover
	_cover = {'pos': None,'score': 9000}
	
	#TODO: Unchecked Cython flag
	_a = time.time()
	_x = numbers.clip(at[0]-(MAP_WINDOW_SIZE[0]/2),0,MAP_SIZE[0])
	_y = numbers.clip(at[1]-(MAP_WINDOW_SIZE[1]/2),0,MAP_SIZE[1])
	_top_left = (_x,_y,at[2])
	target_los = render_los.render_los(source_map,at,top_left=_top_left,no_edge=False)
	
	for pos in render_los.draw_circle(life['pos'][0],life['pos'][1],30):
		x = pos[0]-_top_left[0]
		y = pos[1]-_top_left[1]
		
		if pos[0]<0 or pos[1]<0 or pos[0]>=MAP_SIZE[0] or pos[1]>=MAP_SIZE[0]:
			continue
		
		if x<0 or y<0 or x>=target_los.shape[1] or y>=target_los.shape[0]:
			continue
		
		if life['pos'][0]-_top_left[0]>=target_los.shape[0] or life['pos'][1]-_top_left[1]>=target_los.shape[1]:
			continue
		
		if target_los[life['pos'][1]-_top_left[1],life['pos'][0]-_top_left[0]]==invert and not ignore_starting:
			_cover['pos'] = life['pos'][:]
			return False
		
		if source_map[pos[0]][pos[1]][at[2]+1] or source_map[pos[0]][pos[1]][at[2]+2]:
			continue
		
		if target_los[y,x] == invert:
			#TODO: Additional scores, like distance from target
			_score = score_callback(life,target['life'],pos)
			
			if _score<_cover['score']:
				_cover['score'] = _score
				_cover['pos'] = list(pos)
	
	if not _cover['pos']:
		print 'Nowhere to hide'		
		return False
	
	print time.time()-_a
	
	return _cover

def handle_lost_los(life):
	if life['in_combat']:
		#TODO: Do something here...
		pass
	
	#TODO: Take the original score and subtract/add stuff from there...
	_nearest_target = {'target': None,'score': 0}
	for entry in life['know']:
		_target = life['know'][entry]
		_score = judgement.judge(life,_target)
		
		if _target['escaped']:
			_score += (_target['last_seen_time']/2)
		
		if _score < _nearest_target['score']:
			_nearest_target['target'] = _target
			_nearest_target['score'] = _score
	
	return _nearest_target

def find_visible_items(life):
	return [item for item in life['know_items'].values() if not item['last_seen_time'] and not 'id' in item['item']]

def find_known_items(life, matches=[], visible=True):
	_match = []
	
	for item in [life['know_items'][item] for item in life['know_items']]:
		if not item['item']['uid'] in ITEMS:
			continue
		
		if visible and not lfe.can_see(life,item['item']['pos']):
			continue
		
		if 'parent' in item['item'] or 'id' in item['item']:
			continue
		
		if 'demand_drop' in item['flags']:
			continue
		
		if item['item']['lock']:
			continue
		
		_break = False
		for match in matches:
			for key in match:
				if not item['item'].has_key(key) or not item['item'][key] == match[key]:
					_break = True
					break
			
			if _break:
				break
		
		if _break:
			continue
		
		_match.append(item)
	
	return _match

