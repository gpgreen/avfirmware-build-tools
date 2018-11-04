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
import stat

# parameters for each project
# key is the name of the project
# value is a list
#  0: type of project
#  1: directory where CMakeLists.txt for project resides
#  2: directory name for build
#  3: which build generator to use for cmake
#  4: list of -D arguments to add to cmake
project_params = {
    'ahrs': [
        "avr",
        "ahrs",
        "build-ahrs-avr",
        "Ninja",
        ["CMAKE_AVRLIBS_PATH=%s"],
        ],
    'compass': [
        "avr",
        "compass",
        "build-compass-avr",
        "Ninja",
        ["CMAKE_AVRLIBS_PATH=%s"],
        ],
    'avr_drivers-ahrs': [
        "avr",
        "libs/avr_drivers",
        "build-avr_drivers-ahrs-avr",
        "Ninja",
        ["AHRS_FIRMWARE=ON"],
        ],
    'avr_drivers-compass': [
        "avr",
        "libs/avr_drivers",
        "build-avr_drivers-compass-avr",
        "Ninja",
        ["COMPASS_FIRMWARE=ON"],
        ],
    'libuavcan': [
        "linux-x86_64",
        "libs/libuavcan",
        "build-libuavcan-linux-x86_64",
        "Ninja",
        [],
        ],
}

def finish_cmake_define_string(projname, rootdir, s):
    # if an avr application firmware, replace the '%s' for
    # CMAKE_AVRLIBS_PATH with appropriate path to avr_drivers
    # libraries for that firmware build
    if projname == 'ahrs' or projname == 'compass':
        news = s % os.path.abspath(
            os.path.join(rootdir,
                         'build', 'build-avr_drivers-%s-avr' % projname))
        s = news
    return s

def construct_cmake_args(deflist):
    newlist = ["-D" + d for d in deflist]
    if len(newlist) > 0:
        return " ".join(newlist)
    else:
        return ""

def execute_avr_cmake(root_dir, proj_dir, generator_type, definestr):
    build_chain_path = os.path.abspath(
        os.path.join(root_dir,
                     'build-tools/cmake-avr/generic-gcc-avr.cmake'))
    cmd = 'cmake -G "%s" -DCMAKE_TOOLCHAIN_FILE=%s %s %s' % (
        generator_type, build_chain_path, definestr, proj_dir)
    print("Executing: " + cmd)
    return os.popen(cmd, 'r', True)
    
def execute_cmake(root_dir, proj_dir, generator_type, definestr):
    cmd = 'cmake -G "%s" %s %s' % (generator_type, definestr, proj_dir)
    print("Executing: " + cmd)
    return os.popen(cmd, 'r', True)
    
def main(args):
    if len(args) < 3:
        print("usage: run-cmake.py root_dir project_name")
        sys.exit(-1)
    root_dir = os.path.abspath(args[1])
    projname = args[2]
    proj_type, proj_dir, build_dir, gen_type, defines = project_params[projname]
    if proj_type == 'avr':
        cmake_fn = execute_avr_cmake
    else:
        cmake_fn = execute_cmake

    # path to proj
    proj_dir = os.path.abspath(os.path.join(root_dir, proj_dir))
        
    # create the build directory under root directory
    os.chdir(root_dir)
    root_build = os.path.abspath(os.path.join(root_dir, 'build'))
    if not os.path.exists(root_build):
        os.mkdir('build')
        os.chmod(root_build, stat.S_IRWXU|stat.S_IRWXG|stat.S_IROTH|stat.S_IXOTH)
    os.chdir(root_build)

    # create the project build directory
    build_path = os.path.abspath(os.path.join(root_build, build_dir))
    if not os.path.exists(build_path):
        os.mkdir(build_dir)
        os.chmod(build_dir, stat.S_IRWXU|stat.S_IRWXG|stat.S_IROTH|stat.S_IXOTH)

    # now that all directories are built, do the rest
    if os.path.isdir(build_path):
        os.chdir(build_path)
        print("build directory: " + build_path)
        definestr = finish_cmake_define_string(projname, root_dir, construct_cmake_args(defines))
        with cmake_fn(root_dir, proj_dir, gen_type, definestr) as output:
            print(output.read())
    else:
        raise RuntimeError("build path '%s' exists but is not a directory" % build_path)
    
if __name__ == "__main__":
    main(sys.argv)
