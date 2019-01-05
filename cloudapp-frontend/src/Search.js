import React, {Component} from 'react';
import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";
import searchYouTube from "youtube-api-search";
import SpotifyWebApi from 'spotify-web-api-node';
import axios from 'axios'

var spotifyApi = new SpotifyWebApi({
    clientId: '1811c9058bad498b8d829cd37564fdc6'
});

class Search extends Component {

    //will receive search tokens
    constructor(props) {
        super(props);

        //TODO rather than expecting the token from the parent, make an API call and obtain it directly here
        spotifyApi.setAccessToken(this.props.cookies.get('SpotifySearchToken'));
        
    }

    state = {
        results: []
    }



    search = async (word) => {
        var entries = [];
        searchYouTube({key: this.props.cookies.get('YoutubeSearchToken'), term: word, maxResults: 6}, (videos) => {
            for(var video of videos){
                entries.push({
                    time: 0,
                    url: video.id.videoId,
                    name: video.snippet.title
                });
            }

            this.setState({results: entries});
        });

        if(spotifyApi.getAccessToken()){
            var tracks  = await spotifyApi.searchTracks(word, {limit: 6});
            for(var track of tracks.body.tracks.items){
                entries.push({
                    name: track.artists[0].name + ' - ' + track.name,
                    url: track.uri,
                    time: track.duration_ms
                });
            }
        }
    }

    addSong = async (index) => {
        //TODO api call to add the song
        console.log(JSON.stringify(this.state.results[index]) + ' will be added')
        // var postLink = 'http://127.0.0.1:5000/' + this.props.cookies.get('roomId') + '/enqueue-song';
        var postLink = 'https://cloud-app-dev-227512.appspot.com/' + this.props.cookies.get('roomId') + '/enqueue-song';
        var code  = {
            Authorization : this.props.cookies.get('MasterCookie'),
            body: {
                name: this.state.results[index].name,
                url : this.state.results[index].url,
                time: this.state.results[index].time

            }
        };
        const response = await axios.post(postLink, code);
        console.log(response);    
    }

    renderSearch(){
        var searchResults = this.state.results;
        return searchResults.map(
            (song, i) =>

                <li style={{border:"0"}} className="list-group-item" key = {i}  >

                    { !song.url.startsWith('spotify:') &&
                    <img src={require('./youtubeLogo.png')} width="50" height="40"/>
                    }
                    {  song.url.startsWith('spotify:') &&
                    <img src={require('./spotifyLogo.png')} width="40" height="40"/>
                    }
                    <span> </span>
                    {song.name}
                    <span> </span>
                    <div className="float-right">
                        <button type="button" className="btn btn-success" onClick={() => this.addSong(i)}><FontAwesomeIcon icon="plus-square"/></button>
                        </div>

                </li>


        );
    }

    render() {
        return (
            <div>
                <ul className="list-group" style={{textAlign:"left"}}>
                    {this.renderSearch()}
                </ul>
            </div>
        );
    }
}

export default Search;