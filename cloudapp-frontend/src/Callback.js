import React, {Component} from 'react';
import queryString from 'query-string';

//this component exists only to handle spotify authorization
//it will redirect to the master room, so no need for a pretty interface
class Callback  extends Component {
    constructor(props) {
        super(props);
    }

    componentDidMount(){
        //TODO: call to our backend to set/retrieve an access token, then redirect

        console.log(this.props.cookies.get('roomId'));
        console.log(queryString.parse(this.props.location.search, { ignoreQueryPrefix: true }).code);

        this.props.history.push('/master/'+this.props.cookies.get('roomId'));
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