import subprocess
import os
import logging
import shutil
import textwrap

from jinja2 import Template

log = logging.getLogger('templates')

class InfoGraphHTML:
    reference = "jinja2cpp/1.1.0@"
    template_filename = 'info_graph.html'
    _target_template_path = None

    output_template = Template(textwrap.dedent("""
        # {{ name }}

        Add info about the output (maybe a minimal template inside the folder?)

        Install it using...

        ```bash
        conan config install .... {{ install_path }}
        ```

        Output

        <p align="center">
            <img src="{{ name }}.png" width="350" title="{{ name }}">
        </p>
    """))

    def __init__(self):
        process = subprocess.Popen(['conan', 'config', 'home'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        conan_home = stdout.decode('utf8').strip()
        target_template_directory = os.path.join(conan_home, 'templates', 'output')
        os.makedirs(target_template_directory, exist_ok=True)
        self._target_template_path = os.path.join(target_template_directory, 'info_graph.html')

    def setup(self):
        process = subprocess.Popen(['conan', 'install', self.reference, '--remote', 'conan-center'],
                     stdout=subprocess.PIPE, 
                     stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

    def run(self, name, template_path):
        # Copy the template file in place
        template_filename = os.path.join(template_path, self.template_filename)
        if not os.path.exists(template_filename):
            log.error(f"Template '{name}' not found: expected file '{self.template_filename}' missing")
            return False

        shutil.copyfile(template_filename, self._target_template_path)

        # Run the actual work
        output_file = name + '.html'
        process = subprocess.Popen(['conan', 'info', self.reference, '--graph', output_file],
                     stdout=subprocess.PIPE, 
                     stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        # Take the picture
        picture_file = name + '.png'
        process = subprocess.Popen(['wkhtmltoimage', '--debug-javascript', output_file, picture_file],
                     stdout=subprocess.PIPE, 
                     stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        log.info(stdout)

        # Generate the output
        with open(f"{name}.md", 'w') as f:
            f.write(self.output_template.render(name=name, install_path="WIP"))

        return f"{name}.md"
