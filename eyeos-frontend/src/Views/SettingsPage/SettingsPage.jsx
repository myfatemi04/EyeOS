import React from 'react';

class SettingsPage extends React.Component {


  constructor(props) {
    super(props)
    this.state = {
      eyeTrackingOn: false,
      sttOn: false,
      leftCalibrated: false,
      rightCalibrated: false, 
      errorEye: false,
      errorSTT: false,
    }
    this.toggleEyeOS = this.toggleEyeOS.bind(this);
    this.toggleSTT = this.toggleSTT.bind(this);
    this.processEyeOSLog = this.processEyeOSLog.bind(this);
    this.processSTTLog = this.processEyeOSLog.bind(this);
  }

  componentDidMount() {
    this.ipc = window.ipcRenderer;
    this.ipc.on("eyeOS-startup-log", (event, arg) => {
      if(arg.err && this.state.eyeTrackingOn) {
        this.props.disableAlert();
        let newState = Object.assign({}, this.state);
        newState.errorEye = true;
        this.setState(newState)
      } else this.processEyeOSLog(arg.msg);
    })
    this.ipc.invoke("eyeOS-on", true)
      .then((res) => {
        let newState = Object.assign({}, this.state);
        newState.eyeTrackingOn = res;
        this.setState(newState)
      });

    this.ipc.on("stt-startup-log", (event, arg) => {
      if(arg.err && this.state.sttOn) {
        this.props.disableAlert();
        let newState = Object.assign({}, this.state);
        newState.errorSTT = true;
        this.setState(newState)
      } else this.processSTTLog(arg.msg);
    })
    this.ipc.invoke("stt-on", true)
      .then((res) => {
        let newState = Object.assign({}, this.state);
        newState.sttOn = res;
        this.setState(newState)
      });
  }

  componentWillUnmount() {
    this.disableListeners();
  }

  disableListeners() {
    this.ipc.removeAllListeners("eyeOS-startup-log");
  }

  toggleEyeOS() {
    let newState = Object.assign({}, this.state);
    newState.errorEye = false;
    this.setState(newState);
    if(!this.state.eyeTrackingOn) {
      this.ipc.invoke('start-eyeOS');
    } else {
      this.props.disableAlert()
      this.ipc.invoke('stop-eyeOS');
      let newState = Object.assign({}, this.state);
      newState.eyeTrackingOn = false
      this.setState(newState)
    }
    
    newState.eyeTrackingOn = !newState.eyeTrackingOn;
    this.setState(newState)
  }

  toggleSTT() {
    let newState = Object.assign({}, this.state);
    newState.errorSTT = false;
    this.setState(newState);
    if(!this.state.sttOn) {
      this.ipc.invoke('start-stt', false);
    } else {
      this.props.disableAlert()
      this.ipc.invoke('stop-stt');
      let newState = Object.assign({}, this.state);
      newState.sttOn = false
      this.setState(newState)
    }
    
    newState.sttOn = !newState.sttOn;
    this.setState(newState)
  }

  processEyeOSLog(log) {
    if(this.state.eyeTrackingOn) {
      if(log.includes("Booting EyeOS")) {
        this.props.alert("Starting", "Enabling EyeOS")
      } else if(log.includes("Look at the top left")) {
        this.props.alert("Calibrating", "Look at the top left of your screen and say \"ready\"");
      } else if(log.includes("Look at the bottom right")) {
        this.props.alert("Calibrating", "Look at the bottom right of your screen and say \"ready\"");
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
  }

  processSTTLog(log) {

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
          <button 
            onClick={this.toggleEyeOS} 
            className={(!this.state.eyeTrackingOn ? "bg-green-500 hover:bg-green-700" : "bg-red-500") +  " text-white font-medium hover:shadow-xl duration-200 py-2 px-4 rounded outline-none focus:outline-"}
          >
            {this.state.errorEye ? "ERROR" : this.state.eyeTrackingOn ? "Disable" : "Enable"}
          </button>
        </div>
        <div className="mt-4 p-4 rounded-md bg-secondary block max-w-xl">
          <div className="text-xl font-bold">Speech To Text</div>
          <div className="mb-2">
            Use speech-to-text as a keyboard input source! Speak to type words into your computer hands free!
          </div>
          <button 
            onClick={this.toggleSTT}  
            className={(!this.state.sttOn ? "bg-green-500 hover:bg-green-700" : "bg-red-500") +  " text-white font-medium hover:shadow-xl duration-200 py-2 px-4 rounded outline-none focus:outline-"}
          >
            {this.state.errorSTT ? "ERROR" : this.state.sttOn ? "Disable" : "Enable"}
          </button>
        </div>
      </div>
    );
  }
}

export default SettingsPage;