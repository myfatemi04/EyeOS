const {PythonShell} = require('python-shell');
const path = require("path")

class EyeOS {
  start(event) {
    let options = {}
    if(process.platform === 'darwin' || process.platform === '') {
      options = {
        pythonPath: '/usr/bin/python3',
        pythonOptions: ['-u'],
      }
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
        event.reply('eyeOS-startup-log', {
          err: "An error occured"
        });
        console.log(err);
      }
      console.log("finished");
    })
  }

  kill(event) {
    if(this.python_process) {
      this.python_process.kill('SIGINT');
      this.python_process = null;
      event.sender.send('eyeOS-kill', true);
    }
  }

  get isOn() {
    return true && this.python_process;
  }
}

module.exports = EyeOS;