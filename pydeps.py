#!/usr/bin/env python

"""
Given a directory of Python source files, creates a graph showing which
modules depend on which other modules.

The graph omits modules that are not in the source file directory.
These are assumed to be system modules.
"""

from collections import OrderedDict
from optparse import OptionParser
import os
import os.path
import re
import sys


VERBOSE = False

IMPORT_RE = re.compile(                                   r'^import ([a-zA-Z_.]+)')
FROM_IMPORT_RE = re.compile(           r'^from ([a-zA-Z_.]+) import ([a-zA-Z_.]+)')
DELAYED_IMPORT_RE = re.compile(                        r'^\W+import ([a-zA-Z_.]+)')
DELAYED_FROM_IMPORT_RE = re.compile(r'^\W+from ([a-zA-Z_.]+) import ([a-zA-Z_.]+)')
MAIN_FUNCTION_MARKER = "if __name__ == '__main__':"

def main(args_ignored):
    parser = OptionParser()
    parser.add_option(
        "-i", "--ignore-modules",
        dest="ignore_modules", default="",
        help="Comma-separated list of modules to omit from the output graph.",
        metavar="IGNORE")
    (options, args) = parser.parse_args()
    
    # Parse arguments
    (source_directory_dirpath, output_dot_file_filepath) = args
    
    # Parse options
    ignored_module_names = options.ignore_modules.split(',')
    if ignored_module_names == ['']:
        ignored_module_names = []
    
    module_name_2_info = OrderedDict()
    for (dirpath, dirnames, filenames) in os.walk(source_directory_dirpath):
        for filename in filenames:
            if filename.endswith('.py'):
                filepath = os.path.join(dirpath, filename)
                filepath_relative_to_source_directory = os.path.relpath(
                    filepath, source_directory_dirpath)
                
                module_name = filepath_relative_to_source_directory
                module_name = module_name[:-len('.py')]
                module_name = module_name.replace(os.sep, '.')
                if module_name.endswith('.__init__'):
                    module_name = module_name[:-len('.__init__')]
                
                info = read_source_file(filepath)
                
                module_name_2_info[module_name] = info
    
    if VERBOSE:
        from pprint import pprint
        pprint(dict(module_name_2_info))
    
    module_names = module_name_2_info.keys()
    
    # Convert relative imports to absolute imports
    for (module_name, info) in module_name_2_info.iteritems():
        deps = info['deps']
        delayed_deps = info['delayed_deps']
        for rel_dep in deps + delayed_deps:
            if '.' in module_name:
                abs_dep = module_name[:module_name.rindex('.')] + '.' + rel_dep
            else:
                # abs_dep is the same as rel_dep
                continue
            
            if abs_dep in module_names:
                # Rewrite rel_dep -> abs_dep
                deps = info['deps'] = [
                    abs_dep if dep == rel_dep else dep for dep in deps]
                delayed_deps = info['delayed_deps'] = [
                    abs_dep if dep == rel_dep else dep for dep in delayed_deps]
    
    # Compute edges and count the number of occurrences
    edge_2_weight = OrderedDict()
    for (module_name, info) in module_name_2_info.iteritems():
        deps = info['deps']
        delayed_deps = info['delayed_deps']
        for dep in deps + delayed_deps:
            is_system_dep = dep not in module_names
            if not is_system_dep:
                edge = (module_name, dep)
                
                if edge not in edge_2_weight:
                    edge_2_weight[edge] = 1
                else:
                    edge_2_weight[edge] += 1
    
    with open(output_dot_file_filepath, 'wb') as output:
        print >> output, 'digraph "Module Dependencies" {'
        print >> output, '    graph [rankdir=LR]'
        print >> output, '    '
        
        # Output nodes (modules)
        for (module_name, info) in module_name_2_info.iteritems():
            if module_name in ignored_module_names:
                continue
            
            is_empty = info['is_empty']
            if is_empty:
                # Omit empty modules from the graph
                continue
            
            has_main_function = info['has_main_function']
            if has_main_function:
                # Color modules yellow that have main functions
                style_suffix = ' [style=filled, fillcolor=yellow]'
            else:
                style_suffix = ''
            
            print >> output, '    "%s"%s' % (module_name, style_suffix)
        print >> output, '    '
        
        # Output edges (dependencies)
        for (edge, weight) in edge_2_weight.iteritems():
            (module_name, dep) = edge
            
            if (module_name in ignored_module_names) or (dep in ignored_module_names):
                continue
            
            has_nondelayed = dep in module_name_2_info[module_name]['deps']
            has_delayed = dep in module_name_2_info[module_name]['delayed_deps']
            only_delayed = has_delayed and not has_nondelayed
            
            style_suffix = ' [penwidth=%d' % weight
            if only_delayed:
                style_suffix += ', style=dashed'
            style_suffix += ']'
            
            print >> output, '    "%s" -> "%s"%s' % \
                (module_name, dep, style_suffix)
        
        print >> output, '}'


def read_source_file(source_filepath):
    deps = []
    delayed_deps = []
    has_main_function = False
    with open(source_filepath, 'rb') as source_file:
        for line in source_file:
            line = line.strip('\r\n')
            
            matcher = IMPORT_RE.match(line)
            if matcher is not None:
                deps.append(matcher.group(1))
            
            matcher = FROM_IMPORT_RE.match(line)
            if matcher is not None:
                deps.append(matcher.group(1))
            
            matcher = DELAYED_IMPORT_RE.match(line)
            if matcher is not None:
                delayed_deps.append(matcher.group(1))
            
            matcher = DELAYED_FROM_IMPORT_RE.match(line)
            if matcher is not None:
                delayed_deps.append(matcher.group(1))
            
            if MAIN_FUNCTION_MARKER in line:
                has_main_function = True
        
        is_empty = (source_file.tell() == 0)
    
    return {
        'deps': deps,
        'delayed_deps': delayed_deps,
        'has_main_function': has_main_function,
        'is_empty': is_empty,
    }


if __name__ == '__main__':
    main(sys.argv[1:])
