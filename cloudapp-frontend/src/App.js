import React, { Component } from 'react';
import './App.css';
import {Route, Switch} from 'react-router-dom'
import Home from './Home'
import PeasantRoom from './PeasantRoom'
import MasterRoom from './MasterRoom'
import Callback from './Callback'
import {withCookies} from 'react-cookie';

class App extends Component {
    constructor(props) {
        super(props);
    }


  render() {
    return (
      <div className="App">
          <Switch>
              <Route exact path='/' component={Home}/>
              <Route path='/callback' render={(props) => <Callback {...props} cookies={this.props.cookies}/>}/>
              <Route path='/master/:id' render={(props) => <MasterRoom {...props} cookies={this.props.cookies}/>}/>
              <Route path='/:id' render={(props) => <PeasantRoom {...props}/>}/>
              <Route path='*' component={() => <div><h1>404 Not Found!</h1></div>}/>
          </Switch>
      </div>
    );
  }
}

export default withCookies(App);
