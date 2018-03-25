import json
import sys
import cv2
import numpy as np

video = sys.argv[1]
annot = json.load(open(sys.argv[2]))

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
cv2.createTrackbar('frame#','frame', 0, len(frames), trackbar_callback)

accept_annot = [True]*10
frame_no = 0
while frame_no < len(frames):
	frame = frames[frame_no].copy()
	cur_objs = annot[frame_no].keys()

	obj_no = 0
	obj_map = {}
	for cur_obj in annot[frame_no]:
		obj_map[cur_obj] = obj_no
		if accept_annot[obj_no]==True:
			cur_box = annot[frame_no][cur_obj]
			pt1 = [int(cur_box['x']), int(cur_box['y'])]
			pt2 = [int(cur_box['x'] + cur_box['w']), int(cur_box['y'] + cur_box['h'])]
			cv2.rectangle(frame, tuple(pt1), tuple(pt2), color_map[obj_map[cur_obj]], 2)
		obj_no += 1			

	cv2.imshow('frame', frame)
	k = cv2.waitKey(0)
	if k==ord('a'):
		for cur_obj in annot[frame_no]:
			print 'frame:', frame_no, 'accept annotations for', cur_obj, '? (y/n)',
			choice = raw_input()
			if choice =='n':
				accept_annot[obj_map[cur_obj]] = False
			if choice == 'y':
				accept_annot[obj_map[cur_obj]] = True
	
	if k==ord('b'):
		if frame_no > 0:
			frame_no -= 1
	if k==27:
		break
	if k==ord(' '):
		frame_no +=1
	cv2.setTrackbarPos('frame#', 'frame', frame_no)

