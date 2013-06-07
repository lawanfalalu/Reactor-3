from globals import *

import graphics as gfx
import scripting
import drawing
import logging
import numbers
import maps
import life

try:
	import ujson as json
except:
	import json

def load_item(item):
	with open(os.path.join(ITEM_DIR,item+'.json'),'r') as e:
		try:
			return json.loads(''.join(e.readlines()))
		except ValueError,e:
			raise Exception('Failed to load item: %s' % e)

def initiate_item(name):
	"""Loads (and returns) new item type into memory."""
	if name in ITEM_TYPES:
		logging.warning('Item type \'%s\' is already loaded. Reloading...' % name)
	
	item = load_item(name)
	_marked_for_reint = {}
	
	if not 'prefix' in item:
		logging.warning('No prefix set for item type \'%s\'. Using default (%s).' % (name, DEFAULT_ITEM_PREFIX))
		item['prefix'] = DEFAULT_ITEM_PREFIX
	
	if not 'icon' in item:
		logging.warning('No icon set for item type \'%s\'. Using default (%s).' % (name, DEFAULT_ITEM_ICON))
		item['tile'] = DEFAULT_ITEM_ICON
	
	if not 'flags' in item:
		logging.error('No flags set for item type \'%s\'. Errors may occur.' % name)
		item['flags'] = ''
	
	if 'attaches_to' in item:
		item['attaches_to'] = item['attaches_to'].split('|')
	
	if 'capacity' in item:
		item['max_capacity'] = [int(c) for c in item['capacity'].split('x')]
		item['max_capacity'] = item['max_capacity'][0]*item['max_capacity'][1]
		item['capacity'] = 0
		item['storing'] = []
	
	if not 'size' in item:
		logging.warning('No size set for item type \'%s\'. Using default (%s).' % (name, DEFAULT_ITEM_SIZE))
		item['size'] = DEFAULT_ITEM_SIZE
	
	if item['type'] == 'gun':
		item[item['feed']] = None
	
	#item['flags'] = []
	_flags = {}
	for flag in item['flags'].split('|'):
		if '=' in flag:
			_flag_split = flag.split('=')
			_flags[_flag_split[0]] = None
			
			if len(_flag_split)==2:
				_flags[_flag_split[0]] = _flag_split[1]
		elif '[' in flag:
			_ocount = flag.count('[')
			_ccount = flag.count(']')
			
			if _ocount > _ccount:
				logging.error('Brace mismatch in item \'%s\': Expected \']\'' % name)
				continue
			elif _ocount < _ccount:
				logging.error('Brace mismatch in item \'%s\': Expected \'[\'' % name)
				continue
			
			_flags[flag.split('[')[0]] = scripting.initiate(item, flag)
		else:
			_flags[flag] = None
	
	item['flags'] = _flags
	item['size'] = 	[int(c) for c in item['size'].split('x')]
	item['size'] = item['size'][0]*item['size'][1]
	
	for key in item:
		if isinstance(item[key],list):
			_marked_for_reint[key] = item[key][:]
	
	item['marked_for_reint'] = _marked_for_reint.copy()
	
	#Unicode isn't handled all that well on Windows for some reason...
	for key in item:
		_value = item[key]
		del item[key]
		item[str(key)] = _value
		
		if isinstance(item[key],unicode):
			item[key] = str(item[key])
	
	ITEM_TYPES[item['name']] = item
	
	return item

def create_item(name,position=[0,0,2]):
	"""Initiates and returns a copy of an item type."""
	item = ITEM_TYPES[name].copy()
	
	for key in item['marked_for_reint']:
		item[key] = item['marked_for_reint'][key][:]
	
	del item['marked_for_reint']

	item['uid'] = len(ITEMS)
	item['pos'] = list(position)
	item['realpos'] = list(position)
	item['velocity'] = [0,0,0]
	item['friction'] = 0
	item['gravity'] = SETTINGS['world gravity']
	item['lock'] = None
	
	if 'speed' in item:
		item['max_speed'] = item['speed']
	else:
		item['max_speed'] = 2
	
	ITEMS[item['uid']] = item
	
	return item

def delete_item(item):
	logging.debug('Deleting references to item %s' % item['uid'])
	
	for life in [LIFE[i] for i in LIFE]:
		if item['uid'] in life['know_items']:
			logging.debug('\tDeleted reference in life #%s' % life['id'])
			
			del life['know_items'][item['uid']]
	
	del ITEMS[item['uid']]

def get_item_from_uid(uid):
	"""Helper function. Returns item of `uid`."""
	return ITEMS[uid]

def get_items_at(position):
	"""Returns list of all items at a given position."""
	_items = []
	
	for _item in ITEMS:
		item = ITEMS[_item]
		
		if item.has_key('id'):
			continue
		
		if item.has_key('parent'):
			continue
		
		if item['pos'] == position:
			_items.append(item)
	
	return _items

def get_name(item):
	"""Returns the full name of an item."""
	return '%s %s' % (item['prefix'],item['name'])		

def move(item,direction,speed,friction=0.05,_velocity=0):
	"""Sets new velocity for an item. Returns nothing."""
	velocity = numbers.velocity(direction,speed)
	velocity[2] = _velocity
	
	#TODO: We have 30 frames per second. Any formula for finding speeds using that?
	item['friction'] = friction
	item['velocity'] = velocity
	item['realpos'] = item['pos'][:]
	
	logging.debug('%s flies off in an arc!' % get_name(item))

def draw_items():
	for _item in ITEMS:
		item = ITEMS[_item]
		
		if item.has_key('id'):
			continue
		
		if item.has_key('parent'):
			continue
		
		if item['pos'][0] >= CAMERA_POS[0] and item['pos'][0] < CAMERA_POS[0]+MAP_WINDOW_SIZE[0] and\
			item['pos'][1] >= CAMERA_POS[1] and item['pos'][1] < CAMERA_POS[1]+MAP_WINDOW_SIZE[1]:
			_x = item['pos'][0] - CAMERA_POS[0]
			_y = item['pos'][1] - CAMERA_POS[1]
		
			if not LOS_BUFFER[0][_y,_x]:
				continue
			
			gfx.blit_char(_x,
				_y,
				item['icon'],
				tcod.white,
				None,
				char_buffer=MAP_CHAR_BUFFER,
				rgb_fore_buffer=MAP_RGB_FORE_BUFFER,
				rgb_back_buffer=MAP_RGB_BACK_BUFFER)

def tick_all_items(MAP):
	_remove = []
	
	for _item in ITEMS:
		item = ITEMS[_item]
		
		if item['velocity'] == [0,0,0]:
			continue
		
		item['realpos'][0] += item['velocity'][0]
		item['realpos'][1] += item['velocity'][1]
		_break = False
		
		for pos in drawing.diag_line(item['pos'],(int(item['realpos'][0]),int(item['realpos'][1]))):
			if not item['type'] == 'bullet':
				item['realpos'][2] += item['velocity'][2]
				item['velocity'][2] -= item['gravity']
			
			if 0>pos[0] or pos[0]>=MAP_SIZE[0] or 0>pos[1] or pos[1]>=MAP_SIZE[1]:
				logging.warning('Item OOM: %s', item['uid'])
				_remove.append(item['uid'])
				break
			
			if item['type'] == 'bullet':
				for _life in [LIFE[i] for i in LIFE]:
					if _life['id'] == item['owner']:
						continue
					
					if _life['pos'][0] == pos[0] and _life['pos'][1] == pos[1] and _life['pos'][2] == int(round(item['realpos'][2])):
						item['pos'] = [pos[0],pos[1],_life['pos'][2]]
						life.damage_from_item(_life,item,60)
						_break = True
						
						_remove.append(item['uid'])
						break
				
			if _break:
				break
			
			if MAP[pos[0]][pos[1]][int(round(item['realpos'][2]))+1]:
				item['velocity'][0] = 0
				item['velocity'][1] = 0
				item['velocity'][2] = 0
				item['pos'] = [pos[0],pos[1],item['pos'][2]-1]
				#print 'LANDED',item['pos']				
				_break = True
				break
		
		if _break:
			item['pos'][0] = int(pos[0])
			item['pos'][1] = int(pos[1])
			item['pos'][2] = int(round(item['realpos'][2]))
			print int(round(item['realpos'][2]))
		else:
			item['pos'][0] = int(round(item['realpos'][0]))
			item['pos'][1] = int(round(item['realpos'][1]))
			item['pos'][2] = int(round(item['realpos'][2]))

		if item['pos'][0] < 0 or item['pos'][0] > MAP_SIZE[0] \
			or item['pos'][1] < 0 or item['pos'][1] > MAP_SIZE[1]:
			if not item['uid'] in _remove:
				_remove.append(item['uid'])
				continue
		elif _break:
			maps.refresh_chunk(life.get_current_chunk_id(item))
			continue

		#TODO: Min/max
		item['velocity'][0] -= (item['velocity'][0]*item['gravity'])
		item['velocity'][1] -= (item['velocity'][1]*item['gravity'])
	
	for _id in _remove:
		delete_item(ITEMS[_id])

def tick_all_items_old(MAP):
	for _item in ITEMS:
		item = ITEMS[_item]
		
		if not item['velocity'].count(0)==3:
			#if item['velocity'][0]:
			item['realpos'][0]+=item['velocity'][0]
			item['realpos'][1]+=item['velocity'][1]
			item['realpos'][2]+=item['velocity'][2]
			
			item['velocity'][2] -= item['gravity']
			
			_nx = int(round(item['realpos'][0]))
			_ny = int(round(item['realpos'][1]))
			_nz = int(round(item['realpos'][2]))
			
			item['velocity'][2] -= item['gravity']

			#Collisions
			if MAP[_nx][item['pos'][1]][_nz]:
				item['velocity'][0] = -(item['velocity'][0]/float(2))
				_nx = item['pos'][0]
				
			if MAP[item['pos'][0]][_ny][_nz]:
				item['velocity'][1] = -(item['velocity'][1]/float(2))
				_ny = item['pos'][1]
			
			if MAP[item['pos'][0]][item['pos'][1]][_nz]:
				#If we're touching the ceiling...
				if _nz > item['pos'][2]:
					item['velocity'][2] = -(item['velocity'][2]/float(2))
					_nz = item['pos'][2]
					print 'DEBUG: Touching ceiling'
				else:
					item['velocity'][2] = 0
					item['gravity'] = 0
					print 'DEBUG: Touching floor'
				
					#TODO: We can handle bouncing here
					item['velocity'][0] = item['velocity'][0]/float(2)
					item['velocity'][1] = item['velocity'][1]/float(2)
			else:
				item['gravity'] = 0.1
				
			item['pos'] = [_nx,_ny,_nz]
			
			if not item['velocity'][2]:
				for i in range(0,2):
					if item['velocity'][i]>0:
						item['velocity'][i]-=item['friction']
						
						if item['velocity'][i]<0:
							item['velocity'][i]=0
						
					elif item['velocity'][i]<0:
						item['velocity'][i]+=item['friction']
						
						if item['velocity'][i]>0:
							item['velocity'][i]=0
			
			if item['velocity'].count(0)==3:
				logging.debug('%s comes to a rest at %s,%s,%s.' %
					(get_name(item),item['pos'][0],item['pos'][1],item['pos'][2]))
