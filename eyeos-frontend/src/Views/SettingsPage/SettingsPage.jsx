import React from 'react';

class SettingsPage extends React.Component {
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
          <button className="bg-green-500 hover:bg-green-700 text-white font-medium hover:shadow-xl duration-200 py-2 px-4 rounded outline-none focus:outline-none">Enable</button>
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