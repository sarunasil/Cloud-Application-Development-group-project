import React, {Component} from 'react';
import queryString from 'query-string';
import axios from 'axios'

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
        console.log(room);
        console.log(code);

        // const response = await axios.post(
        //     'https://cloud-app-dev-227512.appspot.com/' + room + '/spotify',
        //     {code: code}
        // );
        // console.log(response);

        this.props.cookies.set('accessToken', '', { path: '/', maxAge: 3600 });
        this.props.history.push('/master/'+room);
    }


    render() {
        return (
            <div>
                <h1>THis is Callback</h1>
            </div>
        );
    }
}

export default Callback;