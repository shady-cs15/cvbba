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
while True:
	ret, frame = cap.read()
	if not ret:
		break
	frames.append(frame)

def trackbar_callback(arg):
	global frame_no
	frame_no = arg

cv2.namedWindow('frame')
cv2.createTrackbar('frame#','frame', 0, len(frames)-1, trackbar_callback)

rors = {}
bors = {}

accept_annot = [True]*10
frame_no = 0
obj_no = 0
obj_map = {}
	
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

	if k==ord('r') and frame_no < len(annot):
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

		# update rors
		for obj in rors:
			for rej_id in range(rors[obj][0], rors[obj][1]+1):
				annot[rej_id].pop(obj, None)

	
	if k==ord('b'):
		if frame_no > 0:
			frame_no -= 1
	if k==27:
		break
	if k==ord(' '):
		if frame_no < len(frames)-1:
			frame_no +=1
	cv2.setTrackbarPos('frame#', 'frame', frame_no)

print 'Accept modified annotations? (y/n)',
choice = raw_input()
if choice =='y':
	with open(out_annot, 'w') as outfile:
		json.dump(annot, outfile)

