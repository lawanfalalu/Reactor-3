from globals import *
import tiles
import maps
import time

def generate_structure_map(source_map):
	_buildings = []
	_all_walls = []
	
	#TODO: z-levels
	for x in range(MAP_SIZE[0]):
		for y in range(MAP_SIZE[1]):
			z = 2
			
			if not source_map[x][y][z] and not source_map[x][y][z+1]:
				continue
			
			if (x,y,z+1) in _all_walls:
				continue
			
			_walls = []
			_open_walls = [(x,y,z+1)]
			while _open_walls:
				_wall_x,_wall_y,_wall_z = _open_walls.pop(0)
				
				for x_mod in range(-1,2):
					for y_mod in range(-1,2):
						if (x_mod,y_mod) == (0,0):
							continue
						
						_x = _wall_x+x_mod
						_y = _wall_y+y_mod
						
						if (_x,_y,z+1) in _all_walls:
							continue
						
						if _x>=MAP_SIZE[0] or _y>=MAP_SIZE[1]:
							continue
						
						if not source_map[_x][_y][z+1]:
							continue
						
						_walls.append((_x,_y,z+1))
						_open_walls.append((_x,_y,z+1))
						#_all_walls.append((_x,_y,z+1))
			
			_all_walls.extend(_walls)
			_buildings.append(_walls)
	
	return _buildings
			
_stime = time.time()
MAP = maps.load_map('map1.dat')
print len(generate_structure_map(MAP))
print time.time()-_stime