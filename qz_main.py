#!/usr/bin/python

import glfw
from OpenGL.GL import *

from qz_display import *

def on_reshape( window, width, height ):
	glViewport( 0, 0, width, height )
	glMatrixMode( GL_PROJECTION )
	glLoadIdentity( )
	#glOrtho( 0, width, 0, height, -1, 1 )
	glOrtho( 0, 1600, 0, 900, -1, 1 )
	glMatrixMode( GL_MODELVIEW )
	glLoadIdentity( )
	print width, height

def on_key( window, key, scancode, action, mods):
	if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
		glfw.set_window_should_close(window,1)
	elif action == glfw.PRESS:
		on_key_input(key)

def on_cursor_pos( window, xpos, ypos ):
	print xpos, ypos

def on_cursor_enter( window, entered ):
	if (entered):
		print 'cursor entered '
	else:
		print 'cursor left '

def on_mouse( window, button, action, mods):
	if (button == glfw.MOUSE_BUTTON_LEFT and action == glfw.PRESS):
		print 'mouse pressed '
	if (button == glfw.MOUSE_BUTTON_LEFT and action == glfw.RELEASE):
		x,y = glfw.get_cursor_pos(window)
		w,h = glfw.get_window_size(window)
		print 'mouse released ', (format(x/w, '.4f'), format(y/h, '.4f'))
		qz_display_set(x/w, y/h)

def main():
	qz_display_init()

	width = 1200
	height = 675

	# Initialize the library
	if not glfw.init():
		return
	# Create a windowed mode window and its OpenGL context
	window = glfw.create_window(width, height, 'SPEED QUIZ', None, None)
	if not window:
		glfw.terminate()
		return

	# Make the window's context current
	glfw.make_context_current(window)

	# register callback functions
	glfw.set_window_size_callback(window, on_reshape)
	glfw.set_key_callback(window, on_key)
	glfw.set_mouse_button_callback(window, on_mouse)
	#glfw.set_cursor_pos_callback(window, on_cursor_pos)
	glfw.set_cursor_enter_callback(window, on_cursor_enter)

	# init gl environment
	'''
	glTexEnvf( GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE )
	glColorMaterial( GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE )
	glEnable( GL_DEPTH_TEST )
	glEnable( GL_COLOR_MATERIAL )
	'''
	glBlendFunc( GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA )
	glEnable( GL_BLEND )

	on_reshape(window, width, height)
	#on_reshape(window, 1200, 675)

	# make freetype font
	loadfont()

	#gluPerspective(30, (640./480.), 0.5, 10.0)
	#glTranslate(0.0, 0.0, -7)

	timer_sec = 5.0	
	countdown = timer_sec
	prev_time = glfw.get_time()

	# Loop until the user closes the window
	while not glfw.window_should_close(window):
		# Render here, e.g. using pyOpenGL
		#glRotatef(0.5,3,1,1)
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
		on_display()

		# Swap front and back buffers
		glfw.swap_buffers(window)

		# Poll for and process events
		glfw.poll_events()
		
		# check timer
		'''
		curr_time = glfw.get_time()
		dt = curr_time - prev_time
		if (dt.totalcountdown <= 0.):
			print 'timer called : ', countdown
			countdown += timer_sec
		'''

	glfw.ternimate()


if __name__ == '__main__':
	main()


