import React from 'react';
import { BrowserRouter as Router, Route } from "react-router-dom";
import './App.scss';
import HomePage from '../../Views/HomePage/HomePage';

function App() {
  return (
    <div className="App">
      <Router>
        <Route path="/" exact component={HomePage} />
      </Router>
    </div>
  );
}

export default App;
