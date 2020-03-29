import React from 'react';

class SettingsPage extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      eyeTrackingOn: false,
      leftCalibrated: false,
      rightCalibrated: false, 
    }
    this.toggleEyeOS = this.toggleEyeOS.bind(this);
    this.processLog = this.processLog.bind(this);
  }

  componentDidMount() {
    this.ipc = window.ipcRenderer;
  }

  toggleEyeOS() {
    window.ipcRenderer.on("eyeOS-startup-log", (event, arg) => {
      if(arg.err) console.log(arg.err);
      else this.processLog(arg.msg);
    })
    window.ipcRenderer.on("eyeOS-kill", (event, arg) => {
      console.log("Turned off eyeOS")
      this.setState({
        eyeTrackingOn: false
      })
    })
    window.ipcRenderer.on("eyeOS-started", (event, arg) => {
      console.log("eyeOS started")
      this.setState({
        eyeTrackingOn: true
      })
    })
    if(!this.state.eyeTrackingOn) {
      window.ipcRenderer.send('start-eyeOS', true);
      this.props.alert("Starting", "Enabling EyeOS")
    } else {
      window.ipcRenderer.send('stop-eyeOS', true)
    }
  }

  processLog(log) {
    if(log.includes("Booting EyeOS")) {
      this.props.alert("Starting", "Enabling EyeOS")
    } else if(log.includes("Look at the top left")) {
      this.props.alert("Calibrating", "Look at the top left of your screen and blink");
    } else if(log.includes("Look at the bottom right")) {
      this.props.alert("Calibrating", "Look at the bottom right of your screen and blink");
    } else if(log.includes("Saved Top Left")) {
      let newState = Object.assign({}, this.state);
      newState.leftCalibrated = true;
      this.setState(newState);
    } else if(log.includes("Saved Bottom Right")) {
      let newState = Object.assign({}, this.state);
      newState.leftCalibrated = true;
      this.setState(newState);
      this.props.disableAlert();
    }
  }

  render() {
    return (
      <div className="relative p-8 text-white pb-12">
        <div className="text-3xl font-bold">Settings</div>
        <div className="text-lg text-gray-200 -my-1">Configure settings for eye tracking</div>
        <div className="mt-4 p-4 rounded-md bg-secondary block max-w-xl">
          <div className="text-xl font-bold">Eye Tracking</div>
          <div className="mb-2">
            Start using EyeOS's eye tracking for motion control! Please follow the onscreen prompts when calibrating.
            You can recalibrate by saying "recalibrate"
          </div>
          <button onClick={this.toggleEyeOS} className={(!this.state.eyeTrackingOn ? "bg-green-500 hover:bg-green-700" : "bg-red-500") +  " text-white font-medium hover:shadow-xl duration-200 py-2 px-4 rounded outline-none focus:outline-"}>{this.state.eyeTrackingOn ? "Disable" : "Enable"}</button>
        </div>
        <div className="mt-4 p-4 rounded-md bg-secondary block max-w-xl">
          <div className="text-xl font-bold">Text To Speech</div>
          <div className="mb-2">
            Use Text to Speech as keyboard input source! Speak to type words into your computer hands free!
          </div>
          <button className="bg-green-500 hover:bg-green-700 text-white font-medium hover:shadow-xl duration-200 py-2 px-4 rounded outline-none focus:outline-none">Enable</button>
        </div>
      </div>
    );
  }
}

export default SettingsPage;