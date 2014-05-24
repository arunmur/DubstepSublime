DubstepSublime
==============

A Package for sublime to run your development machine in dubstep with sublime in your laptop/desktop.

<h2>Who is this for</h2>
This module is intended for folks who work in an environment where they have a
<ul>
<li>Laptop/Desktop running sublime</li>
<li>Server for running the code</li>
</ul>

This module allows you to keep the server in sync with your sublime at all times and allows you to run a few commands, such as restart apache or other services directly from your sublime.

This module is tested on Mac and should work on Linux.

<h2>How to use this</h2>
This package is not intended to be delivered as a fully packaged solution but rather as an reusable, extendable framework. Feel free to fork & modify according to your or your work environment needs. Out of the box this package provides two functionalities.
<ul>
<li>Restart apache.</li>
<li>It integrates into SublimeGit to keep your devbox in sync.</li>
</ul>

<h3>Installation</h3>
Fork this repository into your sublime's pacakges directory. You can find sublime packages dirctory by clicking on Preferences->Browse Pacakges....

<h3>Configuration</h3>
We need a working ssh keys configuration between your laptop/desktop and development machine for this modeule to work.

https://www.digitalocean.com/community/articles/how-to-set-up-ssh-keys--2

Create a file 'Dubstep.sublime-settings' in your sublime User directory. 

<b>Without SublimeGit autoupdate</b>

```JSON
{
  "remote" : {
    "host": "<hostname of your devbox(fqdn)>",
    "user": "<Which user to connect with>",
    "port": "<specify if you use a custom port for sshd>",
    "home": "<directory where the code is in remote machine>"
  },
}
```

<b>With SublimeGit autoupdate</b> - The sample is in 'Dubstep.sublime-settings' file, provided in the repo. 

```JSON
{	
	"remote": {
        "host": "<hostname of your devbox(fqdn)>",
        "user": "<Which user to connect with>",
        "port": "<specify if you use a custom port for sshd>",
        "home": "<directory where the code is in remote machine>"
	},
	"autoupdate":  [
		{
			"on_command" : "git_push_current_branch",
			"commands": [
				{
					"type": "ssh",
					"description": "Git pull",
					"run": "sleep 10 && git pull"
				}
			]
		},
		{
			"on_command" : "git_checkout_branch",
			"commands": [
				{
					"type": "ssh",
					"description": "Cheking out branch in remote",
					"run": "git checkout . && sleep 10 && git checkout ##GIT_BRANCH##"
				}
			]
		}
	]
}

```
<h2>Customisations</h2>
All customisations using this package can be performed with three types of files
<ul>
<li>settings - Dubstep.sublime-settings file(in sublime User directory)</li>
<li>commands - Dubste.sublime-commands file(in sublime User directory)</li>
<li>sublime python modules</li>
</ul>

The center of the DubstepSublime package/module is the <b>dubstep_run</b> command. To create custom commands, create a file called 'Dubstep.sublime-commands' on your sublime's User directory. 

Every command has the following structure.

```JSON
{
	"caption": "<Name of your command>",
	"command": "dubstep_run",
	"args" : {
		"commands": [
			{
				"type": "<ssh|scp>",
				"description": "<Some description>",
				"run": "<command to run on the remote>"
			}
		],
		"output_to_view": {
		  "syntax_file": "<path to syntax file>"
		}
	}
}
```
See 'Dubstep.sublime-commands' provided in the repository for examples. The args provided to dubstep_run has two parts
<ul>
<li>command - what to run</li>
<li>output - what to do with the output of the command</li>
</ul>

<h3>Commands: </h3>
The dubstep_run command takes an array of comands, run in sequence.

<b>ssh command</b>
```JSON
{
  ...
  "args": {
    "commands": [
      {
        "type": "ssh",
        "description": "Generated reports",
        "run": "ls /var/reports/Generated"
    ]
  }
}
```
This runs 'ls /var/reports/Generated' on the remote machine.

<b>scp command</b>
```JSON
{
  ...
  "args": {
    "commands": [
      {
        "type": "scp",
        "description": "Copy CSV files",
        "file": "/tmp/in.csv"
      }
    ]
  }
}
```

This copies /tmp/in.csv from your laptop to remote machine.


<h3>Output</h3>
When no option is provided, output is ignored. Error messages always come on a popup. But output of your set of commands can be captured and displayed to the user

<table>
<tr><td>output_to_view</td><td>A temporary view will be opened to display the output of the command. optionally syntax_file for the output can be sepecified</td></tr>
<tr><td>output_to_dialog</td><td>The output will be displayed on a dialog</td></tr>
</table>

<b>A more complete example</b>
```JSON
{
  ...
  "args": {
    "commands": [
      {
        "type": "scp",
        "description": "Copy CSV files",
        "file": "/tmp/in.csv"
      },
      {
        "type": "ssh",
        "description": "Generate report files",
        "run": "/usr/bin/generate_report -i /tmp/in.csv -o /tmp/out.csv"
      },
      {
        "type": "ssh",
        "description": "Get output",
        "run": "cat /tmp/out.csv"
      },
    ],
    "output_to_view": 1
  }
}
```

<h3>Placeholders</h3>
There are a few bulit-in place holders available, for the 'run' or 'file' argument in the command.
<table>
<tr><td>##FILE##</td><td>represents the current file</td></tr>
<tr><td>##FILE_IN_REMOTE##</td><td>represents the current file in remote machine(home should be specified in settings file)</td></tr>
</table>

More custom place holders can be provided in the <b>Dubstep.sublime-settings</b> file. Placeholders will run a command in your laptop/desktop and send it as an argument to the remote.

```JSON
{
...
  "placeholders" : [
    {"BRANCH" : "git rev-parse --abbrev-ref HEAD"},
    {"HOSTNAME" : "hostname -f"}
  ]
}
```

now, the command

```JSON
{
...
  "commands": [
    {
      "type" : "ssh"
      "run" : "git checkout ##BRANCH##"

  }
  ]
}
```
will run as "git checkout master" on the remote machine, assuming you have checkout master on sublime.

<h3>Autoupdate</h3>
The autoupdate command provided in <b>Dubstep.sublime-settings</b> file is used to run a command on trigger of another sublime window command. We use this to keep our git always upto date on our devbox. There are two parts to these commands. the trigger 'on_command' and 'commands', which is  a debstep_run command. To find the sublime command on which you want to run somethinng, on the sublime's console type 

```
sublime.log_commands(True)
```

It will show all the commands as you use sublime. When you find your command your configuration will look like this.
```JSON
{
  ...
  "autoupdate": [
    {
      "on_command": "<the command you found>",
      "commands" [
          ...
      ]
    }
  ]
}
```

The commands here follow the same structure as commands in the sublime-commands file.

<h3>Sublime Python Modules</h3>
Writing Sublime Python Modules is out of scope of this package. To read how to write one see below
http://code.tutsplus.com/tutorials/how-to-create-a-sublime-text-2-plugin--net-22685

However if you knew how to write the modeule, then dubstep_run command with all the above features is available to be called from the module. The dubstep_run will always run as a seperate thread.
