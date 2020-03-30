import React from 'react';
import './AppLauncherPage.scss'

class AppLauncherPage extends React.Component {

  constructor(props) {
    super(props)
    this.state = { value: '', appList: [], searchList: [] }

    this.handleAppNameChange = this.handleAppNameChange.bind(this)
    this.getAppList = this.getAppList.bind(this)
  }

  async componentDidMount() {
    this.ipc = window.ipcRenderer;
    let newState = Object.assign({}, this.state);
    newState.appList = await this.ipc.invoke('get-app-list', this.state.value)
    newState.searchList = newState.appList;
    this.setState(newState);
  }

  getAppList(name) {
    console.log(name)
    let newSearchList = [];
    this.state.appList.forEach((val, _) => {
      if(val.name.indexOf(name) == 0)
        newSearchList.push(val);
    })
    return newSearchList;
  }

  async handleAppNameChange(event) {
    let newState = Object.assign({}, this.state);
    newState.value = event.target.value;
    newState.searchList = this.getAppList(event.target.value);
    console.log(newState)
    this.setState(newState)
  }


  render() {
    return (
      <div className="relative p-8 text-white pb-24">
        <div className="text-3xl font-bold">App Launcher</div>
        <div className="text-lg text-gray-200 -my-1">Open apps using voice commands!</div>
        <div className="mt-4 p-4 rounded-md bg-secondary block max-w-xl">
          <div className="text-xl font-bold">How do I do this?</div>
          <div className="mb-2">
            Go to settings, and enable either "Eye Tracking" or "Speech to Text". Then, look at the menu below for keywords to open different apps.
          </div>
          <div className="-mt-2">
            Say <span className="text-green-200 font-bold">"open"</span>, <span className="text-green-200 font-bold">"run"</span>, or <span className="text-green-200 font-bold"> "play"</span> + a keyword from the menu below to start.
          </div>
          <div className="font-bold">Example: <span className="text-green-200">open </span> <span className="text-orange-400">chrome</span></div>
        </div>
        <div className="mt-4 p-4 rounded-md bg-secondary block max-w-xl">
          <div className="text-xl font-bold">Apps</div>
          <div className="mb-2">
            <input
              value={this.state.value}
              onChange={this.handleAppNameChange}
              className="transition-colors duration-100 ease-in-out focus:outline-none block w-full appearance-none leading-normal rounded-md h-10 mt-2 card-bg shadow-md px-4"
              placeholder="Search for an app"
            />
            <div className="w-full mt-4 card-bg p-4 rounded-md shadow-md">
              <div className="font-bold mb-1">App</div>
              {this.state.searchList.map((value, _) => {
                return (
                  <React.Fragment key={value.name}>
                    <div className="font-medium text-gray-200">{value.name}</div>
                    <div className="text-xs -mt-1 mb-1">{value.path}</div>
                  </React.Fragment>
                )
              })}
            </div>
          </div>
        </div>
      </div>
    );
  }
}

export default AppLauncherPage;