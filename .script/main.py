import os
import shutil
import argparse
import logging
from typing import Union, Text, Iterator, Tuple
from info_graph_dot import InfoGraphDot

PATH = Union[bytes, Text]
me = os.path.abspath(os.path.dirname(__file__))
log = logging.getLogger('templates')


def configure_log():
    log.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    log.addHandler(ch)

def get_templates(template_dir: PATH) -> Iterator[Tuple[str, PATH]]:
    for tpl in os.listdir(template_dir):
        tpl_path: PATH = os.path.join(template_dir, tpl)
        if os.path.isdir(tpl_path):
            yield tpl, os.path.join(template_dir, tpl)

def main(working_dir: PATH, args: argparse.Namespace):
    log.debug(f"Generate output for templates '{args.templates}'")
    log.debug(f" - output directory: '{working_dir}")

    info_graph_dot = InfoGraphDot()
    os.chdir(working_dir)
    info_graph_dot.setup()

    readme_all = os.path.join(working_dir, 'README.md')
    with open(readme_all, 'w') as f:
        f.write("# info_graph.dot\n")

        templates_dir = os.path.abspath(os.path.join(me, '..', args.templates))
        for name, path in get_templates(templates_dir):
            log.info(f"{name}: {path}")
            
            filename = info_graph_dot.run(name, path)
            f.write(f"[{name}]({filename})\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create docs for templates')
    parser.add_argument('--output', type=str, default=os.path.join(me, '..', '_working_dir'), help='working directory')
    parser.add_argument('--templates', type=str, help='templates to generate')
    args = parser.parse_args()

    working_dir = os.path.abspath(os.path.join(args.output, args.templates))
    if os.path.exists(working_dir):
        shutil.rmtree(working_dir)
    os.mkdir(working_dir)

    configure_log()
    main(working_dir, args)