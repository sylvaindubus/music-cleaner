import sys
import os
from glob import glob
from mutagen.id3 import ID3, APIC
from PIL import Image

def get_cover(path):
	cover_paths = glob(os.path.join(path, '*.[jpg][jpeg]*'))

	if (len(cover_paths) == 0):
		return None

	if (len(cover_paths) == 1):
		return cover_paths[0]

	# Sort covers to get the widest one
	cover_paths.sort(key=lambda cover: Image.open(cover).size[0], reverse=True)
	
	return cover_paths[0]

if (len(sys.argv) < 2):
	print('❌ Please specify a path containing your mp3 files.')
	exit(1)

paths = glob(os.path.join(sys.argv[1], '**/*.mp3'))

if (len(paths) == 0):
	print('❌ No mp3 files found in the specified directory.')
	exit(1)

print(f'🤖 Checking file names...')
for path in paths:
	dirname = os.path.dirname(path)
	audio = ID3(path)
	artist = audio.get('TPE1')
	year = audio.get('TDRC')
	track = audio.get('TRCK')
	name = audio.get('TIT2')

	if not artist or not year or not track or not name:
		print(f'😞 Some tags are missing for {path}')
		continue

	track_number = track.text[0].split('/')[0].zfill(2)
	current_filename = os.path.basename(path)
	new_filename = f'{artist} - {year} - {track_number} - {name}.mp3'

	if (current_filename != new_filename):
		newPath = os.path.join(dirname, new_filename)
		os.rename(path, newPath)
		print(f'Rename "{current_filename}" ➡️ "{new_filename}"', )

print(f'🤖 Checking album covers...')
folder_paths = set(map(lambda path: os.path.dirname(path), paths))
for path in folder_paths:
	cover_path = get_cover(path)

	if not cover_path:
		print(f'😞 No cover found in {path}')
		continue

	correct_cover_path = os.path.join(path, 'Cover.jpg')
	if cover_path != correct_cover_path:
		os.rename(cover_path, correct_cover_path)
		print(f'Rename "{cover_path}" ➡️ "{correct_cover_path}"')

	cover_content = open(correct_cover_path, 'rb').read()
	for path in glob(os.path.join(path, '*.mp3')): 
		if (not ID3(path).getall('APIC')):
			audio.add(APIC(3, 'image/jpeg', 3, 'Cover', cover_content))
			audio.save()
			print(f'Attach cover to "{os.path.basename(path)}"')

print(f'🤖 Cleaning useless files...')
useless_file_paths = set(glob(os.path.join(sys.argv[1], '**/*'))) - set(glob(os.path.join(sys.argv[1], '**/*.mp3'))) - set(glob(os.path.join(sys.argv[1], '**/Cover.jpg')))
for path in useless_file_paths:
	os.remove(path)
	print(f'Remove "{path}"')

print('🤖 Done')
exit(0)