from globals import *

import libtcodpy as tcod

BLANK_TILE = {'id':'blank_tile',
				'icon': '.',
				'color':(tcod.darker_gray, tcod.black)}

SHORT_GRASS_TILE = {'id':'short_grass',
					'icon':'.',
					'color':(GRASS_GREEN_DARK, tcod.desaturated_green),
					'burnable':8,
					'cost':1}

GRASS_TILE = {'id':'grass',
			  'icon':';',
			  'color':(GRASS_GREEN, tcod.desaturated_sea),
			  'burnable':7,
			  'cost':1}

TALL_GRASS_TILE = {'id':'tall_grass',
				   'icon':'\\',
				   'color':(GRASS_GREEN, tcod.desaturated_chartreuse),
				   'burnable':6,
				   'cost':1}

DIRT_TILE = {'id':'dirt',
			 'icon':'.',
			 'color':(SAND_LIGHT,SAND),
			 'burnable':False,
			 'type': 'road',
			 'cost':2}

SAND_TILE_1 = {'id':'sand_1',
			 'icon':'.',
			 'color':(SAND_LIGHT,SAND),
			 'burnable':False,
			 'cost':2}

SAND_TILE_2 = {'id':'sand_2',
			 'icon':'\\',
			 'color':(SAND,SAND_LIGHT),
			 'burnable':False,
			 'cost':2}

DIRT_TILE_1 = {'id':'dirt_1',
			 'icon':'\\',
			 'color':(BROWN_DARK,BROWN_DARK_ALT),
			 'burnable':False,
			 'type': 'road',
			 'cost':2}

DIRT_TILE_2 = {'id':'dirt_2',
			 'icon':',',
			 'color':(BROWN_DARK_ALT,BROWN_DARK),
			 'burnable':False,
			 'type': 'road',
			 'cost':2}

DIRT_TILE_3 = {'id':'dirt_3',
			 'icon':'.',
			 'color':(BROWN_DARK_ALT,BROWN_DARK_ALT_2),
			 'burnable':False,
			 'type': 'road',
			 'cost':2}

WALL_TILE = {'id':'wall',
			 'icon':'#',
			 'color':(tcod.black, tcod.dark_gray),
			 'burnable':False,
			 'type': 'building',
			 'cost':-1}

CONCRETE_TILE_1 = {'id':'concrete_1',
			 'icon':'.',
			 'color':(tcod.Color(130,130,130), tcod.Color(70,70,70)),
			 'burnable':False,
			 'type': 'road',
			 'cost':2}

CONCRETE_TILE_2 = {'id':'concrete_2',
			 'icon':'.',
			 'color':(tcod.Color(95,95,95), tcod.Color(62,62,62)),
			 'burnable':False,
			 'type': 'road',
			 'cost':2}

CONCRETE_FLOOR_1 = {'id':'concrete_floor_1',
			 'icon':'.',
			 'color':(tcod.Color(115,115,115), tcod.Color(100,100,100)),
			 'burnable':False,
			 'type': 'building',
			 'cost':2}

CONCRETE_FLOOR_2 = {'id':'concrete_floor_2',
			 'icon':'.',
			 'color':(tcod.Color(125,125,125), tcod.Color(110,110,110)),
			 'burnable':False,
			 'type': 'building',
			 'cost':2}

ROAD_STRIPE_1 = {'id':'road_stripe_1',
			 'icon':'.',
			 'color':(tcod.yellow, tcod.yellow),
			 'burnable':False,
			 'cost':2}

ROAD_STRIPE_2 = {'id':'road_stripe_2',
			 'icon':'.',
			 'color':(tcod.white, tcod.darker_gray),
			 'burnable':False,
			 'cost':2}

RED_BRICK_1 = {'id':'red_brick_1',
			 'icon':'#',
			 'color':(tcod.gray, tcod.dark_red),
			 'burnable':False,
			 'cost':-1}

RED_BRICK_2 = {'id':'red_brick_2',
			 'icon':'#',
			 'color':(tcod.light_gray, tcod.dark_red),
			 'burnable':False,
			 'cost':-1}

WHITE_TILE_1 = {'id':'white_tile_1',
			 'icon':',',
			 'color':(tcod.lightest_gray, tcod.lighter_gray),
			 'burnable':False,
			 'type': 'building',
			 'cost':-1}

WHITE_TILE_2 = {'id':'white_tile_2',
			 'icon':'.',
			 'color':(tcod.white, tcod.lightest_gray),
			 'burnable':False,
			 'type': 'building',
			 'cost':-1}

#Groups
TEMP_TILES = [BLANK_TILE,
		DIRT_TILE,
		WALL_TILE,
		ROAD_STRIPE_1,
		ROAD_STRIPE_2,
		RED_BRICK_1,
		RED_BRICK_2,
		WHITE_TILE_1,
		WHITE_TILE_2]

GRASS_TILES = [SHORT_GRASS_TILE,
		GRASS_TILE,
		TALL_GRASS_TILE]

DIRT_TILES = [DIRT_TILE_1,
			DIRT_TILE_2,
			DIRT_TILE_3]

SAND_TILES = [SAND_TILE_1,
			SAND_TILE_2]

CONCRETE_TILES = [CONCRETE_TILE_1,
			CONCRETE_TILE_2]

CONCRETE_FLOOR_TILES = [CONCRETE_FLOOR_1,
			CONCRETE_FLOOR_2]

RED_BRICK_TILES = [RED_BRICK_1,
			RED_BRICK_2]

WHITE_TILE_TILES = [WHITE_TILE_1,
			WHITE_TILE_2]

def create_all_tiles():
	TEMP_TILES.extend(GRASS_TILES)
	TEMP_TILES.extend(DIRT_TILES)
	TEMP_TILES.extend(SAND_TILES)
	TEMP_TILES.extend(CONCRETE_TILES)
	TEMP_TILES.extend(CONCRETE_FLOOR_TILES)
	TEMP_TILES.extend(RED_BRICK_TILES)
	TEMP_TILES.extend(WHITE_TILE_TILES)

	for tile in TEMP_TILES:
		TILES[tile['id']] = tile

def create_tile(tile):
	_ret_tile = {}
	_ret_tile['id'] = tile['id']

	return _ret_tile

def get_raw_tile(tile):
	return TILES[tile['id']]

def get_tile(pos):
	return WORLD_INFO['map'][pos[0]][pos[1]][pos[2]]

def flag(tile, flag, value):
	tile['flags'][flag] = value
	
	return value

def get_flag(tile, flag):
	if not flag in tile['flags']:
		return False
	
	return tile['flags'][flag]
