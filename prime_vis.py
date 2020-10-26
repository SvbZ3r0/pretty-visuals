# A number walk along primes
# Inspired by work of u/Oh_Tassos on r/dataisbeautiful
# Animation optimization by u/TiagoTiagoT 

import io
import sys
import time
import turtle
import argparse
import colorsys
import itertools
from PIL import Image

def lowpass(val, prev, bias):
	return ((val*(bias)) + (prev * (1-bias)))

def mag(x, y):
	return ((x**2)+(y**2))**0.5

def imsave():
	ps = canvas.postscript(colormode='color')
	img = Image.open(io.BytesIO(ps.encode('utf-8')))
	img.load(scale=10)
	img.save(f'./img/prime_{angle}_{n}.png', 'png')
	print(f'{n}->{prime}')

def gen_primes(end=None):
# from https://code.activestate.com/recipes/117119/#c12
	D = {}
	yield 2
	for q in itertools.islice(itertools.count(3), 0, end, 2):
		p = D.pop(q, None)
		if not p:				# if p is not previously marked as composite
			D[q * q] = 2 * q
			yield q
		else:
			x = p + q
			while x in D:
				x += p
			D[x] = p 			# mark next multiple of p as composite

def get_args():
	parser = argparse.ArgumentParser(description='Walk along prime numbers')
	parser.add_argument('-n', default=None, type=int,
						help='Stop the walk at N')
	parser.add_argument('-a', default=90, type=float,
						help='Angle to turn at primes')
	parser.add_argument('-s', action='store_true',
						help='Enable screenshot on pressing space')
	return parser.parse_args()


if __name__ == '__main__':

	args = get_args()
	end, angle, scrnshot = args.n, args.a, args.s

	t = turtle.Turtle()
	s = turtle.Screen()
	canvas = s.getcanvas()
	turtle.bgcolor('black')

	t_width, t_height = s.screensize()
	s.setworldcoordinates(-t_width/2,-t_height/2,t_width/2,t_height/2)

	t.speed(-1)
	t.ht()
	t.penup()
	t.goto(0,0)
	t.pendown()

	prev = 1

	scale = 1
	last_scale = 1
	scale_max = scale

	cam_bias = 0.000075			# affects how smoothly the camera pans
	scale_bias = 0.000075		# affects how smoothly the camera scales

	framerate = 60
	fps_target_ratio = 1

	colorcyclelength = 2**20

	x_min, x_max, y_min, y_max = 0,0,0,0
	cam_x_min, cam_x_max, cam_y_min, cam_y_max = 0,0,0,0

	if scrnshot:
		s.onkey(imsave, 'space')
		s.listen()

	last_time = time.monotonic()

	for n, prime in enumerate(gen_primes(end)):

		dist = prime - prev

		t.fd(dist)
		t.rt(angle)
		t.pencolor(colorsys.hsv_to_rgb((n % colorcyclelength)/colorcyclelength,1,1))
		prev = prime

		x_curr, y_curr = t.pos()
		x_min = min(x_min, x_curr)
		x_max = max(x_max, x_curr)
		y_min = min(y_min, y_curr)
		y_max = max(y_max, y_curr)

		cam_x_min = cam_x_min - ((cam_x_min - lowpass(x_min/2, cam_x_min, cam_bias)) * fps_target_ratio)
		cam_x_max = cam_x_max - ((cam_x_max - lowpass(x_max/2, cam_x_max, cam_bias)) * fps_target_ratio)
		cam_y_min = cam_y_min - ((cam_y_min - lowpass(y_min/2, cam_y_min, cam_bias)) * fps_target_ratio)
		cam_y_max = cam_y_max - ((cam_y_max - lowpass(y_max/2, cam_y_max, cam_bias)) * fps_target_ratio)

		scale_max = max(scale_max, mag(x_max-x_min, y_max-y_min) / 2)
		scale = lowpass(scale_max, scale, scale_bias * fps_target_ratio)

		curr_time = time.monotonic()

		if(curr_time - last_time >= 1/framerate):
			if((scale-last_scale)/scale > 0.001):
				s.setworldcoordinates(-scale+(cam_x_min+cam_x_max),-scale+(cam_y_min+cam_y_max), scale+(cam_x_min+cam_x_max), scale+(cam_y_min+cam_y_max))
				last_scale = scale
			else:
				turtle.update()
			turtle.tracer(n=0,delay=0)
			fps_target_ratio = ((curr_time - last_time) * framerate)
			last_time = curr_time

	imsave()