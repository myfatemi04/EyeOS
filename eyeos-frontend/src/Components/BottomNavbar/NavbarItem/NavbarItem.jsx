import React from 'react';
import { Link } from 'react-router-dom';


class NavbarItem extends React.Component {
  defaultProps = {
    className: "",
    color: "black",
    textColor: "black",
  }

  render() {
    return (
      <Link to={this.props.link}>
        <div 
          style={{background: this.props.color, color: this.props.textColor}} 
          className={"flex items-center text-center py-1 px-3 rounded-full " + this.props.className}
        >
          {this.props.text}
        </div>
      </Link>
    );
  }
}

export default NavbarItem;