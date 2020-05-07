# Mail Snapshot

This script takes snapshots of a folder and send them by email.

The typical use is a professor supervising students during a programming labs (potentially remotely). Students should run this script in order to regularly email snapshots of their projects.

The professor can thus check:

-  if any student magically gets a working code that is completely different from the last snapshot
-  how students have progressed through the lab

The script has to be tailored for a given professor and a given project. All modifications are to be done in the first lines of the script.

## Professor-wise

Fill in your email address / smtp server. Some advanced parameters can be found in the script.

## Project-wise

A 'project' is the folder that will be zipped. It should be given a name, and should match one of these two conditions to be identified on the student's hard drive:

- if it is a CMake project, then the folder should have the project name and the CMakeLists.txt file should define a project with this name
- more generally, a list of files (possibly in sub-folders) can be given and will serve a the folder signature

A list of ignored files can also be entered: they will not be part of the mailed zip file.

The mail period and total should be entered, the first mail will only be send after one period is over. 
Typically, if `mail_period` is 15 and `mail_total` is 8 then the script will send a mail every 15 minutes, the last mail will be sent after 2 hours.


## Student-wise

Students should just fill in their email address. Email password will be asked at runtime.


## Examples

Three examples are given:

- A CMake project called `a_cmake_project`:
  * it will be found by defining `project_name = 'a_cmake_project'`.
  * `project_signature`  should be empty.
  * `project_ignores` can be equal to `['do_not_want.md']`, in this case the file will not be zipped.
  
- A Python project:
  * pick any name for this project.
  * give the signature `project_signature = ['main.py','module.py']`.
  * `project_ignores` can be equal to `['do_not_want.md']`.
  
- A duplicate CMake project:
  * it will be found by defining `project_name = 'another_cmake_project'`.
  * `project_signature`  should be empty.
  * there are actually two folders defining such a CMake project: the script will ask which one is to be sent.
