

/**
 * This class handles the connection to the server via WebSockets
 */
class Socks {
    constructor(url, JwtToken, retryAllowed) {
        try {
            this.retryAllowed = retryAllowed; // how many retries are allowed if the server throws an error
            this.JwtToken = JwtToken; // the token for authentication
            this.host = url; // the host url
            this.sock = new WebSocket(url); // the socket instance
            // start the logic when the socket is open
            this.sock.addEventListener("open", (event) => { this.onConnection(event) });
            this.queue = [];// queue to store the requests


            // // binding requests handling function for normal requests
            // this.hadleErrorConnection = this.hadleErrorConnection.bind(this);
            // this.handleMessageRecieved = this.handleMessageRecieved.bind(this);
            // this.handleClosedConnection = this.handleClosedConnection.bind(this);
            // this.cleanEvents = this.cleanEvents.bind(this);

            // // binding requests handling function for Authentication
            // this.AuthHandleMessageRecieved = this.AuthHandleMessageRecieved.bind(this);
            // this.AuthHandleClosedConnection = this.AuthHandleClosedConnection.bind(this);
            // this.AuthHadleErrorConnection = this.AuthHadleErrorConnection.bind(this); 
            // this.AuthCleanEvents = this.AuthCleanEvents.bind(this);
        }
        catch (Exception) {
            // throw an error if the WebSocket is not initiated
            throw "an error occurred when trying to initiate webSocket\n" + Exception;
        }
    }

    /**
     * This function executes when the socket connects
     * and it just calls the initiatAuth function
     * @param {*} event 
     */
    onConnection(event) {
        console.log("[+] connected to host on ", this.host);
        this.initiatAuth();
    }
    /**
     * returnes the right configured message based on the type
     * 
     * types:
     * 
     *  "auth": to send an authentication request
     *
     *  "request": to send a request , could be anything
     * @param {*} msgType the message type
     * @param {*} msg the message
     * @returns the configured message
     */
    figureMsgType(msgType, msg) {
        function authMessage(token) { return { "type": "auth", "token": token }; }
        function requestMessage(request) { return { "type": "request", "request": request } }
        let msgs = null;
        if (msgType === "auth") {
            msgs = JSON.stringify(authMessage(msg));
        }
        else if (msgType === "request") {
            msgs = JSON.stringify(requestMessage(msg));
        }
        return msgs;
    }
    /**
     * This function is used inside the class, not for outside use (DON'T USE IT)
     */
    PrivateSendMessage(msgType, msg) {
        let msgs = this.figureMsgType(msgType, msg);
        if (this.sock && this.sock.readyState === WebSocket.OPEN) {
            this.sock.send(msgs);
        } else {
            console.error("WebSocket is not open. Ready state is:", this.sock.readyState);
        }
    }
    /**
     * This function sends a message to the socket server if the socket is open and ready
     * and it calls the successCallback or the errorCallback depending on what the response
     * of the socket server is
     * @param {*} msgType type of message
     * @param {*} msg the message
     * @param {*} successCallback the success callback 
     * @param {*} errorCallback  the error callback
     */
    sendMessageFromQueue(msgType, msg, successCallback, errorCallback) {
        let msgs = this.figureMsgType(msgType, msg);
        if (this.sock && this.sock.readyState === WebSocket.OPEN) {
            this.sock.send(msgs);
        } else {
            console.error("WebSocket is not open. Ready state is:", this.sock.readyState);
        }

        // event listener for when the sock gets a message
        this.sock.onmessage = (event) => { this.handleMessageRecieved(event, successCallback) };
        //event listener for when the sock closes
        this.sock.onclose = (event) => { this.handleClosedConnection(event) };
        // event listener for when the sock gets an error
        this.sock.onerror = (event) => { this.handleErrorConnection(event, errorCallback) };

    }
    /**
     * This function passes the message to the queue it guarantees that the sending process will not take
     * place before the expectedAfter arg, meaning you could pass a request that it's going to be sent
     * after 5secs, so the actual sending time would be > 5secs, depending on the load on the queue 
     * 
     * @param {*} msgType the types of message to send to the server
     * @param {*} msg  the message that is going to be sent to the server
     * @param {*} successCallback a callback if the server responded
     * @param {*} failedCallback a callback with the error  if the server didn't respond or threw an error
     * @param {*} expectedAfter 
     * @param {boolean} permanent a variable that indicates if the request should not be poped
     * If true only the execution period will be updated when executed, if False then after the
     * execution the request will be removed from the queue! USE THIS CAREFULLY
     */
    queueAmessage(msgType, msg, successCallback, failedCallback, expectedAfter, permanent) {
        let msgs = this.figureMsgType(msgType, msg);
        let currTimeSeconds = new Date().getTime() / 1000;
        if (msgs) {
            // adding a new request to the queue
            this.queue.push(
                [
                    msgType, // message type
                    msg, // the message that will be sent
                    successCallback, // success callback
                    failedCallback, // error callback
                    expectedAfter, // amount of time to execute this request
                    permanent, //Is this request permanent or not?
                    currTimeSeconds // time when the request is appended
                ]);
        }
        else {
            throw "you didn't pass a valid message type this is the problem => " + msgType;
        }
    }
    /** +++++++++++++++++++++ FUNCTION FOR HANDLING AUTH REQUESTS +++++++++++++++++++++++++=**/
    /**
     * function that handles the case where the server responds
     * After we sent the authentication token
     * @param {*} event the event of the socket
     * @param {*} This pointer to this instance
     */
    AuthHandleMessageRecieved(event) {
        // console.log("receved message");
        // console.log(event.data);
        // parse the data received
        let response = JSON.parse(event.data);
        // if the server is allowing the communication
        // start the event loop
        if (response["message"] == "ok") {
            this.allowEventLoopToStart();
        }
    }
    /**
     * function that handles the case where the server
     * closes the connection, indicating that our authentication
     * is not right
     * @param {*} event the event of the socket
     * @param {*} This pointer to this instance
     */
    AuthHandleClosedConnection(event, cleanEvents) {
        console.warn("auth server closed connection");
        console.error("authentication is refused");
    }
    /**
     * function that handles an error by retrying to connect
     * @param {*} event the event of the socket
     * @param {*} This pointer to this instance
     */
    AuthHadleErrorConnection(event, cleanEvents) {
        //If retries are a none negative number and not zero try to connect again
        if (this.retryAllowed > 0) {
            console.warn('an error accured retrying to connect');
            this.retryAllowed--;
            this.initiatAuth();
        }
        // if we can't connect throw an error
        throw "can't connect after trying the specified 'retryAllowed' ";
    }
    /** +++++++++++++++++++++ FUNCTION FOR HANDLING NORMAL REQUESTS +++++++++++++++++++++++++=**/
    /**
     * function that handles the case where the server responds to a message passed
     * @param {*} event the event of the socket
     * @param {*} This pointer to this instance
     */
    handleMessageRecieved(event, successCallback) {
        // parse the response

        let response = JSON.parse(event.data);
        successCallback(response)


    }
    /**
     * function that handles the case where the server closes the connection
     * @param {*} event the event of the socket
     * @param {*} This pointer to this instance
     */
    handleClosedConnection(event) {


    }
    /**
     * function that handles when the server throws an error
     * @param {*} event the event of the socket
     * @param {*} This pointer to this instance
     */
    hadleErrorConnection(event, errorCallback) {
        console.error('an error accured trying to send a message');
        errorCallback(error);
    }

    /**
     * This function is responsible for authenticating the communication
     * between the server and the client, on error the function will try
     * again X amount of times specified in the variable this.retryAllowed
     */
    initiatAuth() {
        console.log("start authentication");
        //Send the request to authenticate
        this.PrivateSendMessage("auth", this.JwtToken);
        // handle when the server sends a message
        this.sock.onmessage = (event) => { this.AuthHandleMessageRecieved(event) };
        // handle when the server closes the connection
        this.sock.onclose = (event) => { this.AuthHandleClosedConnection(event) };
        // handle when the server throws an error
        this.sock.onerror = (event) => { this.AuthHadleErrorConnection(event) };
    }
    /**
     * allow the event loop to start
     */
    allowEventLoopToStart() {
        // start event loop
        this.eventLoop();
    }
    /**
     * This function is the routine that gets executed every 1s
     * First the function records the moment it got executed to compare it
     * with the requests more on that later, next for every request in the queue
     * we're doing the following
     *  1) checking if the time of execution is reached, by checking if the 
     *     distance between when the request got appended and the recorded time when 
     *     this function executed is superior or equal to the expected time for the request to run
     *        
     *        1) if Execution time is reached  the request is going to get sent to the server using  the 
     *          function sendMessageFromQueue()
     *          
     *              2) now we're going to check if the request is permanent or not
     *              
     *                  1) if the request is not permanent, we're just going to add its index to an array so 
     *                 We can remove it from the queue later because we can't interfere with the length of
     *                 the queue while we're looping using its length attribute
     *              
     *                  2) if the request is permanent, we're just going to update the currTimeSeconds so it 
     *                 can get executed again when the expected time for the request is reached 
     *     
     *        3)
     *      if Execution time is not reached ) the request is going to get ignored for the moment
     *  
     *  2) at last we're just going to remove the none permanent requests from the queue
     *  
     */
    loopRoutine() {

        // start time
        let currTimeSeconds = new Date().getTime() / 1000;
        // list to store indexes of requests that are going to be deleted from the queue
        let toPop = [];
        // for every request
        for (let index = 0; index < this.queue.length; index++) {
            // check if the request should be executed at this time
            if ((currTimeSeconds - this.queue[index][6]) >= this.queue[index][4]) {
                // send the request to the sock server
                this.sendMessageFromQueue(
                    this.queue[index][0],
                    this.queue[index][1],
                    this.queue[index][2],
                    this.queue[index][3],
                );
                // check if this request is not a permanent one
                if (this.queue[index][5] === false) {
                    console.debug("this request is not permenent, add it to the a list to pop it after");
                    toPop.push(index);
                }
                //If it's permanent we nee to update the time for the next execution
                else if (this.queue[index][5] === true) {
                    console.debug("this request is permenent, updating execution time");
                    this.queue[index][6] = new Date().getTime() / 1000;
                }
            }
        }
        // clean non permanent requests
        for (let index = 0; index < toPop.length; index++) {
            this.queue.splice(toPop[index], 1);
            console.log("removing index", index, "  from queue");

        }
    }
    /**
     * This function creates an event loop that executes the 
     * loop routine every 1second
     */
    eventLoop() {
        let loop = 0;
        setInterval(() => {
            this.loopRoutine();
            console.info("loop = ", loop);
            loop++;
        }, 1000);
    }
}
let s = new Socks("ws://127.0.0.1:8000/ws/chat/", "your_valid_token", 2);
