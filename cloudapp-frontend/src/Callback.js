import React, {Component} from 'react';
import queryString from 'query-string';
import axios from 'axios';
import api from './api';
//this component exists only to handle spotify authorization
//it will redirect to the master room, so no need for a pretty interface
class Callback  extends Component {
    constructor(props) {
        super(props);
    }

    async componentDidMount(){
        //TODO: call to our backend to set/retrieve an access token, set cookie then redirect

        const room = this.props.cookies.get('roomId');
        const code = queryString.parse(this.props.location.search, { ignoreQueryPrefix: true }).code;
        var toSend = {
            code : code,
            redirect_url : "http://localhost:3000/callback"
        };

         //const response = await api.post('https://cloud-app-dev-227512.appspot.com/spotify', this.props.cookies.get('MasterCookie'), toSend);
        const response = await api.postNoCookie('https://cloud-app-dev-227512.appspot.com/spotify', toSend);



        this.props.cookies.set('accessToken', response.data.success.auth, { path: '/', maxAge: 36000 });
        //console.log(this.props.cookies.get('accessToken'));
        this.props.history.push('/master/'+room);
    }


    render() {
        return (
            <div>
                <h1></h1>
            </div>
        );
    }
}

export default Callback;