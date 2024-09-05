import {Socks}  from "../../socket_logic/customSockets";
/**
 * this function pushes a list of socks jobs to the queue to be executed
 * @param {*} sockConnection the Socks object
 * @param {*} sockRequests the Socks jobs array
 */
function queueSockMessageWhenReady(sockConnection, sockRequests) {
    for (let sockRequest = 0; sockRequest < sockRequests.length; sockRequest++) {
        sockConnection.queueAmessage(
            sockRequests[sockRequest].msgType,
            sockRequests[sockRequest].msg,
            sockRequests[sockRequest].successCallback,
            sockRequests[sockRequest].failedCallback,
            sockRequests[sockRequest].expectedAfter,
            sockRequests[sockRequest].permanent
        );
    }
}

/**
 * this function will only initiate the Sock object when the token
 * to make the request is available, then it's passing the jobs 
 * to the queue to be executed
 * @param {*} token  the token
 * @param {*} sockRequests  the Socks jobs array 
 */
export default function initiateSocksWhenTokenIsAvailable(token, sockRequests) {
    if (token && token.current) {
        let sockConnection = new Socks(callTrackSession(), token.current, 4);
        queueSockMessageWhenReady(sockConnection, sockRequests);
    }
    else {
        setTimeout(() => { initiateSocksWhenTokenIsAvailable(token, sockRequests) }, 200);
    }
}