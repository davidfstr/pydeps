# pydeps

Visualizes dependencies between Python modules.

## Usage

Just run the `pydeps.py` command with a path to a directory containing Python source files.

```
python pydeps.py ~/Projects/CPM/src output.dot
```

The output is a `.dot` file, which can be rendered with [GraphViz].

And marvel as your program's modules and their dependencies become visible:

<img src="https://raw.github.com/davidfstr/pydeps/master/docs/sample_output.png" />

## Output Notes

* Nodes are Python modules. Edges are `imports` from one module to another.
* Edge thickness is proportional to the number of imports.
    * Therefore the thickness approximates the amount of coupling between adjacent modules.
* Dashed edges (*not depicted*) denote an import that is outside the top-level.
    * Such imports inside functions are typically used when creating a circular dependency.
    * Conditional imports at the top level are also displayed in this manner.
* Yellow modules contain a main function (via the idiom `if __name__ == '__main__':`).
    * Since modules with main functions are typically standalone programs or commands,
      it's a good idea to avoid depending on them.
* System modules are excluded from the graph.
    * A system module is defined as any module which resides outside the specified source directory.

## Advanced Usage

A small number of command-line options are also supported:

<table>
  <tr>
    <th>Option</th>
    <th>Description</th>
    <th>Example</th>
  </tr>
  <tr>
    <td><code>-i, --ignore-modules</code></td>
    <td>Comma-separated list of modules to omit from the output graph.</td>
    <td>crystal.xthreading, crystal.xfutures</td>
  </tr>
</table>

## Fun Ideas

* Create an animated history of your program's growth over time:
    * Write a program that checks out each revision of your program,
      runs `pydeps.py`, and uses the `dot` tool to generate an image.

## Requirements

* Python 2.7
    * Earlier versions probably work too, but I haven't tested them.
* [GraphViz] &mdash; to render the output `.dot` files


[GraphViz]: http://www.graphviz.org