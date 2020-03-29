import React from 'react';
import { BrowserRouter as Router, Route } from "react-router-dom";
import './App.scss';
import HomePage from '../../Views/HomePage/HomePage';
import AppContent from '../../Views/AppContent/AppContent';

function App() {
  return (
    <div className="App">
      <Router>
        <Route path="/" exact >
          <HomePage />
        </Route>
        <Route path="/app">
          <AppContent/>
        </Route>
      </Router>
    </div>
  );
}

export default App;
