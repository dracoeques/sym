import React from 'react';

// import Api from '../modules/api';

import { withRouter } from './utils.jsx';

import 'bootswatch/dist/lux/bootstrap.min.css'; // Added this :boom:

import ReactMarkdown from 'react-markdown'

import Api from './api.js';
import WS from './ws.js';

//import styles from "@chatscope/chat-ui-kit-styles/dist/default/styles.min.css";

import {
  MainContainer,
  ChatContainer,
  MessageList,
  Message,
  MessageInput,
} from "@chatscope/chat-ui-kit-react";


class PromptDeckColumn extends React.Component {

    constructor(props){
        super(props);

        this.state = {
            
        }

    }

    componentDidMount(){

    }


    render(){



        const routerParams = this.props.params;
        
        //console.log("routerParams", routerParams);
        //console.log(this.state.prompt);

        const chatInputHeight = 100;
        const contentHeight = window.innerHeight - chatInputHeight;

        
        let loader = (<div></div>);
        if (this.state.isLoading === true){
            loader = (
                <div className='row message-row' >
                    <div className='col-sm-3'></div>
                    
                    <div className='col-sm-5 text-light'>
                        <h3>Loading...</h3>
                      
                    </div>
                    <div className='col-sm-4'></div>
                    
                </div>);

        }

        return (
            
            <div style={{ 
                position: "relative",
                height: window.innerHeight-5,
               
            }}>

            <MainContainer>
                
                <ChatContainer>
                <MessageList>
                    <Message
                    model={{
                        message: "Hello my friend",
                        sentTime: "just now",
                        sender: "Joe",
                    }}
                    />
                </MessageList>
                <MessageInput placeholder="Type message here" />
                </ChatContainer>
            </MainContainer>
            </div>
            
        )
    }

}

export default withRouter(PromptDeckColumn);