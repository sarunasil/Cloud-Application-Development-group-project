import React, { Component } from 'react';
import './App.css';
import {Route, Switch} from 'react-router-dom'
import Home from './Home'
import PeasantRoom from './PeasantRoom'
import MasterRoom from './MasterRoom'
import Callback from './Callback'
import {withCookies} from 'react-cookie';
import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faIgloo } from '@fortawesome/free-solid-svg-icons'
import { faPlayCircle } from '@fortawesome/free-solid-svg-icons'
import { faTrashAlt } from '@fortawesome/free-solid-svg-icons'
import { faPlusSquare } from '@fortawesome/free-solid-svg-icons'
import { faSearch } from '@fortawesome/free-solid-svg-icons'
import { faThumbsUp} from '@fortawesome/free-solid-svg-icons'
import { faThumbsDown} from '@fortawesome/free-solid-svg-icons'
import {faSyncAlt} from  '@fortawesome/free-solid-svg-icons'
import {faForward} from '@fortawesome/free-solid-svg-icons'
import {faBackward} from '@fortawesome/free-solid-svg-icons'
import {faPause} from '@fortawesome/free-solid-svg-icons'
import {faStepForward} from '@fortawesome/free-solid-svg-icons'
import {faPlay} from '@fortawesome/free-solid-svg-icons'


library.add(faForward)
library.add(faBackward)
library.add(faPause)
library.add(faStepForward)
library.add(faPlay)
library.add(faThumbsDown)
library.add(faSyncAlt)
library.add(faThumbsUp)
library.add(faPlayCircle)
library.add(faTrashAlt)
library.add(faPlusSquare)
library.add(faSearch)

class App extends Component {
    constructor(props) {
        super(props);
    }


  render() {
    return (
      <div className="App">
          <Switch>
              <Route exact path='/' render={(props) => <Home {...props} cookies={this.props.cookies}/>}/>
              <Route path='/callback' render={(props) => <Callback {...props} cookies={this.props.cookies}/>}/>
              <Route path='/master/:id' render={(props) => <MasterRoom {...props} cookies={this.props.cookies}/>}/>
              <Route path='/:id' render={(props) => <PeasantRoom {...props} cookies={this.props.cookies}/>}/>
              <Route path='*' component={() => <div><h1>404 Not Found!</h1></div>}/>
          </Switch>
      </div>
    );
  }
}

export default withCookies(App);
