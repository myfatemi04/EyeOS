const {PythonShell} = require('python-shell');
const path = require("path")

class EyeOS {
  start(event) {
    let options = {}
    if(process.platform === 'darwin' || process.platform === 'linux') {
      console.log("using a manual path to python3")
      options = {
        pythonPath: '/usr/bin/python3',
        pythonOptions: ['-u'],
      }
      options.args = ['eye']
    }
  
    console.log(path.join(__dirname, "../../EyeTracker/main.py"))
    let pyshell = new PythonShell(path.join(__dirname, "../../EyeTracker/main.py"), options);
    this.python_process = pyshell.childProcess;
    event.sender.send('eyeOS-started', true);
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
      }
      console.log("finished eyeOS");
    })
  }

  kill() {
    if(this.python_process) {
      this.python_process.kill('SIGINT');
      this.python_process = null;
    }
  }

  get isOn() {
    return (this.python_process !== undefined && this.python_process !== null)
  }
}

class SpeechToText {
  start(launcherEnabled, event) {
    let options = {}
    if(process.platform === 'darwin' || process.platform === 'linux') {
      console.log("using a manual path to python3")
      options = {
        pythonPath: '/usr/bin/python3',
        pythonOptions: ['-u'],
      }
      options.args = (launcherEnabled) ? ['stt', '1'] : ['stt', 0]
    }
  
    console.log(path.join(__dirname, "../../EyeTracker/main.py"))
    let pyshell = new PythonShell(path.join(__dirname, "../../EyeTracker/main.py"), options);
    this.python_process = pyshell.childProcess;
    event.sender.send('stt-started', true);
    pyshell.on('message', (message) => {
      console.log(message);
      event.sender.send('stt-startup-log', {
        msg: message
      })
    })
  
    pyshell.end((err) => {
      if(err) { 
        event.sender.send('stt-startup-log', {
          err: "An error occured"
        });
        console.log(err);
      }
      console.log("finished stt");
    })
  }

  kill() {
    if(this.python_process) {
      this.python_process.kill('SIGINT');
      this.python_process = null;
    }
  }

  get isOn() {
    return (this.python_process !== undefined && this.python_process !== null)
  }
}

module.exports = {EyeOS, SpeechToText};