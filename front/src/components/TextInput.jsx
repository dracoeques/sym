import React from 'react';

// import Api from '../modules/api';

import { withRouter } from './utils.jsx';

import 'bootswatch/dist/lux/bootstrap.min.css'; // Added this :boom:

import ReactMarkdown from 'react-markdown'

import Api from './api.js';
import WS from './ws.js';


class TextInput extends React.Component {

    constructor(props){
        super(props);

        this.state = {
            messages:[],
            message:"",
            chatInputHeight: 100,
            
        }

        this.handleMessageInput = this.handleMessageInput.bind(this);

        


    }

    handleMessageInput(e){
        e.preventDefault();
        const text = e.target.value;
        console.log(text);
        //calculate height of text input

        this.setState({message:text});
    }

    
    render(){


        const messages = this.state.messages.map(m => {
            return (
                <p>m</p>
            )
        })

        const contentHeight = window.innerHeight - this.state.chatInputHeight - 40;
        
        return (

        <div className="container-textarea">
            <div className='row'>
                
                <div className='col-sm-12 nomargin pad40'>

                    <div
                    
                        style={{
                            height:contentHeight,
                            overflowY:"scroll",
                            overflowX: "hidden",
                            

                        }}
                    >
                        <br></br>
                        {messages}
                        <br></br>
                    </div>
                    
                    

                        <textarea
                        className="form-control dynamic-textarea"
                        value={this.state.textValue}
                        onChange={this.handleTextChange}
                        placeholder="Type here..."

                        style={{
                            color: "#a0a0a0",
                            backgroundColor: "#fff",
                            outline: "1px solid #ffffff",                        
                            fontSize: "16px",
                            boxShadow: "0 0 20px rgba(0, 0, 0, .15)",
                            border: "0.75px solid #d8d8d8",
                            paddingRight:75,
                        }}
                        
                        ></textarea>
                        
                        <button className="bottom-button btn btn-secondary" type="button" id="button-addon2"
                                                
                                                onClick={this.handleWebsocketSendMessage}
                                                style={{
                                                    padding: 0,
                                                }}
                                            >
                                                <img 
                                            src="https://uploads-ssl.webflow.com/64ee39d44b81a0ec6c03c3ba/64fb5f064f65e4372c4fb7ad_Screenshot%202023-09-08%20at%2010.50.21%20AM.png" 
                                            loading="lazy" 
                                            alt="" 
                                            style={{
                                                height:69,
                                                borderLeft: "1px solid #fefefe ",
                                            }}
                                            class="image-62"/></button>
                    </div>
            </div>
        </div>
        )
    }

}

export default withRouter(TextInput);