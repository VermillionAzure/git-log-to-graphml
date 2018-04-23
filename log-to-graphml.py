import itertools, collections
import xml.etree.cElementTree as ET

# Setup the header XML element, including
# the links to the schema
root = ET.Element('graphml')
root.set('xmlns',
        'http://graphml.graphdrawing.org/xmlns')
root.set('xmlns:xsi',
        'http://www.w3.org/2001/XMLSchema-instance')
root.set('xsi:schemaLocation',
          'http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd')

# Setup the actor_type attribute for nodes
keyd0 = ET.Element('key')
keyd0.set('id', 'd0')
keyd0.set('for', 'node')
keyd0.set('attr.name', 'actor_type')
keyd0.set('attr.type', 'integer')

# Enum-like class for the actor_type attribute
class NodeActorType():
    CONTRIBUTOR = 0
    FILE = 1

# Setup the label attribute for nodes
keyd1 = ET.Element('key')
keyd1.set('id', 'd1')
keyd1.set('for', 'node')
keyd1.set('attr.name', 'email')
keyd1.set('attr.type', 'string')

# Setup the Git commit contributor name / filename
# attribute
keyd2 = ET.Element('key')
keyd2.set('id', 'd2')
keyd2.set('for', 'node')
keyd2.set('attr.name', 'name')

# Put the attribute subtrees on the XML element tree
root.append(keyd0)
root.append(keyd1)
root.append(keyd2)

# Prepare the graph subtree.
# This will be appended to.
graph = ET.Element('graph')
graph.set('id', 'G')
graph.set('edgedefault', 'directed')

# Integers to hold our global count for the
# node id and the edge id
node_id = 0
edge_id = 0

#debug
# Test XML capabilities
print(ET.tostring(root, 'utf-8'))

# A global line buffer to be used by the
# parsing procedures.
line = ''

def consume(iterator, n):
    collections.deque(itertools.islice(iterator, n))

def next_line(it):
    global line
    line = it.next()

def generate_node_id():
    global node_id
    temp = node_id
    node_id = node_id + 1
    return temp

def generate_edge_id():
    global edge_id
    temp = edge_id
    edge_id = edge_id + 1
    return temp

def insert_contributor_node(data):
    global graph
    # Get the email and username data
    email = data[0]
    username = data[1]

    # Build the XML tree
    node = ET.Element('node')
    node.set('id', str(generate_node_id()))
    # Fill out the actor_type attribute
    datad0 = ET.SubElement(node, 'data')
    datad0.set('key', 'd0')
    datad0.text = str(NodeActorType.CONTRIBUTOR)

    # Fill out the email attribute
    datad1 = ET.SubElement(node, 'data')
    datad1.set('key', 'd1')
    datad1.text = data[0]

    # Fill out the name attribute (for the contributor)
    datad2 = ET.SubElement(node, 'data')
    datad2.set('key', 'd2')
    datad2.text = data[1]

    print(ET.tostring(node, 'utf-8'))


def parse_entry(it):
    global line
    global graph
    # Parse the commit info line for that line
    parts = line.split('|')

    # Remove empty strings from the list
    parts = filter(None, parts)
    print('parts: ' + ' | '.join(parts))
    next_line(it)

    print(graph.findall('node'))

    # Add the new contributor node to the list
    # only if it already is not there.
    contributor_found = False
    for node_elem in graph.findall('node'):
        if node_elem.findtext(parts[0]):
            contributor_found = True
            break

    if contributor_found:
        print('Contributor ' + parts[0] + ' already found')
    else:
        print('Contributor ' + parts[0] + ' not found')
        print('Inserting contributor node into graph...')
        insert_contributor_node(parts)

    # For each file, mark it.
    files = []
    sentinel = object()
    while (line != '$'):
        if (line.strip() != ''):
            files.append(line)
            print('>>> ' + line)
        try:
            next_line(it)
        except StopIteration:
            print("End of file reached.")
            line = ''
            break
    print('files: ' + ','.join(files))


with open('git-commit.log', 'r') as file:
    # Get all the lines in the file
    lines = file.readlines()
    # Strip leading, trailing whitespace
    lines = [x.strip() for x in lines]

    #debug
    print(lines)

    # Get the iterator for the lines array
    it = iter(lines)
    line = it.next()

    # For each line, 
    while True:
        try:
            if (line == '$'):
                print('NEW ENTRY:')
                next_line(it)
                parse_entry(it)
            else:
                next_line(it)
        except StopIteration:
            print('Ended loop.')
            break
    root.append(graph)
    print(ET.tostring(root, 'utf-8'))

