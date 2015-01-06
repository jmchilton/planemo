#!/usr/bin/env python
import os
import re
import traceback
import string
import subprocess
import sys
import urllib
import urlparse
from xml.etree import ElementTree as ET

import click

from bioblend import toolshed


TOOLSHED = "https://toolshed.g2.bx.psu.edu"
TOOLSHED_MAP = {
    "toolshed": "https://toolshed.g2.bx.psu.edu",
    "testtoolshed": "https://testtoolshed.g2.bx.psu.edu",
}
GIT_USER = "jmchilton"
if sys.platform == "darwin":
    DEFAULT_HOMEBREW_ROOT = "/usr/local"
else:
    DEFAULT_HOMEBREW_ROOT = os.path.join(os.path.expanduser("~"),
                                         ".linuxbrew")

UNNEEDED_SET_ENV = ("# Tool Shed set environment variable that is "
                    "picked implicitly.")


EXTENSION_ENVIRONMENT = """
def environment(actions)
    # Setup envirnoment variable modifications that will be used later by
    # platform-brew's env and vinstall commands.
    act_hash = {"actions" => actions}
    (prefix / "platform_environment.json").write act_hash.to_json
end
"""

EXTENSION_PYTHON = """
  def depend_python(python_recipe)
    ENV["PYTHONHOME"] = Formula[python_recipe].prefix
    ENV["PYTHONPATH"] = Formula[python_recipe].prefix
    ENV.prepend_path "PATH", prefix / "bin"
    ENV.prepend_path "PYTHONPATH", prefix
  end

  def easy_install(what)
    system "easy_install", "--install-dir", prefix, "--script-dir",
           "#{prefix}/bin", what
  end
"""

EXTENSION_R = """
"""

EXTENSION_RUBY = """
"""

EXTENSION_PERL = """

"""


@click.command()
@click.option('--tool_shed',
              default="toolshed",
              type=click.Choice(TOOLSHED_MAP.keys()),
              help='Tool shed to target.')
@click.option('--owner',
              default=None,
              help='Limit generation to specific owner.')
@click.option('--name_filter',
              default=None,
              help='Apply regex to name filters.')
@click.option('--git_user', default="jmchilton")
@click.option('--brew_directory', default=DEFAULT_HOMEBREW_ROOT)
def main(**kwds):
    user = kwds["git_user"]
    repo_name = "homebrew-%s" % kwds["tool_shed"]
    target = os.path.join(
        kwds["brew_directory"],
        "Library",
        "Taps",
        user,
        repo_name
    )
    tap = Tap("%s/%s" % (user, kwds["tool_shed"]))
    # shell("rm -rf %s" % target)
    shell("mkdir -p %s" % target)
    prefix = kwds["tool_shed"]
    tool_shed_url = TOOLSHED_MAP[prefix]
    dependencies_list = []
    repo_iter = repos(
        tool_shed_url,
        owner=kwds["owner"],
        name_filter=kwds["name_filter"]
    )
    for raw_repo in repo_iter:
        repo = Repo.from_api(prefix, raw_repo)
        dependencies_file = repo.get_file("tool_dependencies.xml")
        if not dependencies_file:
            message = "skipping repository %s, no tool_dependencies.xml"
            click.echo(message % repo)
            continue
        try:
            dependencies = Dependencies(dependencies_file, repo, tap)
        except Exception as e:
            message = "Failed to parse dependencies for repo %s, skipping."
            print message % repo
            continue
        dependencies_list.append(dependencies)

    for dependencies in dependencies_list:
        for package in dependencies.packages:
            try:
                (file_name, contents) = package.to_recipe()
                recipe_path = os.path.join(target, file_name)
                open(recipe_path, "w").write(contents)
            except Exception as e:
                traceback.print_exc()
                message = "Failed to convert package [%s], exception [%s]"
                print message % (package, e)

    shell("git init %s" % target)
    git_target = "--work-tree %s --git-dir %s/.git" % (target, target)
    shell("git %s add %s/*" % (git_target, target))
    shell("git %s commit -m 'Initial Commit' " % (git_target))


class Tap(object):

    def __init__(self, prefix):
        self.prefix = prefix


class Dependencies(object):

    def __init__(self, dependencies_file, repo, tap):
        self.repo = repo
        self.tap = tap
        self.root = ET.parse(dependencies_file).getroot()
        packages = []
        dependencies = []
        package_els = self.root.findall("package")
        if not package_els:
            print "No packages found for repo %s" % repo
        for package_el in package_els:
            install_els = package_el.findall("install")
            readme_els = package_el.findall("readme")
            if len(readme_els) > 0:
                readme = readme_els[0].text
            else:
                readme = None
            assert len(install_els) in (0, 1)
            if len(install_els) == 1:
                install_el = install_els[0]
                package = Package(self, package_el, install_el, readme=readme)
                packages.append(package)
            else:
                repository_el = package_el.find("repository")
                if repository_el is None:
                    message = "no repository in package el for %s" % repo
                    raise AssertionError(message)
                dependency = Dependency(self, package_el, repository_el)
                dependencies.append(dependency)

        self.packages = packages
        self.dependencies = dependencies

    def single_package(self):
        return len(self.packages) == 1

    def __repr__(self):
        return "Dependencies[for_repo=%s]" % self.repo


class Dependency(object):

    def __init__(self, dependencies, package_el, repository_el):
        self.dependencies = dependencies
        self.package_el = package_el
        self.repository_el = repository_el
        self.repo = Repo.from_xml(repository_el)

    def __repr__(self):
        temp = "Dependency[package_name=%s,version=%s,dependent_package=%s]"
        return temp % (
            self.package_el.attrib["name"],
            self.package_el.attrib["version"],
            self.repository_el.attrib["name"]
        )


class Actions(object):

    def __init__(
        self,
        actions,
        os=None,
        architecture=None,
        action_packages=[]
    ):
        self.os = os
        self.architecture = architecture
        self.actions = actions or []
        self.action_packages = action_packages

    def first_download(self):
        for action in self.actions:
            if action.type in ["download_by_url", "download_file"]:
                return action
        return None

    def downloads(self):
        actions = []
        for action in self.actions:
            if action.type in ["download_by_url", "download_file"]:
                actions.append(action)
        return actions

    def __repr__(self):
        platform = ""
        if self.os or self.architecture:
            platform = "os=%s,arch=%s," % (self.os, self.architecture)
        return "Actions[%s%s]" % (platform, map(str, self.actions))


class Action(object):

    def __init__(self, **kwds):
        self._keys = []
        for key, value in kwds.iteritems():
            self._keys.append(key)
            setattr(self, key, value)

    def __repr__(self):
        return "Action[type=%s]" % self.type

    def same_as(self, other):
        if self._keys != other._keys:
            return False
        else:
            for key in self._keys:
                if getattr(self, key) != getattr(other, key):
                    return False

            return True

    def shell_command_to_ruby(self):
        command = self.command.strip()
        if "\n" in command:
            command = templatize_string(command)
            cmd_parts = [p.strip() for p in command.split("\n") if p]
            command = "\n".join(cmd_parts)
            return 'system <<-EOF\n%s\nEOF' % command
        else:
            shell_command = shell_string(self.command)
            return 'system %s' % shell_command

    def move_file_to_ruby(self):
        statements = []
        named_destination = self.named_dir(self.destination)
        if named_destination:
            args = (named_destination, shell_string(self.source))
            statements.append('%s.install %s' % args)
        else:
            shell_dest = shell_string(self.destination)
            shell_source = shell_string(self.source)
            statements.append('system "mkdir", "-p", %s' % shell_dest)
            statements.append('mv %s, %s' % (shell_source, shell_dest))
        return statements

    def move_directory_files_to_ruby(self):
        statements = []
        named_destination = self.named_dir(self.destination_directory)
        if named_destination:
            temp = '''%s.install Dir["%s/*"]'''
            statements.append(temp % (
                named_destination,
                shell_string(self.source_directory, quote_now=False))
            )
        else:
            shell_dest = shell_string(self.destination_directory)
            statements.append('''system "mkdir", "-p", %s''' % shell_dest)
            statements.append('''mv Dir["%s/*"], %s ''' % (
                shell_string(self.source_directory, quote_now=False),
                shell_string(self.destination_directory))
            )
        return statements

    def set_environment_to_ruby(self):
        statements = []
        modify_environment = []
        for variable in self.variables:
            if variable.explicit:
                modify_environment.append(variable)
            else:
                statements.append(UNNEEDED_SET_ENV)
        if modify_environment:
            list_str = '''['''
            for i, set_variable in enumerate(modify_environment):
                if i > 0:
                    list_str += ","
                list_str += set_variable.to_ruby_hash()
            list_str += ']'
            if self.package.has_multiple_set_environments():
                statements.append('environment_actions += %s' % list_str)
            else:
                statements.append('''environment(%s)''' % list_str)
            self.package.extensions_used.add('ENVIRONMENT')
        return statements

    def chmod_to_ruby(self):
        statements = []
        for mod in self.mods:
            target = shell_string(mod["target"])
            chmod_command = 'system "chmod", "%s", %s'
            statements.append(chmod_command, (mod["mode"], target))
        return statements

    def to_ruby(self):
        action_type = self.type
        statements = []
        if action_type == "shell_command":
            statements.append(self.shell_command_to_ruby())
        elif action_type == "move_file":
            statements.extend(self.move_file_to_ruby())
        elif action_type == "move_directory_files":
            statements.extend(self.move_directory_files_to_ruby())
        elif action_type == "set_environment":
            statements.extend(self.set_environment_to_ruby())
        elif action_type == "chmod":
            statements.extend(self.chmod_to_ruby())
        elif action_type == "make_install":
            statements.append('''system "make install"''')
        elif action_type == "download_file":
            resource = url_to_resource(self.text)
            statements.append("resource('%s').stage do" % resource)
            move_comment = ("Tool Shed would download inside build directory"
                            " instead of its own - so move download.")
            statements.append('''    # %s''' % move_comment)
            if self.extract:
                statements.append('''    buildpath.install Dir["../*"]''')
            else:
                statements.append('''    buildpath.install Dir["*"]''')
            statements.append("end")

        elif action_type == "change_directory":
            statements.append("cd '%s'" % self.directory)
        elif action_type == "make_directory":
            shell_dir = shell_string(self.directory)
            statements.append('system "mkdir", "-p", %s' % shell_dir)
        elif action_type == "setup_perl_environment":
            statements.append(self.unhandled_action(action_type))
        elif action_type == "setup_ruby_environment":
            statements.append(self.unhandled_action(action_type))
        elif action_type == "setup_python_environment":
            statements.append(self.unhandled_action(action_type))
        elif action_type == "setup_r_environment":
            statements.append(self.unhandled_action(action_type))
        elif action_type == "setup_virtualenv":
            statements.append(self.unhandled_action(action_type))
        else:
            statements.append(self.RAW_RUBY)

        return statements

    def unhandled_action(action_type):
        template = 'onoe("Unhandled tool shed action %s encountered.")'
        message = template % action_type
        return [message]

    def named_dir(self, path):
        ruby_path = shell_string(path, quote_now=False)
        if ruby_path == "#{prefix}":
            return "prefix"
        elif ruby_path == "#{prefix}/bin":
            return "bin"
        else:
            return None

    @property
    def explicit_variables(self):
        type = self.type
        if type == "set_environment":
            return filter(lambda v: v.explicit, self.variables)
        else:
            return []

    @classmethod
    def download_by_url_from_elem(clazz, elem):
        return {"text": elem.text}

    @classmethod
    def from_elem(clazz, elem, package):
        type = elem.attrib["type"]
        kwds = {}

        def parse_action_repo(elem):
            repo_elem = elem.find("repository")
            repo = Repo.from_xml(repo_elem)
            kwds["repo"] = repo

        def parse_package_elems(elem):
            package_els = elem.findall("package")
            packages = []
            for package_el in package_els:
                packages.append(package_el.text)
            kwds["packages"] = packages

        if type == "download_by_url":
            kwds.update(clazz.download_by_url_from_elem(elem))
        elif type == "download_file":
            kwds["text"] = elem.text
            kwds["extract"] = elem.attrib.get("extract", False)
        elif type == "shell_command":
            kwds["command"] = elem.text
        elif type == "move_file":
            kwds["source"] = elem.find("source").text
            kwds["destination"] = elem.find("destination").text
        elif type == "move_directory_files":
            source_directory = elem.find("source_directory").text
            destination_directory = elem.find("destination_directory").text
            kwds["source_directory"] = source_directory
            kwds["destination_directory"] = destination_directory
        elif type == "set_environment":
            variables = []
            for ev_elem in elem.findall("environment_variable"):
                var = SetVariable(ev_elem)
                variables.append(var)
            kwds["variables"] = variables
        elif type == "chmod":
            mods = []
            for mod_elem in elem.findall("file"):
                mod = {}
                mod["mode"] = mod_elem.attrib["mode"]
                mod["target"] = mod_elem.text
            kwds["mods"] = mods
        elif type == "make_install":
            pass
        elif type == "download_file":
            pass
        elif type == "change_directory":
            kwds["directory"] = elem.text
        elif type == "make_directory":
            kwds["directory"] = elem.text
        elif type == "setup_perl_environment":
            parse_action_repo(elem)
            parse_package_elems(elem)
        elif type == "setup_ruby_environment":
            parse_action_repo(elem)
            parse_package_elems(elem)
        elif type == "setup_python_environment":
            parse_action_repo(elem)
            parse_package_elems(elem)
        elif type == "setup_virtualenv":
            use_reqs = elem.attrib.get("use_requirements_file", "True")
            kwds["use_requirements_file"] = asbool(use_reqs)
            kwds["python"] = elem.get('python', 'python')
            # TODO: evaled
            kwds["requirements"] = elem.text or 'requirements.txt'
        elif type == "setup_r_environment":
            parse_action_repo(elem)
            parse_package_elems(elem)
        elif type == "set_environment_for_install":
            kwds["RAW_RUBY"] = ("# Skipping set_environment_for_install "
                                "command, handled by platform brew.")
        else:
            kwds["RAW_RUBY"] = ('onoe("Unhandled tool shed action [%s] '
                                'encountered.")' % type)

        return Action(type=type, package=package, **kwds)


class SetVariable(object):

    def __init__(self, elem):
        self.action = elem.attrib["action"]
        self.name = elem.attrib["name"]
        self.raw_value = elem.text
        self.ruby_value = templatize_string(self.raw_value)

    @property
    def explicit(self):
        return not self.implicit

    @property
    def implicit(self):
        if self.name == "PATH" and self.ruby_value == "#{prefix}/bin":
            return True
        else:
            return False

    def to_ruby_hash(self):
        action = self.action
        variable = self.name
        value = self.ruby_value.replace("#{prefix}", "$KEG_ROOT")
        if action == "set_to":
            action = "set"
        elif action == "prepend_to":
            action = "prepend"
        else:
            action = "append"
        template = '''{'action'=> '%s', 'variable'=> '%s', 'value'=> '%s'}'''
        return template % (action, variable, value)


def shell_string(tool_shed_str, quote_now=True, templatize=True):
    if templatize:
        target_string = templatize_string(tool_shed_str)
    else:
        target_string = tool_shed_str.replace("#", "\\#")
    to_ruby = (target_string.replace('"', '\\"'))
    if quote_now:
        return '"%s"' % to_ruby
    else:
        return to_ruby


def templatize_string(tool_shed_str):
    tool_shed_str.replace("#", "\\#")
    env_var_dict = {}
    env_var_dict['INSTALL_DIR'] = '#{prefix}'
    env_var_dict['system_install'] = '#{prefix}'
    # If the Python interpreter is 64bit then we can safely assume
    # that the underlying system is also 64bit.
    env_var_dict['__is64bit__'] = '#{Hardware.Hardware.is_64_bit?}'
    return string.Template(tool_shed_str).safe_substitute(env_var_dict)


class Package(object):

    def __init__(self, dependencies, package_el, install_el, readme):
        self.dependencies = dependencies
        self.package_el = package_el
        self.install_el = install_el
        self.readme = readme
        self.extensions_used = set()
        self.all_actions = self.get_all_actions()
        self.no_arch_option = self.has_no_achitecture_install()

    def get_all_actions(self):
        action_or_group = self.install_el[0]
        parsed_actions = []
        if action_or_group.tag == "actions":
            parsed_actions.append(self.parse_actions(action_or_group))
        elif action_or_group.tag == "actions_group":
            for actions in action_or_group.findall("actions"):
                parsed_actions.append(self.parse_actions(actions))
            for action in action_or_group.findall("action"):
                for parsed_a in parsed_actions:
                    parsed_a.actions.append(self.parse_action(action))
        return parsed_actions

    def to_recipe(self):
        name = self.get_recipe_name()
        formula_builder = FormulaBuilder()
        if self.has_explicit_set_environments():
            # Required for environment method.
            formula_builder.require('json')

        name = name.replace("__", "_")
        parts = [p[0].upper() + p[1:] for p in name.split("__")]
        temp = "|".join(parts)
        parts = [p[0].upper() + p[1:] for p in temp.split("_")]
        class_name = "".join(parts).replace("|", "_")
        formula_builder.set_class_name(class_name)
        repo = self.dependencies.repo
        url = "%s/%s/%s" % (repo.tool_shed_url, repo.owner, repo.name)
        line = "# Recipe auto-generate from repository %s" % url
        formula_builder.add_line(line)
        if self.readme:
            formula_builder.add_line("# Tool Shed Readme:")
            for line in self.readme.split("\n"):
                formula_builder.add_line("#    %s" % line)
        formula_builder.add_line("")
        formula_builder.add_line('option "without-architecture", "Build '
                                 'without allowing architecture information ('
                                 'to force source install when binaries are '
                                 'available)."')
        formula_builder.add_line("")
        self.pop_download_block(formula_builder)
        formula_builder.add_line("")
        self.pop_deps(formula_builder)
        self.pop_install_def(formula_builder)
        self.pop_extensions(formula_builder)
        formula_builder.finish_formula()
        return "%s.rb" % name, formula_builder.to_file()

    def get_recipe_name(self):
        repo = self.dependencies.repo
        base = repo.recipe_base_name()
        if self.dependencies.single_package():
            return base
        else:
            return base + self.package_el.attrib["name"]

    def pop_install_def(self, formula_builder):
        formula_builder.add_and_indent("def install")
        multiple_set_environments = self.has_multiple_set_environments()
        if multiple_set_environments:
            formula_builder.add_line("environment_actions = []")

        def handle_actions(actions):
            if not actions.actions:
                return

            first_action = actions.actions[0]
            for_pop = actions.actions
            if first_action.type in ["download_by_url", "download_file"]:
                for_pop = for_pop[1:]

            return self.populate_actions(formula_builder, for_pop)

        if self.actions_diff_only_by_download():
            handle_actions(self.all_actions[0])
        else:
            self.conditional_action_map(formula_builder, handle_actions)

        if multiple_set_environments:
            formula_builder.add_line('''environment(environment_actions)''')

        formula_builder.end()

    def pop_deps(self, formula_builder):
        def handle_actions(actions):
            return self.populate_actions_packages(
                formula_builder,
                actions.action_packages
            )

        self.populate_actions_packages(
            formula_builder,
            self.dependencies.dependencies
        )
        self.conditional_action_map(formula_builder, handle_actions)

    def pop_extensions(self, formula_builder):
        for extension in self.extensions_used:
            ext_def = globals()["EXTENSION_%s" % extension].split("\n")
            map(formula_builder.add_line, ext_def)

    def populate_actions_packages(self, formula_builder, packages):
        for package in packages:
            repo = package.repo
            prefix = self.dependencies.tap.prefix
            base = "%s/%s" % (prefix, repo.recipe_base_name())
            formula_builder.add_line('depends_on "%s"' % base)

    def populate_actions(self, formula_builder, actions):
        for action in actions:
            for line in action.to_ruby():
                formula_builder.add_line(line)

    def actions_diff_only_by_download(self):
        all_actions = self.all_actions
        first_actions = all_actions[0].actions
        for actions in all_actions[1:]:
            if len(first_actions) != len(actions.actions):
                return False
            for i, action in enumerate(actions.actions):
                download_action = action.type in ["download_by_url",
                                                  "download_file"]
                first_action = first_actions[0].type == action.type
                if download_action and first_action:
                    continue
                else:
                    if not action.same_as(first_actions[i]):
                        return False
        return True

    def pop_download_block(self, formula_builder):
        def func(actions):
            self.pop_download(actions, formula_builder)

        self.conditional_action_map(formula_builder, func)

    def conditional_action_map(self, formula_builder, func):
        all_actions = self.all_actions
        if len(all_actions) == 1:
            func(all_actions[0])
        else:
            self._complex_conditional(formula_builder, func)

    def _complex_conditional(self, formula_builder, func):
        all_actions = self.all_actions
        for i, actions in enumerate(all_actions):
            if i > 0:
                formula_builder.unindent()
            conds = []
            if actions.os and actions.os == "linux":
                conds.append("OS.linux?")
            elif actions.os and actions.os == "darwin":
                conds.append("OS.mac?")
            if actions.architecture and actions.architecture == "x86_64":
                conds.append("Hardware.is_64_bit?")
            elif actions.architecture and actions.architecture == "i386":
                conds.append("Hardware.is_32_bit?")
            if conds and self.no_arch_option:
                conds.append('!build.without?("architecture")')
            conds_str = " and ".join(conds)
            if not conds_str:
                assert i == len(all_actions) - 1, actions
                formula_builder.add_and_indent("else")
                func(actions)
            else:
                cond_op = "%sif" % ("" if i == 0 else "els")
                line = "%s %s" % (cond_op, conds_str)
                formula_builder.add_and_indent(line)
                func(actions)
        formula_builder.end()

    def has_no_achitecture_install(self):
        all_actions = self.all_actions
        if len(all_actions) < 2:
            return False
        else:
            last_action = all_actions[-1]
            return (not last_action.architecture) and (not last_action.os)

    def has_explicit_set_environments(self):
        all_actions = self.all_actions
        for actions in all_actions:
            for action in actions.actions:
                if action.explicit_variables:
                    return True
        return False

    def has_multiple_set_environments(self):
        all_actions = self.all_actions
        for actions in all_actions:
            count = 0
            for action in actions.actions:
                if action.explicit_variables:
                    count += 1
            if count > 1:
                return True
        return False

    def pop_download(self, actions, formula_builder):
        one_populated = False
        for action in actions.downloads():
            if one_populated:
                resource = url_to_resource(action.text)
                line = "resource '%s' do" % resource
                formula_builder.add_and_indent(line)
                self.pop_single_download(action, formula_builder)
                formula_builder.end()
            else:
                self.pop_single_download(action, formula_builder)
            one_populated = True
        if not one_populated:
            self.pop_single_download(None, formula_builder)

    def pop_single_download(self, action, formula_builder):
        if action is None:
            url = "http://ftpmirror.gnu.org/hello/hello-2.9.tar.gz"
            sha1 = "cb0470b0e8f4f7768338f5c5cfe1688c90fbbc74"
        else:
            url = action.text
            sha1 = self.fetch_sha1(url)
        download_line = '''url "%s"''' % url
        if action and action.type == "download_file" and not action.extract:
            download_line += ", :using => :nounzip"
        if action is None:
            formula_builder.add_line("# Each homebrew formula must have at "
                                     "least one download, tool shed doesn't "
                                     "require this so hacking in hello source"
                                     " download.")
        formula_builder.add_line(download_line)
        formula_builder.add_line('''sha1 "%s"''' % sha1)

    def fetch_sha1(self, url):
        return ''  # TODO

    def parse_actions(self, actions):
        os = actions.attrib.get("os", None)
        architecture = actions.get("architecture", None)
        parsed_actions = map(self.parse_action, actions.findall("action"))
        action_packages = []
        for package in actions.findall("package"):
            action_packages.append(self.parse_action_package(package))
        return Actions(parsed_actions, os, architecture, action_packages)

    def parse_action_package(self, elem):
        name = elem.attrib["name"]
        version = elem.attrib["version"]
        repo = Repo.from_xml(elem.find("repository"))
        return ActionPackage(name, version, repo)

    def parse_action(self, action):
        return Action.from_elem(action, package=self)

    def __repr__(self):
        actions = self.all_actions
        parts = (
            self.package_el.attrib["name"],
            self.package_el.attrib["version"],
            self.dependencies,
            actions
        )
        template = "Install[name=%s,version=%s,dependencies=%s,actions=%s]"
        return template % parts


class ActionPackage(object):

    def __init__(self, name, version, repo):
        self.name = name
        self.version = version
        self.repo = repo


class Repo(object):

    def __init__(self, **kwds):
        for key, value in kwds.iteritems():
            setattr(self, key, value)

    def recipe_base_name(self):
        owner = self.owner.replace("-", "")
        name = self.name
        name = name.replace("_", "").replace("-", "")
        base = "%s_%s" % (owner, name)
        return base

    @staticmethod
    def from_xml(elem):
        tool_shed_url = elem.attrib["toolshed"]
        if "testtoolshed" in tool_shed_url:
            prefix = "testtoolshed"
        else:
            prefix = "toolshed"
        prior = elem.attrib["prior_installation_required"]
        return Repo(
            prefix=prefix,
            name=elem.attrib["name"],
            owner=elem.attrib["owner"],
            tool_shed_url=tool_shed_url,
            changeset_revision=elem.attrib["changeset_revision"],
            prior_installation_required=prior,
        )

    @staticmethod
    def from_api(prefix, repo_json):
        return Repo(
            prefix=prefix,
            name=repo_json["name"],
            owner=repo_json["owner"],
            tool_shed_url=TOOLSHED_MAP[prefix],
        )

    def get_file(self, path):
        try:
            url_template = "%s/repos/%s/%s/raw-file/tip/%s"
            url = url_template % (
                self.tool_shed_url,
                self.owner,
                self.name,
                path
            )
            path, headers = urllib.urlretrieve(url)
            return path
        except Exception as e:
            print e
            return None

    def __repr__(self):
        return "Repository[name=%s,owner=%s]" % (self.name, self.owner)


def url_to_resource(url):
    path = urlparse.urlparse(url).path
    name = os.path.split(path)[1]
    base = name.rstrip("\.tar\.gz").rstrip("\.zip")
    return base


class RubyBuilder(object):

    def __init__(self):
        self.lines = []
        self.indent = 0

    def add_line(self, line):
        indent_spaces = "  " * self.indent
        self.lines.append("%s%s" % (indent_spaces, line))

    def add_and_indent(self, line):
        self.add_line(line)
        self.indent += 1

    def end(self):
        self.unindent()
        self.add_line("end")

    def unindent(self):
        self.indent -= 1

    def to_file(self):
        assert self.indent == 0, "\n".join(self.lines)
        return "\n".join(self.lines)

    def require(self, module):
        assert self.indent == 0
        self.add_line("require '%s'" % module)


class FormulaBuilder(RubyBuilder):

    def __init__(self):
        super(FormulaBuilder, self).__init__()
        self.require('formula')

    def set_class_name(self, name):
        self.add_line("")
        self.add_and_indent("class %s < Formula" % name)
        self.add_line('version "1.0"')

    def finish_formula(self):
        self.end()


def shell(cmds, **popen_kwds):
    click.echo(cmds)
    p = subprocess.Popen(cmds, shell=True, **popen_kwds)
    return p.wait()


def repos(tool_shed_url, name_filter=None, owner=None):
    ts = toolshed.ToolShedInstance(url=TOOLSHED)
    repos = ts.repositories.get_repositories()
    if owner:
        repos = [r for r in repos if r["owner"] == owner]
    if name_filter:
        pattern = re.compile(name_filter)
        repos = [r for r in repos if pattern.match(r["name"])]
    return repos


truthy = frozenset(['true', 'yes', 'on', 'y', 't', '1'])
falsy = frozenset(['false', 'no', 'off', 'n', 'f', '0'])


def asbool(obj):
    if isinstance(obj, basestring):
        obj = obj.strip().lower()
        if obj in truthy:
            return True
        elif obj in falsy:
            return False
        else:
            raise ValueError("String is not true/false: %r" % obj)
    return bool(obj)


if __name__ == "__main__":
    main()
