import sublime, sublime_plugin
from subprocess import call, check_output
import threading
import os
import tempfile
import re

class AutoUpdateCommand(sublime_plugin.EventListener):
	def on_window_command(self, window, command_name, args):
		auto_update_triggers = sublime.load_settings('Dubstep.sublime-settings').get('autoupdate')
		if auto_update_triggers  is None or not isinstance(auto_update_triggers, list):
			return

		for trigger in auto_update_triggers:
			if command_name == trigger['on_command']:
				window.active_view().run_command('dubstep_run', trigger['commands'])

class DubstepRunCommand(sublime_plugin.TextCommand):
	def run(self, edit, name=None, commands=None,output_to_view=None,output_to_dialog=None):
		self.commands = commands
		self.output_to_view = output_to_view	
		self.output_to_dialog = output_to_dialog
		self.name = name

		if commands is not None:
			th = DubstepRunThread(commands=commands, filename=self.view.file_name(), on_failure=self.run_failed, on_success=self.run_success)
			th.start()

	def run_failed(self, message):
		if self.name is not None:
			sublime.error_message("Failed to run command(" + self.name + "): \n" +  message)
		else:
			sublime.error_message("Failed to run command: \n" +  message)

	def run_success(self, message):
		if self.output_to_view is not None:
			view = sublime.active_window().new_file()
			view.set_scratch(True)
			if(self.name):
				view.set_name("**dubstep-run**#" + self.name)
			else:
				view.set_name("**dubstep-run**" )
			view.run_command('append', {'characters':message})
			if isinstance(self.output_to_view, dict) and 'syntax_file' in self.output_to_view:
				view.set_syntax_file(self.output['syntax_file'])
		elif self.output_to_dialog is not None:
			sublime.message_dialog(message);


class DubstepRunThread(threading.Thread):
	def __init__(self, commands=None, filename=None, on_success=None, on_failure=None):
		self.commands = commands
		self.on_success = on_success
		self.on_failure = on_failure
		self.filename = filename
		threading.Thread.__init__(self)

	def run(self):
		if self.commands is None or not isinstance(self.commands, list):
			sublime.error_message("No command given to run")
			return

		out = tempfile.NamedTemporaryFile(delete=True)
		err = tempfile.NamedTemporaryFile(delete=True)
		try:
			for command in self.commands:
				if 'description' in command:
					sublime.status_message("Running : " + command['description'])

				sublime.message_dialog(DubstepCommand(filename=self.filename).resolve_command(command))
				status = call(DubstepCommand(filename=self.filename).resolve_command(command), shell=True, stderr=err, stdout=out)
				if int(status) != 0 and self.on_failure is not None:
					err = open(err.name, 'r')
					self.on_failure(err.read())
					return

			if self.on_success is not None:
				out = open(out.name, 'r')
				self.on_success(out.read())

		except OSError as e:
			if self.on_failure is not None:
				self.on_failure(str(e))
		except Exception as e:
			if self.on_failure is not None:
				self.on_failure(str(e))
		finally:
			out.close()
			err.close()

class DubstepCommand:
	def __init__(self, filename=None):
		self.filename = filename
		settings = sublime.load_settings('Dubstep.sublime-settings')
		self.remote = settings.get('remote')
		self.placeholders = settings.get('placeholders')
		self.file_in_remote_re = re.compile('##FILE_IN_REMOTE##')
		self.file_re = re.compile('##FILE##')


	def resolve_command(self, command):
		if 'host'  not in self.remote:
			raise Exception("Error: Dubstep remote host isn't configured.")
			
		if  'type' not in command:
			raise Exception("type for command not priovided")

		if command['type'] == 'ssh':
			if  'run' not in command:
				raise Exception("run parameter for command not provided")
			return self.ssh_command(command['run'])

		elif command['type'] == 'scp':
			if  'file' not in command:
				raise Exception("file parameter for command not provided")
			return self.scp_command(command['file'])
		
		raise Exception("Command type " + command['type'] + " is not known")


	def ssh_command(self, run):
		ssh_command = "ssh"
		if  'port'  in self.remote:
			ssh_command += " -p " + self.remote['port']
		ssh_command += " " + self.remote['user'] + '@' + self.remote['host']	
		return ssh_command + " '" + self.replace_placehoders(run) + "'"

	def scp_command(self, filename):
		scp_command = "scp"
		if  'port'  in self.remote:
			scp_command += " -P " + self.remote['port']
		return scp_command + " " + filename + " " + self.remote['user'] + '@' + self.remote['host'] + self.replace_placehoders(filename)

	def replace_placehoders(self, command):
		command = command.replace('##FILE##', self.filename)
		command = command.replace('##FILE_IN_REMOTE##', self.file_in_remote())

		for placeholder in self.placeholders:
			replace = list(placeholder)[0]
			replace_with = self._get_output_of(placeholder[replace])
			command = command.replace("##" + replace + "##", replace_with)

		return command

	def _get_output_of(self, command):
		out = tempfile.NamedTemporaryFile(delete=True)
		status = call(command, shell=True, stdout=out)
		if(int(status) == 0):
			out = open(out.name, 'r')
			output =  out.read()
			out.close()
			return output.rstrip()

		return "";

	def file_in_remote(self):
		filename = self.filename
		current_directory = os.getcwd()
		filename = os.path.relpath(filename, current_directory)
		repo_dir = self.remote['home']
		return repo_dir + '/' + filename.replace("\\", "/")
		


