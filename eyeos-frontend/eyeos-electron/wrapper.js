const {PythonShell} = require('python-shell');
const path = require("path")

class EyeOS {

  constructor(typing=false) {
    this.typing = typing
  }

  start(event) {
    let options = {}
    if(process.platform === 'linux') {
      console.log("using a manual path to python3")
      options = {
        pythonPath: '/usr/bin/python3',
        pythonOptions: ['-u'],
      }
      options.args = [this.typing ? 'typing' : 'notyping']
    }

    if(process.platform === 'darwin') {
      console.log("using a manual OSX path to python3")
      options = {
        pythonPath: '/usr/local/bin/python3',
        pythonOptions: ['-u'],
      }
      options.args = ['notyping']
    }
  
    let pyshell = new PythonShell(path.join(__dirname, "../../EyeTracker/main.py"), options);
    this.python_process = pyshell.childProcess;
    
    pyshell.on('message', (message) => {
      console.log(message);
      event.sender.send('eyeOS-startup-log', {
        msg: message
      })
    })
  
    pyshell.end((err) => {
      if(err) { 
        event.sender.send('eyeOS-startup-log', {
          err: "An error occured"
        });
        console.log(err);
      } else {
        event.sender.send('eyeOS-startup-log', {
          msg: "finished"
        })
      }
    })
  }

  kill() {
    if(this.python_process) {
      this.python_process.kill('SIGINT');
      this.python_process = null;
    }
  }

  restart(mode, event) {
    this.typing = mode;
    this.kill();
    this.start(event);
  }

  get isOn() {
    return (this.python_process !== undefined && this.python_process !== null)
  }
}

module.exports = {EyeOS};