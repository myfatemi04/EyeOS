import React from 'react';
import NavbarItem from './NavbarItem/NavbarItem';

class BottomNavbar extends React.Component {
  render() {
    return (
      <div className="flex items-center w-full bg-white h-16 bottom-0 fixed bg-secondary px-8 py-3 shadow-lg z-50">
        <NavbarItem 
          text="Home" 
          color="#e7d1ee" 
          textColor="#642b75"
          link="/"
        />
        <NavbarItem 
          className="ml-2" 
          text="Settings" 
          color="#94e2bf" 
          link="/app/settings"
        />
        <NavbarItem 
          className="ml-2" 
          text="App Launcher" 
          color="#d7797a" 
          textColor="white"
          link="/app/launcher"
        />
        {/* <NavbarItem 
          className="ml-2" 
          text="Emotion" 
          color="#d1e7e8" 
          textColor="#3f8e84"
          link="/app/emotion"
        /> */}
      </div>
    )
  }
}

export default BottomNavbar