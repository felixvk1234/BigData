import sys
import networkx as nx
import json
import re


def convert(in_file, out_file, full=False):
    elements = []
    with open(in_file, "r", encoding="utf-8") as jsonl:
        if not full:
            for line in jsonl.readlines():
                json_line = json.loads(line)
                for _, ed in json_line.items():
                    eds = []
                    if type(ed) == dict:
                        eds.append(ed)
                    elif type(ed) == list:
                        eds.extend(ed)
                    for ed in eds:
                        if ed.get("type") in ["path"]:
                            for node in ed.get("nodes", []):
                                elements.append(node)
                            for rel in ed.get("relationships", []):
                                elements.append(rel)
                        elif ed.get("type") in ["node", "relationship"]:
                            elements.append(ed)
        else:
            elements = [ed for ed in json.load(jsonl)]

    nodes = {}
    edges = {}

    for element in elements:
        if "labels" in element:
            label = element["labels"][0]
        elif "label" in element:
            label = element["label"]
        else:
            print(f"ERROR: Label not found for element: {element.get('ident')}")
        props = element.get("properties", {})
        typ = element.get("type", None)
        if typ == "node":
            props["label"] = props.get("ident")
            props["node_type"] = label
            props[f"{label}_label"] = props.get("ident")
            nodes[element.get("id", props.get("ident"))] = props
        elif typ == "relationship":
            start = element["start"]
            end = element["end"]
            props["edge_type"] = label
            edges[(start, end)] = props
        else:
            print(f"ERROR: Unrecognized type: {typ}")

    G = nx.DiGraph()
    for identifier, props in nodes.items():
        G.add_node(identifier, **props)
    for (start, end), props in edges.items():
        G.add_edge(start, end, **props)

    nx.write_graphml(G, out_file)


def clean(in_file, out_file):
    print(out_file)
    output = open(out_file, "w", encoding="utf-8")
    with open(in_file, "r", encoding="utf-8") as inputl:
        for ln, line in enumerate(inputl):
            finder = re.finditer("<data (.*?)>(.*?)</data>", line)
            for x in finder:
                line = line.replace(
                    f"<data {x.group(1)}>{x.group(2)}</data>",
                    f"<data {x.group(1)}><![CDATA[{x.group(2)}]]></data>"
                )
            output.write(line)
    output.close()


if __name__ == "__main__":
    arguments = sys.argv[1:]
    if len(arguments) == 0:
        print(f"Usage: python json2graphml.py in_file [out_file] [-f] [-c]")
        exit()
    in_file = arguments[0]
    full = "-f" in arguments
    clea = "-c" in arguments
    out_file = in_file.replace(".json", ".graphml")
    if clea:
        out_file = out_file.replace(".graphml", ".clean.graphml")
        clean(in_file, out_file)
    else:
        convert(in_file, out_file, full)
    print(f"Done, output file saved to: {out_file}")
