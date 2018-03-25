import cv2
import sys
import json

video = sys.argv[1]
n_objects = len(json.load(open(sys.argv[2])))
annots = []

data = json.load(open(sys.argv[2]))
obj_types = [data[i]['type'] for i in range(n_objects)]

for i in range(n_objects):
	annots.append(data[i]['keyframes'])

boxes = [{}]*n_objects
keyframes = [[]]*n_objects

for k in range(n_objects):
	annot = annots[k]
	cur_boxes = {}
	for i in range(len(annot)):
		cur_dim = annot[i]
		frame_id = cur_dim['frame']
		pt1 = [int(cur_dim['x']), int(cur_dim['y'])]
		pt2 = [int(cur_dim['w']+cur_dim['x']), int(cur_dim['h']+ cur_dim['y'])]
		cur_boxes[frame_id] = [pt1, pt2]
	boxes[k] = cur_boxes
	keyframes[k] = sorted(boxes[k].keys())

cap = cv2.VideoCapture(video)
if cap.isOpened():
	print 'video file loaded!'

scale = 29.97

interpolated_boxes = [{}]*n_objects
for k in range(0, n_objects):
	cur_boxes = {}
	for i in range(len(keyframes[k])-1):
		cur_keyframe = int(keyframes[k][i]*scale)
		next_keyframe = int(keyframes[k][i+1]*scale)
		interval = next_keyframe - cur_keyframe
		for frame in range(cur_keyframe, next_keyframe):
			cur_interval = frame - cur_keyframe
			change_scale = (cur_interval*1.)/interval
			cur_box = [[0., 0.], [0., 0.]]
			for p in range(2):
				for q in range(2):
					cur_box[p][q] = int(boxes[k][keyframes[k][i]][p][q] + change_scale*\
					(boxes[k][keyframes[k][i+1]][p][q]-boxes[k][keyframes[k][i]][p][q]))
			cur_boxes[frame] = cur_box
	interpolated_boxes[k] = cur_boxes

annot_index = [0]*n_objects
frame_index = [0]*n_objects
color_map = [(0, 255, 0),(0, 0, 255), (255, 0, 0)]

output = []
frame_no = 0
while True:
	ret, frame = cap.read()
	cur_boxes = {}
	if not ret:
		break

	for k in range(n_objects):
		if annot_index[k] in interpolated_boxes[k]:
			pt1, pt2 = interpolated_boxes[k][annot_index[k]]
			cv2.rectangle(frame, tuple(pt1), tuple(pt2), color_map[k], 2)
			cur_box = {}
			cur_box['x'] = pt1[0]; cur_box['y'] = pt1[1];
			cur_box['w'] = pt2[0]-pt1[0]; cur_box['h'] = pt2[1]-pt1[1];
			cur_boxes[obj_types[k]]=cur_box
		if annot_index[k]<(len(interpolated_boxes[k])-1):
			annot_index[k]+=1

	output.append(cur_boxes)
	cv2.putText(frame, str(frame_no), (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0))	
	cv2.imshow('frame', frame)
	k = cv2.waitKey(20)
	if k==27:
		break
	frame_no +=1

#output = json.dumps(output, indent=4)
with open(sys.argv[2][-9:], 'w') as outfile:
	json.dump(output, outfile)