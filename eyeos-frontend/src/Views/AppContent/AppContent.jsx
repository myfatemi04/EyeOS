import React from 'react';
import { Route } from "react-router-dom";
import BottomNavbar from '../../Components/BottomNavbar/BottomNavbar';
import SettingsPage from '../SettingsPage/SettingsPage';
import BackArrow from './svg/arrow_back.svg';

class AppContent extends React.Component {

  render() {
    return (
      <div>
        <Route path="/app/settings" component={SettingsPage}/>
        <BottomNavbar history={this.props.history}/>
      </div>
    );
  }
}

export default AppContent;