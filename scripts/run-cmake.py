#!/usr/bin/env python3

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
#  5: if not None, then key to other project param to add a cmake
#     define CMAKE_AVRLIBS_PATH with that project's build directory
project_params = {
    'ahrs': [
        "avr",
        "ahrs",
        "build-ahrs-avr",
        "Ninja",
        [],
        "avr_drivers-ahrs",
        ],
    'compass': [
        "avr",
        "compass",
        "build-compass-avr",
        "Ninja",
        ["CMAKE_LIBCANARD_PATH=build-libcanard-drivers-avr-compass-avr"],
        "avr_drivers-compass",
        ],
    'canbus-shield': [
        "avr",
        "canbus-shield",
        "build-canbus-shield-avr",
        "Ninja",
        [],
        "avr_drivers-canbus-shield",
        ],
    'avr_drivers-ahrs': [
        "avr",
        "libs/avr_drivers",
        "build-avr_drivers-ahrs-avr",
        "Ninja",
        ["AHRS_FIRMWARE=ON",
         "CANAERO=ON"],
        None,
        ],
    'avr_drivers-compass': [
        "avr",
        "libs/avr_drivers",
        "build-avr_drivers-compass-avr",
        "Ninja",
        ["COMPASS_FIRMWARE=ON"],
        None,
        ],
    'libcanard-compass': [
        "avr",
        "libs/libcanard/drivers/avr",
        "build-libcanard-drivers-avr-compass-avr",
        "Ninja",
        [],
        None,
        ],
    'avr_drivers-canbus-shield': [
        "avr",
        "libs/avr_drivers",
        "build-avr_drivers-canbus-shield-avr",
        "Ninja",
        ["CANBUS_SHIELD_FIRMWARE=ON",
         "NMEA_2000=ON"],
        None,
        ],
    'libuavcan': [
        "linux-x86_64",
        "libs/libuavcan",
        "build-libuavcan-linux-x86_64",
        "Ninja",
        [],
        None,
        ],
    'libuavcan-bbb': [
        "linux-arm-gnueabihf",
        "libs/libuavcan",
        "build-libuavcan-linux-arm-gnueabihf",
        "Unix Makefiles",
        ["CMAKE_C_COMPILER:STRING=arm-linux-gnueabihf-gcc",
        "CMAKE_CXX_COMPILER:STRING=arm-linux-gnueabihf-g++",],
        None,
        ],
    'pypilot-controller': [
        "avr",
        "pypilot-controller",
        "build-pypilot-controller",
        "Ninja",
        [],
        "avr_drivers-pypilot-controller",
        ],
    'avr_drivers-pypilot-controller': [
        "avr",
        "libs/avr_drivers",
        "build-avr_drivers-pypilot-controller",
        "Ninja",
        ["PYPILOT_CONTROLLER_FIRMWARE=ON",
         "NMEA_2000=ON"],
        None,
        ],
    'libsimavr_parts': [
        "linux-x86_64",
        "libs/simavr_parts",
        "build-libsimavr_parts-linux-x86_64",
        "Ninja",
        [],
        None,
        ],
}

def finish_cmake_define_string(projname, rootdir, add_avr_lib_path, debug_build, s):
    """ if an avr application firmware, add an additional
    cmake define 'CMAKE_AVRLIBS_PATH' with build path
    from another project """
    if add_avr_lib_path:
        avr_build_path = construct_build_path(add_avr_lib_path, rootdir)
        s += " -DCMAKE_AVRLIBS_PATH=" + avr_build_path
    if debug_build:
        s += " -DCMAKE_BUILD_TYPE=Debug"
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
    print("Executing:\n  " + cmd)
    return os.popen(cmd, 'r', True)
    
def execute_cmake(root_dir, proj_dir, generator_type, definestr):
    cmd = 'cmake -G "%s" %s %s' % (generator_type, definestr, proj_dir)
    print("Executing:\n  " + cmd)
    return os.popen(cmd, 'r', True)

def construct_build_path(param_key, root_dir):
    return os.path.abspath(os.path.join(root_dir, 'build', project_params[param_key][2]))

def show_projects():
    keys = project_params.keys()
    print("Project List")
    [print("\t%s" % k) for k in sorted(keys)]
    print

def usage():
        print(
"""usage: 
run-cmake.py create[--create] [debug|--debug] root_dir project_name
    Runs cmake for 'project_name' at firmware tree 'root_dir'
run-cmake.py list[--list]
    Lists all projects
run-cmake.py help[--help]
    Shows this help string
""")
    
def main(args):
    root_dir_index = 2
    debug_build = False
    if len(args) < 2:
        usage()
        sys.exit(-1)
    if args[1] == 'list' or args[1] == '--list':
        show_projects()
        sys.exit(0)
    elif args[1] == 'help' or args[1] == '--help':
        usage()
        sys.exit(0)
    elif (args[1] == 'create' or args[1] == '--create') and (len(args) < 4 or len(args) > 5):
        usage()
        sys.exit(-1)
    if (args[1] == 'create' or args[1] == '--create') and (args[2] == 'debug' or args[2] == '--debug'):
        root_dir_index = 3
        debug_build = True
    root_dir = os.path.abspath(args[root_dir_index])
    projname = args[root_dir_index+1]
    print("Project tree '%s'" % root_dir)
    print("Running cmake for project '%s'" % projname)
    
    proj_type, proj_dir, build_dir, gen_type, defines, add_avr_lib_path = project_params[projname]
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
    build_path = construct_build_path(projname, root_dir)
    if not os.path.exists(build_path):
        os.mkdir(build_dir)
        os.chmod(build_dir, stat.S_IRWXU|stat.S_IRWXG|stat.S_IROTH|stat.S_IXOTH)

    # now that all directories are built, do the rest
    if os.path.isdir(build_path):
        os.chdir(build_path)
        print("Build directory: " + build_path)
        definestr = finish_cmake_define_string(projname, root_dir, add_avr_lib_path,
                                                   debug_build, construct_cmake_args(defines))
        #print("Final cmake options:" + definestr)
        with cmake_fn(root_dir, proj_dir, gen_type, definestr) as output:
            print(output.read())
    else:
        raise RuntimeError("build path '%s' exists but is not a directory" % build_path)
    
if __name__ == "__main__":
    main(sys.argv)
