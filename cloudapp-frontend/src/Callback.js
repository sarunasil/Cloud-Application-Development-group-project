import React, {Component} from 'react';
import queryString from 'query-string';

//this component exists only to handle spotify authorization
//it will redirect to the master room, so no need for a pretty interface
class Callback  extends Component {
    constructor(props) {
        super(props);
    }

    componentDidMount(){
        //TODO: call to our backend to set/retrieve an access token, set cookie then redirect

        console.log(this.props.cookies.get('roomId'));
        console.log(queryString.parse(this.props.location.search, { ignoreQueryPrefix: true }).code);

        //will be set with value returned from server OR server will return it along with the queue
        this.props.cookies.set('accessToken', 'BQDDLNubd4FPSXBz12fi2JD3xE2OLD1KK2f-Vdy7GmfKAm3OLUAOaB9H4PSQ8ycw307ZXVwf7A6eCvbsnF8yDcSy80F0y4w5rYfNtqlhxw-9Q_fKBgiFXkblMyxHx_MMrP9rzBvDinJ4wpen0lfZFxgS9CI-gtgmeAQ7EaHxrEapFW_LjJqlUWS8kbrx', { path: '/', maxAge: 3600 });
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