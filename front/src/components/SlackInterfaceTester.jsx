import React, { Component } from 'react';

class SlackInterfaceTester extends Component {

    constructor(props) {
        super(props);
        this.state = {
            // Initial state here

            authtoken:"FY8Hn2DXtTXZDrasxNyx8lgbtR2AjfPZBT8wCcDBW70",

            inputText: 'Hello!',
            
            current_thread: 1,
            current_thread_item: 1,
            
            thread_order: [1,2],
            threads: {
                1:{
                    "id": 1,
                    "name":"General",
                    "description":"General chat",
                    "message_order": [1,2],
                    "messages": {
                        1: {
                            "id": 1,
                            "text": "Hello, world!",
                            "user": "user1",
                            "timestamp": "2020-01-01T00:00:00Z",
                            "reactions": {
                                "up": 1,
                                "down": 0,
                                "saved": 0,
                            },
                            "replies": {
                                1: {
                                    "id": 1,
                                    "text": "Hello, user1!",
                                    "user": "user2",
                                    "timestamp": "2020-01-01T00:00:01Z"
                                },
                                2: {
                                    "id": 2,
                                    "text": "How are you?",
                                    "user": "user2",
                                    "timestamp": "2020-01-01T00:00:01Z"
                                },
                            },
                            "replies_order": [1,2],
                        },
                        2: {
                            "id": 2,
                            "text": "How are you?",
                            "user": "user2",
                            "timestamp": "2020-01-01T00:00:01Z",
                            "reactions": {
                                "up": 1,
                                "down": 0,
                                "saved": 0,
                            },
                            "replies": {
                                1: {
                                    "id": 1,
                                    "text": "I'm okay, how are you?",
                                    "user": "user2",
                                    "timestamp": "2020-01-01T00:00:01Z"
                                },
                                2: {
                                    "id": 2,
                                    "text": "Yeah fine mate",
                                    "user": "user2",
                                    "timestamp": "2020-01-01T00:00:01Z"
                                },
                            },
                            "replies_order": [1,2],
                        }
                    },
                    
                },
                2:{
                    "id": 2,
                    "name":"Random",
                    "description":"Random chat",
                    "messages": {
                        1: {
                            "id": 1,
                            "text": "Hello, Random!",
                            "user": "user1",
                            "timestamp": "2020-01-01T00:00:00Z"
                        },
                        2: {
                            "id": 2,
                            "text": "Bleep bloop blop?",
                            "user": "user2",
                            "timestamp": "2020-01-01T00:00:01Z"
                        }
                    },
                    "message_order": [1,2]
                },
            },

        };
    }

    componentDidMount() {
        // connect websocket
        this.websocket = new WebSocket('ws://localhost:8000/api/ode/ws');
        this.websocket.onopen = () => {
            console.log('WebSocket connection established.');

            //test sending a few messages
            //test sending a few messages
            const data = {
                route:"/feed/1/reply/2",
                action:"CREATE",
                request_payload: {},
                authtoken: this.state.authtoken,
            }
            this.websocket.send(JSON.stringify(data));

        };
        this.websocket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log('Received data:', data);
            // Handle received data here
        };
        this.websocket.onclose = () => {
            console.log('WebSocket connection closed.');
        };
    }

    onChangeInput = (event) => {
        this.setState({ inputText: event.target.value });
    };

    onClickSend = () => {
        const { inputText } = this.state;
        console.log('Sending:', inputText);
        if (inputText) {
            // Send data through websocket
            const data = {
                request_payload: {
                    payload_type: 'message',
                    message: inputText,
                },
                authtoken: this.state.authtoken,
            }
            this.websocket.send(JSON.stringify(data));
            this.setState({ inputText: '' });
        }
    };
        
    onClickThread(thread_id) {
        this.setState({
            current_thread: thread_id,
            current_thread_item: null,
        });
    }

    onClickThreadItem(thread_item_id) {
        console.log("onClickThreadItem", thread_item_id);
        this.setState({
            current_thread_item: thread_item_id
        });
    }

    renderReplies(replies_order, replies) {
        return (
            <div className='replies_container'>
                <div className="replies"
                    style={{padding: "10px", overflowY: "scroll", height: "calc(100vh - 100px)"}}
                >
                {replies_order.map((reply_id) => {
                    const reply = replies[reply_id];
                    return (
                        <div key={reply.id} className="reply"
                            style={{padding: "10px"}}
                        >
                            <p>{reply.text}</p>
                        </div>
                    );
                })}
                </div>
                <div className="input"
                        style={{width: "calc(100% - 100px)", display: "inline-block"}}>
                        <input type="text" className='form-control'
                            style={{width: "calc(100% - 50px)", display: "inline-block"}}
                            onChange={this.onChangeInput}
                        />
                        <button className='btn btn-primary'
                            style={{width: "40px", display: "inline-block"}}
                            onClick={this.onClickSend.bind(this)}
                        >Send</button>
                </div>
                
            </div>
        );

    }

    render() {

        let replies_component = (<div className="replies"
            style={{padding: "10px"}}
        >
            <p>Click a message to view it here.</p>
        </div>);
        if(this.state.current_thread_item){
            const replies_order = this.state.threads[this.state.current_thread].messages[this.state.current_thread_item].replies_order;
            const replies = this.state.threads[this.state.current_thread].messages[this.state.current_thread_item].replies;
            replies_component = this.renderReplies(replies_order,replies);
        }

        return (
        <div className="slack-interface-tester row">
            <div className="left-sidebar col-sm-4 bg-dark"
                style={{height: "100vh"}}
            >
               
                {this.state.thread_order.map((thread_id) => {
                    const thread = this.state.threads[thread_id];
                    return (
                        <div key={thread.id} className="thread"
                            style={{padding: "10px", cursor: "pointer"}}
                            onClick={this.onClickThread.bind(this, thread.id)}
                        >
                            <h3>{thread.name}</h3>
                            <p>{thread.description}</p>
                        </div>
                    );
                })}
            </div>
            <div className="main-column col-sm-4  bg-primary"
                style={{height: "100vh", borderLeft: "1px solid #eee"}}
            >
                <div className="messages"
                    style={{padding: "10px", overflowY: "scroll", height: "calc(100vh - 100px)"}}
                >
                {this.state.threads[this.state.current_thread].message_order.map((message_id) => {
                    const message = this.state.threads[this.state.current_thread].messages[message_id];
                    return (
                        <div key={message.id} className="message"
                            style={{padding: "10px", cursor: "pointer"}}
                            onClick={this.onClickThreadItem.bind(this, message.id)}
                        >
                            <p>{message.text}</p>
                        </div>
                    );
                })}
                </div>
                <div className="input"
                    style={{width: "calc(100% - 100px)", display: "inline-block"}}>
                    <input type="text" className='form-control'
                        style={{width: "calc(100% - 50px)", display: "inline-block"}}
                        onChange={this.onChangeInput}
                        value={this.state.inputText}
                    />
                    <button className='btn btn-primary'
                        style={{width: "40px", display: "inline-block"}}
                        onClick={this.onClickSend}
                    >Send</button>
                </div>
            </div>
            <div className="right-column col-sm-4 bg-primary"
                style={{height: "100vh", borderLeft: "1px solid #eee"}}
            >
                {replies_component}

                
             
            </div>
        </div>
        );
    }
}

export default SlackInterfaceTester;
