import React from 'react';
import { Link, withRouter } from "react-router-dom";
import './TabItem.scss';

class TabItem extends React.Component {
  defaultProps = {
    iconColor: "#000000",
    className: "",
  }

  render() {
    return (
      <Link to={this.props.link}>
        <div
          className={"bg-secondary text-white w-full h-16 mt-2 rounded-lg p-4 flex items-center shadow-lg hover:shadow-2xl tab-item " + this.props.className}
        >
          <div style={{backgroundColor: this.props.iconColor}} className="h-10 w-10 rounded-full mr-2 flex items-center">
            <img className="m-auto" src={this.props.icon}></img>
          </div>
          <div className="block">
            <div className="font-semibold">{this.props.title}</div>
            <div className="text-sm -mt-1 -mb-1">{this.props.description}</div>
          </div>
        </div>
      </Link>
    );
  }
}

export default withRouter(TabItem);