#!/usr/bin/env python

######################################################################
# run-cmake.py
#
# Script to run cmake in a build directory for a avfirmware build
# Arguments:
#  root_dir: root of avfirmware project structure, all paths relative
#            to this
#  project: name of project to run cmake
#
######################################################################

import sys
import os

# parameters for each project
# key is the name of the project
# value is a list
#  0: type of project
#  1: directory where CMakeLists.txt for project resides
#  2: directory name for build
#  3: which build generator to use for cmake
project_params = {
    'ahrs': [
             "avr",
             "ahrs",
             "build-ahrs",
             "Unix Makefiles"
             ],
    'libuavcan': [
                  "linux-x86_64",
                  "libs/libuavcan",
                  "build-libuavcan-linux-x86_64",
                  "Ninja"
                  ],
}

def execute_avr_cmake(root_dir, proj_dir, generator_type):
    build_chain_path = os.path.abspath(
        os.path.join(root_dir,
                     'build-tools/cmake-avr/generic-gcc-avr.cmake'))
    cmd = 'cmake -G "%s" -DCMAKE_TOOLCHAIN_FILE=%s %s' % (
        generator_type, build_chain_path, proj_dir)
    print("Executing: " + cmd)
    return os.popen(cmd, 'r', True)
    
def execute_cmake(root_dir, proj_dir, generator_type):
    cmd = 'cmake -G "%s" %s' % (generator_type, proj_dir)
    print("Executing: " + cmd)
    return os.popen(cmd, 'r', True)
    
def main(args):
    if len(args) < 3:
        print("usage: run-cmake.py root_dir project_name")
        sys.exit(-1)
    root_dir = os.path.abspath(args[1])
    projname = args[2]
    proj_type, proj_dir, build_dir, gen_type = project_params[projname]
    if proj_type == 'avr':
        cmake_fn = execute_avr_cmake
    else:
        cmake_fn = execute_cmake

    # create path to proj
    proj_dir = os.path.abspath(os.path.join(root_dir, proj_dir))
        
    # create the build directory
    os.chdir(root_dir)
    build_path = os.path.abspath(os.path.join(root_dir, build_dir))
    if not os.path.exists(build_path):
        os.mkdir(build_dir)
    if os.path.isdir(build_path):
        os.chdir(build_path)
        print("in build directory: " + build_path)
        with cmake_fn(root_dir, proj_dir, gen_type) as output:
            print(output.read())
    else:
        raise RuntimeError("build path '%s' exists but is not a directory" % build_path)
    
if __name__ == "__main__":
    main(sys.argv)
