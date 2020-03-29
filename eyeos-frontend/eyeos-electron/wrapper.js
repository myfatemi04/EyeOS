const { PythonShell } = require('python-shell');
const path = require("path")


let opt = {}
if (process.platform === 'linux') {
  console.log("using a manual path to python3")
  opt = {
    pythonPath: '/usr/bin/python3',
    pythonOptions: ['-u'],
  }
}

if (process.platform === 'darwin') {
  console.log("using a manual OSX path to python3")
  opt = {
    pythonPath: '/usr/local/bin/python3',
    pythonOptions: ['-u'],
  }
}


class EyeOS {

  constructor(typing = false) {
    this.typing = typing
  }

  start(event) {
    let options = Object.assign({}, opt);
    let pyshell = new PythonShell(path.join(__dirname, "../../EyeTracker/main.py"), options);
    this.python_process = pyshell.childProcess;

    options.args = [this.typing ? 'typing' : 'notyping']


    pyshell.on('message', (message) => {
      console.log(message);
      event.sender.send('eyeOS-startup-log', {
        msg: message
      })
    })

    pyshell.end((err) => {
      if (err) {
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
    if (this.python_process) {
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

function getAppList(search = "") {
  return new Promise(resolve => {
    let options = Object.assign({}, opt);
    options.args = [search]
    console.log(options.args)

    let pyshell = new PythonShell(path.join(__dirname, "../../EyeTracker/start_menu_to_node.py"), options);
    let process = pyshell.childProcess;
    console.log(pyshell.command)
    let appList = [];

    pyshell.on('message', (message) => {
      let [name, path] = message.split('<>');
      // console.log("Found app:" + name + ", at path:" + path);
      appList.push({ name: name, path: path });
    })

    pyshell.end((err) => {
      if (err) console.log(err)
      scriptFinished = true
      resolve(appList)
    })
  })
}

module.exports = { EyeOS, getAppList };