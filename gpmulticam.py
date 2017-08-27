#!/usr/bin/env python3

# gphoto2 MultiCam Tethering Utility
# https://github.com/acropup/gphoto2-MultiCam-Tethering/
# Requires gphoto2 (linux-only): http://gphoto.org/doc/manual/using-gphoto2.html

import re
import os
import subprocess #https://docs.python.org/3/library/subprocess.html

cameras = []
name_ind = 0
port_ind = 1

filename_format = '{0} - {1}.jpg' #0 is filename, 1 is camera name

#TODO: notes for how to use subprocess
# p = subprocess.run(['dir', '/p'], shell=True, stdout=subprocess.PIPE, universal_newlines=True)
# p = subprocess.run(['xdg-open', picfilename.jpg], shell=True, stdout=subprocess.PIPE, universal_newlines=True)

# p= subprocess.Popen('ping google.com /t', shell=True, stdout=subprocess.PIPE, universal_newlines=True)
# p.stdout.readline()

def main():
  print('Welcome to Better Way Camera Tethering')
  initCameras()
  while(True):
    cmd = input('{} > '.format(os.getcwd())).strip()
    if (not processCommand(cmd)):
      break

def queryCameras():
  "queries for connected cameras, and returns an array of their port mappings"
  p = subprocess.run(['gphoto2', '--auto-detect'], shell=True, stdout=subprocess.PIPE, universal_newlines=True)
  # p.stdout should return something like this:
  # Model                          Port                                             
  # ----------------------------------------------------------
  # Canon PowerShot G2             usb:001,014
  # Canon PowerShot G2             usb:001,023
  if p.returncode == 0:
    r = re.compile(r'^(.*?)   +(usb:\S*)\s', re.MULTILINE)
    matches = r.findall(p.stdout)
    #tuples are immutable, so convert list of tuples to list of lists (so we can edit the name later)
    matches = [list(elem) for elem in matches]
    return True, matches
  return False, []

def listCameras():
  id_width = 4
  name_width = 2 + max([len(c[name_ind]) for c in cameras])
  print('{}{}{}'.format('ID'.ljust(id_width), 'Name'.ljust(name_width), 'Port'))
  for i,c in enumerate(cameras):
    print('{}{}({})'.format((str(i)+':').ljust(id_width), c[name_ind].ljust(name_width), c[port_ind]))

def renameCameras():
  "Lets the user rename each camera. Takes a picture with each camera sequentially, to identify which camera it is."
  print('''The camera name is part of the filename for
  all pictures taken with it.
Choose a different name for every camera.
''')
  for i,c in enumerate(cameras):
    name = ''
    print('Taking a picture with camera {}! '.format(i))
    takePicture(c[port_ind], 'test.jpg')
    openPicture('test.jpg')
    while(len(name) == 0):
      name = input('Enter name for camera {}: '.format(i))
    c[name_ind] = name
  print('All cameras have been named!')

def initCameras():
  global cameras
  success, result = queryCameras()
  if (not success):
    print('Query Camera failed! Make sure gphoto2 is installed.')
    return
  if (len(result) == 0):
    print('No cameras found! Make sure that cameras are connected by USB and powered on.')
    print('If camera is accessible as an external drive, you may have to "Eject..." it.')
    return
  cameras = result
  print(len(cameras), 'cameras found:')
  print()
  listCameras()
  print()
  renameCameras()
  print()
  listCameras()

def openPicture(filename):
  if (os.path.exists(filename)):
    #This should open the image using the default image viewer
    subprocess.run(['xdg-open', filename], shell=True, stdout=subprocess.PIPE, universal_newlines=True)
  else:
    print('Could not open "{}"'.format(filename))

def takePicture(port, filename):
  cmd_params = ['gphoto2', '--port', port, '--capture-image-and-download', '--force-overwrite', '--filename', filename]
  subprocess.run(cmd_params, shell=True)

def takePictures(subject):
  procs = []
  if (not cameras):
    print('There are no cameras connected. Use fc command to find cameras.')
    return
  for c in cameras:
    filename = filename_format.format(subject, c[name_ind])
    if (os.path.exists(filename)):
      if (not input_yn('File with same name already exists. Overwrite?')):
        print('Aborting capture sequence. File already exists:\n{}'.format(os.path.abspath(filename)))
        return
    cmd_params = ['gphoto2', '--port', c[port_ind], '--capture-image-and-download', '--force-overwrite', '--filename', os.path.abspath(filename)]
    cmd = ' '.join(cmd_params)
    print(cmd)
    subprocess.run(cmd_params, shell=True)
    openPicture(filename)
#TODO: if we need to run these in parallel, use Popen
#    procs += subprocess.Popen(cmd_params, shell=True, stdout=subprocess.PIPE, universal_newlines=True)
#  procs[0].communicate()
#  status = p.returncode
#  output = p.stdout

def processCommand(cmd):
  global filename_format
  if (cmd == ''):
    print('''Commands:
  fc - find cameras
  cn - camera names
  ff - filename format (ex. "{0} - {1}.jpg")
  cd - change directory
  ls - list directory contents
  q  - quit

Photo capture:
  Anything more than 3 letters is considered a photo shot name, 
  and will trigger photo capture for the cameras.''')
  
  if (len(cmd) < 3 or cmd[2] == ' '):
    c = cmd[0:2]
    param = cmd[3:]
    
    if (c == 'q'):        #Quit
      if (input_yn('Are you sure you want to quit?')):
        print('Quitting...')
        return False
        
    elif (c == 'fc'):  #Find cameras
      if (cameras):
        print('Current camera list:')
        print()
        listCameras()
        print()
        if (input_yn('Search for cameras?')):
          initCameras()
      else:
        initCameras()
        
    elif (c == 'cn'):  #Camera names
      if (cameras):
        print('Current camera list:')
        print()
        listCameras()
        print()
        if (input_yn('Rename all cameras?')):
          renameCameras()
      else:
        print('There are no cameras to name. Use fc command to find cameras.')
    
    elif (c == 'ff'):  #Change filename format
      print('Filename format: "{}"'.format(filename_format))
      if (not param):
        print('{0} for shot name, and {1} for camera name')
        param = input('Set to: ')
      if (param):
        filename_format = param
        print('Filename format: "{}"'.format(filename_format))
      else:
        print('No change')
        
    elif (c == 'cd'):  #Change directory
      if (not param):
        param = input('Change directory to: ')
      if (param):
        changed = cd(param)
        if (not changed):
          print('Path does not exist: ' + os.path.abspath(param))
          if (input_yn("Make new directory?")):
            if(mkdir(param)): #Make directory and try to cd again
              changed = cd(param)
            else:
              print('Could not make directory')
      else:
        print('No change')
    elif (c == 'ls'):   #List directory contents
      all_items = os.listdir('.')
      dirs = [i for i in all_items if os.path.isdir(i)]
      files = [i for i in all_items if os.path.isfile(i)]
      if (dirs):
        print('Folders:\n  ' + '\n  '.join(dirs))
      else:
        print('No folders.')
      if (files):
        maxfiles = len(files) if (param == '-a') else 10
        print('Files:\n  ' + '\n  '.join(files[:maxfiles]))
        if (len(files) > maxfiles):
          print('...and {} more. Show all with "ls -a"'.format(len(files)-maxfiles))
      else:
        print('No files.')
  elif (len(cmd) >= 3):  #Take picture
    takePictures(cmd)
    
  return True

def cd(path):
  try:
    os.chdir(path)
  except FileNotFoundError:
    return False
  except NotADirectoryError:
    return False
    
  return True

def mkdir(path):
  try:
    os.makedirs(path)
  except FileNotFoundError:
    return False
  except FileExistsError:
    return False
    
  return True

def input_yn(msg):
  return 'y' == input(msg + ' (y/n) ')[:1].lower()
  
  
main()