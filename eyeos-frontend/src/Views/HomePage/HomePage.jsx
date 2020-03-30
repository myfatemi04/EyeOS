import React from 'react';
import './HomePage.scss';
import TabItem from './TabItem/TabItem';
import EyeIcon from './svg/eye.svg';
import AppIcon from './svg/app.svg';
import FaceIcon from './svg/face.svg';

class HomePage extends React.Component {
  render() {
    return (
      <div className="text-white w-full mx-auto min-h-screen bg-secondary decorated-part">
        <div className="absolute flex flex-grow items-center h-full left-0 p-10 bg-main">
          <div>
            <div className="font-semibold text-4xl">EyeOS</div>
            <p className="font-semibold text-md">
              Using eye tracking and machine learning to
              <span className="text-green-200"> empower</span>
            </p>
            <TabItem
              className="mt-2"
              title="Eye Tracking Settings"
              description="Configure EyeOS tracking settings"
              link="/app/settings"
              icon={EyeIcon}
              iconColor="#45BF88"
            />
            <TabItem
              className="mt-3"
              title="App Launcher"
              description="Open an app using text to speech"
              link="/app/launcher"
              icon={AppIcon}
              iconColor="#d7797a"
            />
            {/* <TabItem
              className="mt-3"
              title="Emotional Awareness"
              description="Get advice based on emotional state"
              link="/app/emotion"
              icon={FaceIcon}
              iconColor="#39B7B7"
            /> */}
          </div>
        </div>
      </div>
    );
  }
}

export default HomePage;