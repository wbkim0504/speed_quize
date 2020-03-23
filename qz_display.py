#!/usr/bin/python

import numpy
import datetime

from random import random

from math import *
from freetype import * 

import glfw
from OpenGL.GL import *
from OpenGL.GLUT import *


# -------------------------------------------------------------------
# font
font_list = {}

rgba_box = (0.0, 0.4, 0.6, 1)
rgba_text = (0.4,0.8,0.4, 1)
rgba_gray = (0.5,0.5,0.5,1)
rgba_red = (1,0.3,0.3,1)
rgba_title = (0.6,1.0,0.6,1)

# popup display for oscilloscope
opt_display = -1
menu_list = [] 

# disp_mode
disp_mode = 0
sub_mode = 0

# operation type & level
#	type : +, -, x, %
#	level : 1 - 3
#
operation = {}
operation_type = '+'
operation_level = 1

# problem
num_problem = 10
problem = []
answer = []

# timer setting
start_time = datetime.datetime.now()
end_time = start_time


# -------------------------------------------------------------------
def makefont(filename, size):
	# Load font  and check it is monotype
	face = Face(filename)
	face.set_char_size( size*64 )
	if not face.is_fixed_width:
		raise 'Font is not monotype'

	# Determine largest glyph size
	width, height, ascender, descender = 0, 0, 0, 0
	for c in range(32,128):
		face.load_char( chr(c), FT_LOAD_RENDER | FT_LOAD_FORCE_AUTOHINT )
		bitmap    = face.glyph.bitmap
		width     = max( width, bitmap.width )
		ascender  = max( ascender, face.glyph.bitmap_top )
		descender = max( descender, bitmap.rows-face.glyph.bitmap_top )
	height = ascender+descender
	#print width, height

	# Generate texture data
	Z = numpy.zeros((height*6, width*16), dtype=numpy.ubyte)
	for j in range(6):
		for i in range(16):
			face.load_char(chr(32+j*16+i), FT_LOAD_RENDER | FT_LOAD_FORCE_AUTOHINT )
			bitmap = face.glyph.bitmap
			x = i*width  + face.glyph.bitmap_left
			y = j*height + ascender - face.glyph.bitmap_top
			Z[y:y+bitmap.rows,x:x+bitmap.width].flat = bitmap.buffer

	# Bound texture
	texid = glGenTextures(1)
	glBindTexture( GL_TEXTURE_2D, texid )
	glTexParameterf( GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR )
	glTexParameterf( GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR )
	glTexImage2D( GL_TEXTURE_2D, 0, GL_ALPHA, Z.shape[1], Z.shape[0], 0,
					 GL_ALPHA, GL_UNSIGNED_BYTE, Z )
	#print 'texid: ', texid

	# Generate display lists
	dx, dy = width/float(Z.shape[1]), height/float(Z.shape[0])
	base = glGenLists(8*16)
	#print 'base: ', base
	for i in range(8*16):
		c = chr(i)
		x = i%16
		y = i//16-2
		glNewList(base+i, GL_COMPILE)
		if (c == '\n'):
			glPopMatrix( )
			glTranslatef( 0, -height, 0 )
			glPushMatrix( )
		elif (c == '\t'):
			glTranslatef( 4*width, 0, 0 )
		elif (i >= 32):
			glBegin( GL_QUADS )
			glTexCoord2f( (x  )*dx, (y+1)*dy ), glVertex( 0,     -height )
			glTexCoord2f( (x  )*dx, (y  )*dy ), glVertex( 0,     0 )
			glTexCoord2f( (x+1)*dx, (y  )*dy ), glVertex( width, 0 )
			glTexCoord2f( (x+1)*dx, (y+1)*dy ), glVertex( width, -height )
			glEnd( )
			glTranslatef( width, 0, 0 )
		glEndList( )

	fontinfo = {'texid': texid, 'base': base}
	return fontinfo 

# -------------------------------------------------------------------
def loadfont():
	font_list['12'] = makefont( './VeraMono.ttf', 12 )
	font_list['16'] = makefont( './VeraMono.ttf', 16 )
	font_list['24'] = makefont( './VeraMono.ttf', 24 )
	font_list['32'] = makefont( './VeraMono.ttf', 32 )
	font_list['48'] = makefont( './VeraMono.ttf', 48 )
	font_list['64'] = makefont( './VeraMono.ttf', 64 )
	font_list['128'] = makefont( './VeraMono.ttf', 128 )

# -------------------------------------------------------------------
def qz_display_init():
	global menu_list, max_osc_data, osc_volt, osc_amp

	print 'qz_display_init : do nothing'

	# box pos
	'''
	x1 = [ 0.12, 0.28, 0.34, 0.48, 0.68 ]
	x2 = [ 0.22, 0.34, 0.40, 0.53, 0.76 ]
	y1 = [ 0.16, 0.44, 0.72 ]
	y2 = [ 0.28, 0.55, 0.83 ]
	'''

	# set menu_list
	'''
	pv = { 'id': 0, 'pos': (x1[0], y1[0], x2[0], y2[0]) }
	ess1 = { 'id': 1, 'pos': (x1[0], y1[1], x2[0], y2[1]) }
	ess2 = { 'id': 2, 'pos': (x1[0], y1[2], x2[0], y2[2]) }
	'''

	# add menu_list
	'''
	menu_list.append(pv)
	menu_list.append(ess1)
	menu_list.append(ess2)
	'''


def qz_display_set(x,y):
	global opt_display
	if opt_display >= 0:
		opt_display = -1
	else:	
		# check menu_list
		for menu in menu_list:
			x1, y1, x2, y2 = menu['pos']
			if x>x1 and x<x2 and y>y1 and y<y2:
				opt_display = menu['id']
				break

	print 'opt_display : %d' % (opt_display)		
	

# --------------------------------------------------------------------------
def drawLineX(x,y,length):
	glBegin(GL_LINES)
	glVertex2f(x,y)
	glVertex2f(x+length, y)
	glEnd()

def drawLineY(x,y,length):
	glBegin(GL_LINES)
	glVertex2f(x,y)
	glVertex2f(x,y+length)
	glEnd()

def drawCircle(x, y, r):
	n = 36
	glBegin(GL_LINE_LOOP)
	for i in range(n):
		phi = i*2*pi/n
		x1 = x + r * cos(phi)
		y1 = y + r * sin(phi)
		glVertex2f(x1,y1)
	glEnd()		

def drawBox(x, y, width, height):
	x2 = x + width
	y2 = y + height
	glBegin(GL_LINE_LOOP)
	glVertex2f(x,y)
	glVertex2f(x2,y)
	glVertex2f(x2,y2)
	glVertex2f(x,y2)
	glEnd()

# --------------------------------------------------------------------------
def textout(x,y,text,font_size):
	global font_list

	font_type = str(font_size)
	if font_type in font_list:
		font = font_list[font_type]
	else:
		font = font_list['12']

	glEnable( GL_TEXTURE_2D )
	glPushMatrix( )

	glBindTexture( GL_TEXTURE_2D, font['texid'] )
	glTranslate( x, y, 0)
	glListBase( font['base'] )
	glCallLists( [ord(c) for c in text] )

	glPopMatrix( )
	glDisable( GL_TEXTURE_2D )

# --------------------------------------------------------------------------
def disp_none():
	glColor(rgba_title)
	textout(540,700,'SPEED QUIZ !!',64)
	textout(580,550,'( + - x % )', 48)
	textout(540,400,'Press Enter to continue ...', 32)

def disp_setup():
	global disp_mode, sub_mode
	global operation_type, operation_level

	glColor(rgba_title)
	textout(200,700,'Operation Mode  :    +    -    x    % ',48)
	textout(200,550,'Operation level :    1    2    3 ', 48)
	textout(540,300,'Press Enter to continue ...', 32)

	# draw box for (+,-,x,%)
	x0 = 770
	y0 = 630
	dx = 100
	dy = 100

	x1 = 145

	if operation_type == '-':
		x0 += x1
	elif operation_type == 'x':
		x0 += 2*x1
	elif operation_type == '%':
		x0 += 3*x1
	glColor(rgba_red)
	drawBox(x0,y0,dx,dy)

	# draw box for (operation_level)
	x0 = 770
	y0 -= 150

	if operation_level == 2:
		x0 += x1
	elif operation_level == 3:
		x0 += 2*x1
	drawBox(x0,y0,dx,dy)

def disp_problem():
	global operation_type, problem, answer

	curr_time = datetime.datetime.now()
	dt = curr_time - start_time
	timer = 'Time : ' + str(dt.seconds) + '.' + str(dt.microseconds)

	glColor(rgba_title)
	textout(60, 850, timer ,32)

	p = problem[sub_mode]
	curr_prob = str(p[0]) + ' ' + operation_type + ' '+ str(p[1]) + ' = '
	if len(answer) > sub_mode:
		curr_prob += str(answer[sub_mode])

	textout(300, 600, curr_prob, 128)

	textout(540,300,'Press Enter to continue ...', 32)



def disp_result():
	dt = end_time - start_time
	timer = 'Total Time : ' + str(dt.seconds) + '.' + '%02d' % (dt.microseconds/10000) + ' sec'

	glColor(rgba_title)
	textout(100, 850, timer, 64)

	x0 = 300
	y0 = 750
	dy = 50

	count = 0
	for x in range(num_problem):
		p = problem[x]
		eqn = str(p[0]) + ' ' + operation_type + ' '+ str(p[1]) + ' = '
		if len(answer) > x:
			eqn += str(answer[x])
			if p[2] == answer[x]:
				count += 1
				eqn += '  (O)'
			else:
				eqn += '  (X)'
		
		textout(x0, y0, eqn, 32)
		y0 -= dy

	y0 -= dy
	res = 'Your score is %d / %d' % (count, num_problem)
	textout(100, y0, res, 64)
	

# --------------------------------------------------------------------------
def make_problem():
	global operation_type, operation_level
	global problem, answer

	if len(problem) > 0:
		del problem[:]

	if len(answer) > 0:
		del answer[:]


	for x in range(num_problem):
		if operation_level == 1:
			a = int (1 + random()*9)
			b = int (1 + random()*9)
		elif operation_level == 2:
			a = int (10 + random()*90)
			b = int (1 + random()*9)
		elif operation_level == 3:
			a = int (10 + random()*90)
			b = int (10 + random()*90)
		else:
			a = int (1 + random()*9)
			b = int (1 + random()*9)
		
		if operation_type == '+':
			c = a + b
		elif operation_type == '-':
			a1 = max(a,b)
			b1 = min(a,b)
			a = a1
			b = b1
			c = a - b
		elif operation_type == 'x':
			c = a * b
		elif operation_type == '%':
			a1 = a
			c1 = a * b
			a = c1
			c = a1
		else:
			c = a + b
		
		new_prob = [a, b, c]
		problem.append(new_prob)


# --------------------------------------------------------------------------
def on_display():
	global disp_mode
	
	#glClearColor(1,1,1,1)
	#glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
	#glClear(GL_COLOR_BUFFER_BIT)

	# main boundary
	glColor(0.5,0.5,1,1)
	drawBox(20,15,1560,870)

	curr_time = datetime.datetime.now()
	title = curr_time.strftime('%Y-%m-%d  %H:%M:%S')

	# title
	glColor(rgba_title)
	if disp_mode < 2:
		textout(40, 880, title ,32)

	# disp mode
	if disp_mode == 1:
		disp_setup()
	elif disp_mode == 2:
		disp_problem()
	elif disp_mode == 3:
		disp_result()
	else:
		disp_none()


# --------------------------------------------------------------------------
def on_key_input(key):
	global disp_mode, sub_mode
	global operation_type, operation_level
	global start_time, end_time

	if disp_mode == 0:
		if key == glfw.KEY_ENTER or key == glfw.KEY_KP_ENTER:
			disp_mode = 1
			sub_mode = 0
	# setting
	elif disp_mode == 1:
		if key >= glfw.KEY_KP_0 and key <= glfw.KEY_KP_9:
			key = key - glfw.KEY_KP_0 + glfw.KEY_0

		if key >= glfw.KEY_1 and key <= glfw.KEY_3:
			operation_level = key - glfw.KEY_0
			print 'op_level : ' + str(operation_level)
		elif key == glfw.KEY_KP_ADD:
			operation_type = '+'
		elif key == glfw.KEY_KP_SUBTRACT:
			operation_type = '-'
		elif key == glfw.KEY_KP_MULTIPLY:
			operation_type = 'x'
		elif key == glfw.KEY_KP_DIVIDE:
			operation_type = '%'
		elif key == glfw.KEY_ENTER or key == glfw.KEY_KP_ENTER:
			make_problem()
			start_time = datetime.datetime.now()
			disp_mode = 2
			sub_mode = 0
	# problem
	elif disp_mode == 2:
		if key >= glfw.KEY_KP_0 and key <= glfw.KEY_KP_9:
			key = key - glfw.KEY_KP_0 + glfw.KEY_0

		if key >= glfw.KEY_0 and key <= glfw.KEY_9:
			data = key - glfw.KEY_0
			if len(answer) > sub_mode:
				p = answer[sub_mode]
				answer[sub_mode] = p*10 + data
			else:
				if data:
					answer.append(data)
				else:
					if operation_type == '-':
						answer.append(data)
		elif key == glfw.KEY_BACKSPACE:
			if len(answer) > sub_mode:
				p = answer[sub_mode]
				p = int(p/10)
				if p > 0:
					answer[sub_mode] = p
				else:
					del answer[-1]
		elif key == glfw.KEY_ENTER or key == glfw.KEY_KP_ENTER:
			if len(answer) > sub_mode:
				sub_mode += 1
				if sub_mode >= num_problem:
					end_time = datetime.datetime.now()
					disp_mode = 3
					sub_mode = 0
	# result 
	elif disp_mode == 3:
		if key == glfw.KEY_ENTER or key == glfw.KEY_KP_ENTER:
			disp_mode = 0
			sub_mode = 0

	else:
		pass


	

