import React from 'react';
import { Route } from "react-router-dom";
import './AppContent.scss';
import BottomNavbar from '../../Components/BottomNavbar/BottomNavbar';
import SettingsPage from '../SettingsPage/SettingsPage';
import BackArrow from './svg/arrow_back.svg';

class AppContent extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      alertEnabled: false,
      alertTitle: "",
      alertText: "",
    }
    this.alert = this.alert.bind(this);
    this.disableAlert = this.disableAlert.bind(this);
  }

  alert(title, text) {
    this.setState({
      alertEnabled: true,
      alertTitle: title,
      alertText: text
    })
  }

  disableAlert() {
    this.setState({
      alertEnabled: false,
      alertTitle: "",
      alertText: ""
    });
  }

  render() {
    let alert;
    if(this.state.alertEnabled) {
      alert = (
        <div className="alert-overlay w-full h-full pointer-events-none fixed z-40">
          <div className="flex items-center w-full h-full">
            <div className="alert-box bg-secondary m-auto rounded-lg p-6">
              <div className="text-2xl font-medium text-center">{this.state.alertTitle}</div>
              <div className="text-lg text-center">{this.state.alertText}</div>
            </div>
          </div>
        </div>
      );
    }
    return (
      <div>
        {alert}
        <Route path="/app/settings"><SettingsPage alert={this.alert} disableAlert={this.disableAlert}/></Route>
        <BottomNavbar/>
      </div>
    );
  }
}

export default AppContent;