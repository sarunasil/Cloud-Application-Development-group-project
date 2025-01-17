import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import App from './App';
import * as serviceWorker from './serviceWorker';
import {BrowserRouter as Router, Route} from 'react-router-dom';
import {CookiesProvider} from 'react-cookie';

ReactDOM.render(
    <CookiesProvider>
    <Router>
        <Route path='/' render={ props => <App {...props} />}/>
    </Router>
    </CookiesProvider>,
    document.getElementById('root'));
// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: http://bit.ly/CRA-PWA
serviceWorker.unregister();
