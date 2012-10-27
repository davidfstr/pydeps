#!/usr/bin/env python

"""
Given a directory of Python source files, creates a graph showing which
modules depend on which other modules.

By default, the graph omits modules that are not in the source file directory.
These are assumed to be system modules.
"""

from collections import OrderedDict
import os
import os.path
import re
import sys


IMPORT_RE = re.compile(r'^import ([a-zA-Z_.]+)')
FROM_IMPORT_RE = re.compile(r'^from ([a-zA-Z_.]+) import ([a-zA-Z_.]+)')

def main(args):
    (source_directory_dirpath, output_dot_file_filepath) = args
    
    module_name_2_deps = OrderedDict()
    
    for (dirpath, dirnames, filenames) in os.walk(source_directory_dirpath):
        for filename in filenames:
            if filename.endswith('.py'):
                filepath = os.path.join(dirpath, filename)
                filepath_relative_to_source_directory = os.path.relpath(
                    filepath, source_directory_dirpath)
                
                module_name = filepath_relative_to_source_directory
                module_name = module_name[:-len('.py')]
                module_name.replace(os.sep, '.')
                
                deps = read_dependencies_of_source_file(filepath)
                
                module_name_2_deps[module_name] = deps
    
    with open(output_dot_file_filepath, 'wb') as output:
        print >> output, 'digraph "Module Dependencies" {'
        print >> output, '    graph [rankdir=LR]'
        print >> output, '    '
        
        for (module_name, deps) in module_name_2_deps.iteritems():
            for dep in deps:
                is_system_dep = dep not in module_name_2_deps
                if not is_system_dep:
                    print >> output, '    "%s" -> "%s"' % (module_name, dep)
        
        print >> output, '}'


def read_dependencies_of_source_file(source_filepath):
    deps = []
    with open(source_filepath, 'rb') as source_file:
        for line in source_file:
            line = line.strip('\r\n')
            
            matcher = IMPORT_RE.match(line)
            if matcher is not None:
                deps.append(matcher.group(1))
            
            matcher = FROM_IMPORT_RE.match(line)
            if matcher is not None:
                deps.append(matcher.group(1))
    
    return deps


if __name__ == '__main__':
    main(sys.argv[1:])
