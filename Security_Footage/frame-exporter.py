with open('tcp-stream.raw', 'rb') as f:
	data = f.read()

parts = data.split(b'--BoundaryString')

for i, part in enumerate(parts):
	if b'JFIF' in part:
		jpg_start = part.find(b'\xFF\xD8')
		jpg_end = part.rfind(b'\xFF\xD9') + 2

		if jpg_start != -1 and jpg_end != -1:
			jpg_data = part[jpg_start:jpg_end]
			with open(f'./exported-imgs/frame_{i}.jpg','wb') as img:
				img.write(jpg_data)


