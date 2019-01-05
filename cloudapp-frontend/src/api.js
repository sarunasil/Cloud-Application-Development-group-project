let axios = require('axios');

// api object holding post and get functions for requests
let api = {};

api.post = (url, cookie, body) => {
    let headers = {
        'Authorization': cookie
    };

    return axios.post(url, body, { headers: headers });
}

api.get = (url, cookie) => {
    let headers = {
        'Authorization': cookie
    };

    return axios.get(url, { headers: headers });
}

// let cookie = '5c309c034b2ddd0588ba02c3:f06cbf1bed03c431bf47f60f359082d0228b79dc8b0512b2a473b80a5a73da74:ff40f1830e0e6a7c61c4b315f7a1275e825201d13f0426e76b544add25b4019e'; // example cookie

// example post body
// let body = {
// 	url: "https://www.youtube.com/watch?v=FRI3QGNWJYI&t=86se",
// 	name: "flaskvideo2"
// };

// Working example for GET
// api.get('http://localhost:5000/5c309c044b2ddd0588ba02c4/pending-songs', cookie, body)
// .then(result => {
//     console.log(result);
// });

// Working example for POST
// api.post('https://cloud-app-dev-227512.appspot.com/5c309c044b2ddd0588ba02c4/enqueue-song', cookie, body)
// .then(result => {
//     console.log(result);
// });

module.exports = api;