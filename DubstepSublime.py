import sublime, sublime_plugin
from subprocess import call, check_output
import threading
import os
import tempfile
import re

class RepoAutoUpdateCommand(sublime_plugin.EventListener):
	def on_window_command(self, window, command_name, args):
		auto_update_triggers = sublime.load_settings('Dubstep.sublime-settings').get('repo_autoupdate')
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
			th = DubstepRunThread(commands=commands, on_failure=self.run_failed, on_success=self.run_success)
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
		self.settings = sublime.load_settings('Dubstep.sublime-settings').get('remote')
		self.git_branch_placeholder_re = re.compile('##GIT_BRANCH##')
		self.current_file_placeholder_re = re.compile('##FILE##')
		self.filename = filename
		threading.Thread.__init__(self)

	def run(self):
		if self.commands is None or not isinstance(self.commands, list):
			sublime.error_message("No command given to run")
			return

		if not 'host' in self.settings:
			sublime.error_message("Error: DubstepSublime ssh host isn't configured.")
			return

		out = tempfile.NamedTemporaryFile(delete=True)
		err = tempfile.NamedTemporaryFile(delete=True)
		try:
			for command in self.commands:
				if 'description' in command:
					sublime.status_message("Running : " + command['description'])

				if  'type' not in command:
					sublime.error_message("type for command not priovided")
					return

				if command['type'] == 'ssh':
					if  'run' not in command:
						sublime.error_message("run parameter for command not provided")
						return

					status = call(self._ssh_command(command['run']), shell=True, stderr=err, stdout=out)
				elif command['type'] == 'scp':
					if  'file' not in command:
						sublime.error_message("file parameter for command not provided")
						return

					status = call(self._scp_command(command['file']), shell=True, stderr=err, stdout=out)
				else:
					sublime.error_message("Command type " + command['type'] + " is not known")
					return

				if int(status) != 0 and self.on_failure is not None:
					err = open(err.name, 'r')
					self.on_failure(err.read())
					return


			if self.on_success is not None:
				out = open(out.name, 'r')
				self.on_success(out.read())

			out.close()
			err.close()
		except OSError as e:
			if self.on_failure is not None:
				self.on_failure(str(e))

	def replace_placehoders(self, command):
		if(self.git_branch_placeholder_re.match(command)):
			command  = command.replace('##GIT_BRANCH##', self.get_current_branch())

		if(self.current_file_placeholder_re.match(command)):
			current_directory = os.getcwd()
			filename = os.path.relpath(self.filename, current_directory)
			repo_dir = this.settings['home']
			filename = filename.replace("\\", "/")
			command = command.replace('##FILE##', repo_dir + '/' + filename)

		return command

	def get_current_branch(self):
		return check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])

	def _ssh_command(self, run):
		ssh_command = "ssh"
		if  'port'  in self.settings:
			ssh_command += " -p " + self.settings['port']
		ssh_command += " " + self.settings['user'] + '@' + self.settings['host']	
		return ssh_command + " '" + self.replace_placehoders(run) + "'"

	def _scp_command(self, filename):
		scp_command = "ssh"
		if  'port'  in self.settings:
			scp_command += " -P " + self.settings['port']
		return scp_command + " " + filename + " " + self.settings['user'] + '@' + self.settings['host'] + self.replace_placehoders(command) 	