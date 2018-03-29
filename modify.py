import json
import sys
import cv2
import numpy as np

video = sys.argv[1]
annot = json.load(open(sys.argv[2]))
out_annot = sys.argv[3]

color_map = [(0, 255, 0),(0, 0, 255), (255, 0, 0)]

cap = cv2.VideoCapture(video)
if cap.isOpened():
	print 'video file loaded!'

frames = []
frame = None 

while True:
	ret, frame = cap.read()
	if not ret:
		break
	frames.append(frame)

print len(frames), len(annot)

def trackbar_callback(arg):
	global frame_no
	frame_no = arg

drawing = False
ix,iy = -1,-1
edit_obj = None

updates = {}

def interpolate(cur_idx, cur_obj):
	next_idx = cur_idx
	prev_idx = cur_idx
	
	for i in range(cur_idx+1, len(frames)):
		if cur_obj in annot[i]:
			next_idx = i
			break
	if next_idx < cur_idx + 5:
		delta = next_idx-cur_idx
		delta_x = annot[next_idx][cur_obj]['x']-annot[cur_idx][cur_obj]['x']
		delta_y = annot[next_idx][cur_obj]['y']-annot[cur_idx][cur_obj]['y']
		delta_w = annot[next_idx][cur_obj]['w']-annot[cur_idx][cur_obj]['w']
		delta_h = annot[next_idx][cur_obj]['h']-annot[cur_idx][cur_obj]['h']
		for i in range(cur_idx+1, next_idx):
			cur_delta = i - cur_idx
			cur_box = {}
			del_x = cur_delta*(delta_x)/delta
			del_y = cur_delta*(delta_y)/delta
			del_w = cur_delta*(delta_w)/delta
			del_h = cur_delta*(delta_h)/delta
			cur_box['x'] = annot[cur_idx][cur_obj]['x'] + del_x
			cur_box['y'] = annot[cur_idx][cur_obj]['y'] + del_y
			cur_box['w'] = annot[cur_idx][cur_obj]['w'] + del_w
			cur_box['h'] = annot[cur_idx][cur_obj]['h'] + del_h
			annot[i][cur_obj] = cur_box		
		

	for i in range(cur_idx-1, -1, -1):
		if cur_obj in annot[i]:
			prev_idx = i
			break
	delta = cur_idx-prev_idx
	delta_x = annot[cur_idx][cur_obj]['x']-annot[prev_idx][cur_obj]['x']
	delta_y = annot[cur_idx][cur_obj]['y']-annot[prev_idx][cur_obj]['y']
	delta_w = annot[cur_idx][cur_obj]['w']-annot[prev_idx][cur_obj]['w']
	delta_h = annot[cur_idx][cur_obj]['h']-annot[prev_idx][cur_obj]['h']
	for i in range(prev_idx+1, cur_idx):
		cur_delta = i - prev_idx
		cur_box = {}
		del_x = cur_delta*(delta_x)/delta
		del_y = cur_delta*(delta_y)/delta
		del_w = cur_delta*(delta_w)/delta
		del_h = cur_delta*(delta_h)/delta
		cur_box['x'] = annot[prev_idx][cur_obj]['x'] + del_x
		cur_box['y'] = annot[prev_idx][cur_obj]['y'] + del_y
		cur_box['w'] = annot[prev_idx][cur_obj]['w'] + del_w
		cur_box['h'] = annot[prev_idx][cur_obj]['h'] + del_h
		annot[i][cur_obj] = cur_box				

mouse_pressed = False

def draw_rect(event,x,y,flags,param):
    global ix,iy,drawing, mouse_pressed, frame

    if event == cv2.EVENT_LBUTTONDOWN and drawing is True:
        ix,iy = x,y
        mouse_pressed = True

    elif event == cv2.EVENT_MOUSEMOVE and drawing is True and mouse_pressed is True:
    	framec = frame.copy()
    	framec2 = frame.copy()
    	cv2.rectangle(framec,(ix,iy),(x,y),(0,255,255),-1)
    	framec2 = cv2.addWeighted(framec, 0.3, framec2, 0.7, 0, framec2)
    	cv2.imshow('frame', framec2)

    elif event == cv2.EVENT_LBUTTONUP and drawing is True:
        drawing = False
        cv2.rectangle(frame,(ix,iy),(x,y),(0,255,255),2)
        updates[edit_obj] =(min(ix, x), min(iy, y), abs(ix-x), abs(iy-y))
        print "press 'a' to accept"
        mouse_pressed = False 
  
    #cv2.imshow('frame', frame)
        
cv2.namedWindow('frame')
cv2.createTrackbar('frame#','frame', 0, len(frames)-1, trackbar_callback)
cv2.setMouseCallback('frame', draw_rect)

rors = {}
bors = {}

accept_annot = [True]*10
frame_no = 0
obj_no = 0
obj_map = {}
rej_tog = False
	
while frame_no < len(frames):
	frame = frames[frame_no].copy()
	cur_objs = annot[frame_no].keys()

	for cur_obj in annot[frame_no]:
		if cur_obj not in obj_map:
			obj_map[cur_obj] = obj_no
			obj_no +=1

		# create entry in rors
		if cur_obj not in rors:
			rors[cur_obj]=(-1, -1)

		if accept_annot[obj_no]==True:
			cur_box = annot[frame_no][cur_obj]
			pt1 = [int(cur_box['x']), int(cur_box['y'])]
			pt2 = [int(cur_box['x'] + cur_box['w']), int(cur_box['y'] + cur_box['h'])]
			cv2.rectangle(frame, tuple(pt1), tuple(pt2), color_map[obj_map[cur_obj]], 2)

	cv2.imshow('frame', frame)
	k = cv2.waitKey(0)

	if k==ord('e'):
		if edit_obj is not None:
			print 'frame #:', frame_no, ',',
			drawing = True
		else:
			print 'first press "c" choose object'
	if k==ord('h'):
		print '-'*len('Key bindings')
		print 'Key bindings'
		print '-'*len('Key bindings')
		print 'r: remove/delete a region of annotation (start -> end)'
		print 'e: edit/modify annotation, interpolates from the previous annotated frame'
		print 's: quick save annotations to file'
		print 'c: chose/change object to be annotated'
		print 'space: move forward'
		print 'b: move backward'
		print 'esc: close'

	if k==ord('c'):
		if len(obj_map.keys())>0:
			print 'index of obj to be annotated'
			for i in range(len(obj_map.keys())):
				print i, ':', obj_map.keys()[i]
			choice = int(raw_input())
			if choice in obj_map.values():
				edit_obj = obj_map.keys()[choice]
				print 'object chosen to edit:', edit_obj

	if k==ord('a'):
		for obj in updates:
			cur_dim = {}
			cur_dim['x'], cur_dim['y'], cur_dim['w'], cur_dim['h'] = updates[obj]
			annot[frame_no][obj] = cur_dim
			interpolate(frame_no, obj)
		updates = {}
			

	if k==ord('r') and frame_no < len(annot):
		'''
		for cur_obj in annot[frame_no]:
			print 'frame:', frame_no, 'reject annotations for', cur_obj, '? (y/n)',
			choice = raw_input()
			if choice =='y':
				if accept_annot[obj_map[cur_obj]] is True:
					bors[cur_obj] = frame_no
					accept_annot[obj_map[cur_obj]] = False
			if choice == 'n':
				if accept_annot[obj_map[cur_obj]] is False:
					print 'rejection region:', bors[cur_obj], '->', frame_no
					accept_annot[obj_map[cur_obj]] = True
					rors[cur_obj]=(bors[cur_obj], frame_no)
		'''
		if edit_obj is None:
			print "press 'c' to choose object first"
		else:
			rej_tog = not rej_tog
			if rej_tog is True:
				print 'frame:', frame_no, 'start reject annotations for', edit_obj
				if accept_annot[obj_map[edit_obj]] is True:
					bors[edit_obj] = frame_no
					accept_annot[obj_map[edit_obj]] = False
			else:
				if accept_annot[obj_map[edit_obj]] is False:
					print 'rejection region:', bors[edit_obj], '->', frame_no
					accept_annot[obj_map[edit_obj]] = True
					rors[edit_obj]=(bors[edit_obj], frame_no)

			# update rors
			for obj in rors:
				for rej_id in range(rors[obj][0], rors[obj][1]+1):
					annot[rej_id].pop(obj, None)
				rors[obj] = (-1, -1)

	if k==ord('s'):
		with open(out_annot, 'w') as outfile:
			json.dump(annot, outfile)
		print 'annotations dumped into', outfile

	if k==ord('b'):
		if frame_no > 0:
			frame_no -= 1

	if k==27:
		break

	if k==ord(' '):
		if frame_no < len(frames)-1:
			frame_no +=1

	cv2.setTrackbarPos('frame#', 'frame', frame_no)

print 'save modified annotations? (y/n)',
choice = raw_input()
if choice =='y':
	with open(out_annot, 'w') as outfile:
		json.dump(annot, outfile)

