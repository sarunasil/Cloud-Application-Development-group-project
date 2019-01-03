import React, {Component} from 'react';
import SpotifyWebApi from 'spotify-web-api-node';

var spotifyApi = new SpotifyWebApi({
    clientId: '1811c9058bad498b8d829cd37564fdc6'
});

class SpotifyPlayer extends Component {

    //will receive playback tokens
    constructor(props) {
        super(props);
        spotifyApi.setAccessToken(this.props.spotifyToken);

        this.playerCheckInterval = setInterval(() => this.checkForPlayer(), 1000);
    }

    componentDidMount() {
        const script = document.createElement("script");
        script.src = "https://sdk.scdn.co/spotify-player.js";
        document.body.appendChild(script);

        const script2 = document.createElement("script");
        script2.innerHTML = "window.onSpotifyWebPlaybackSDKReady = () => { window.Spotify = Spotify;}";
        document.body.appendChild(script2);
    }

    checkForPlayer() {
        const token = this.props.spotifyToken;

        if (window.Spotify) {
            clearInterval(this.playerCheckInterval);

            this.player = new window.Spotify.Player({
                name: "Play.me Spotify Player",
                getOAuthToken: cb => { cb(token); },
            });
            this.createEventHandlers();

            // finally, connect!
            this.player.connect();
        }
    }

    createEventHandlers() {
        this.player.on('initialization_error', e => { console.error(e); });
        this.player.on('authentication_error', e => { console.error(e); });
        this.player.on('account_error', e => { console.error(e); });
        this.player.on('playback_error', e => { console.error(e); });

        // Playback status updates
        this.player.on('player_state_changed', state => {
            console.log(state);
            if(state.paused && state.position === 0) this.props.next()
        });

        // Ready
        this.player.on('ready', data => {
            let { device_id } = data;
            console.log(device_id);
            this.setState({ deviceId: device_id });
        });
    }

    play(){
        console.log("in play")
        if(this.props.songUri === this.state.lastPlayed) return;

        const data = spotifyApi.play({
            uris:[this.props.songUri],
            device_id: this.state.deviceId
        });

        this.setState({lastPlayed: this.props.songUri});
        //console.log(JSON.stringify(data.body));
        return (
            <h5>canta: {this.props.songUri}</h5>
        )
    }

    render(){
        return (
            <div>
                {this.props.songUri ?
                this.play() :
                <h3>no song</h3>}
            </div>
        )
    }
}

export default SpotifyPlayer