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
    "port": "<specify if you use a custom port for sshd>"
  },
}
```

<b>With SublimeGit autoupdate</b> - The sample is in 'Dubstep.sublime-settings' file, provided in the repo. 

```JSON
{	
	"remote": {
    "host": "<hostname of your devbox(fqdn)>",
    "user": "<Which user to connect with>",
    "port": "<specify if you use a custom port for sshd>"
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
<h3>Customisations</h3>
The center of the package/module is the <b>dubstep_run</b> command. You can run create a file called 'Dubstep.sublime-commands' on your sublime's User directory to create custom commands. You can see the file provided for a sample.

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
				"run": "<command to run on the devbox>"
			}
		],
		"output_to_view": {
		  "syntax_file": "<path to syntax file>"
		}
	}
}
```

<b>Commands: </b>The dubstep_run command takes an array of comands, run in sequence. <br />

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
This runs 'ls /var/reports/Generated' on your development machine.

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

This copies /tmp/in.csv from your laptop to development machine.

<b>Placeholders</b>There are a few place holders available, for the 'run' or 'file' argument in the command.
<table>
<tr><td>##FILE##</td><td>represents the current file</td></tr>
<tr><td>##GIT_BRANCH##</td><td>represents the current git branch</td></tr>
</table>

<b>Output</b> When no option is provided, output is ignored. Error messages always come on a popup. But output of your set of commands can be captured and displayed to the user

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

<b>autoupdate customisation</b>
The autoupdate command provided in Dubstep.sublime-settings file is used to run a command on trigger of another sublime window command. We use this to keep our git always upto date on our devbox. There are two parts to these commands. the trigger 'on_command' and 'commands', which is  a debstep_run command. To find the sublime command on which you want to run somethinng, on the sublime's console type 

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
