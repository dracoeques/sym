// App.js or Feed.js
import MediaItem from '../MediaItem.jsx';
import EnhancedMediaItem from './EnhancedMediaItem.jsx';
import InfiniteScroll from 'react-infinite-scroll-component';
import Api from '../api.js';
import WS from "../ws.js";
import { withRouter } from '../utils.jsx';

import React, { useState, useEffect } from 'react';

const default_items = [];

class DiscoverChat extends React.Component {
   
    constructor(props) {
        super(props);
        this.state = {
          api:new Api(),
          ws: null,
          sidebarHeight:window.innerHeight,
          loaded:false,
          items: [
          ],
          hasMore:true,
          nextPage: 1,

          feed_id:null,
          feed:{},
        }

        this.handleChatWithMedia = this.handleChatWithMedia.bind(this);

    }

    componentDidMount(){
        console.log("discovery feed topics");

        const routerParams = this.props.params;
        
        console.log(routerParams);
        if (routerParams.discoveryFeedId){
            this.setState({feed_id:routerParams.discoveryFeedId}, () => {this.init()})
        }

        //this.initws()


        
    }

    async initws(){
        const routerParams = this.props.params;
        //console.log("routerParams", routerParams);
        let promptFlowId = this.state.prompt_flow_id;
        if (routerParams.promptFlowId){
            promptFlowId = parseInt(routerParams.promptFlowId);
        }

        try {
            //const me = await this.state.api.me();
            //console.log('me:', me);

            //user is logged in, create websocket
            let base = window.location.host;
            if (base === "localhost:5173" || base === "localhost:5174"){
                base = "localhost:8000"
            } 
            let protocol = "ws";
            if (location.protocol === 'https:') {
                protocol = "wss"
            }
            const ws = new WS(
                `${protocol}://${base}/ode-ws`,
                this.handleWebsocketOnMessage,
                this.handleWebsocketOnOpen,
                this.handleWebsocketOnClose,
                this.handleWebsocketOnError,
            );

            this.setState({
                ws:ws,
            });

            
        } catch (error) {
            console.error('Error ininit:', error);
            //window.location.href = "/app/login";
        }
    }
 

    handleWebsocketOnMessage(event){
        
        const content = event.data;
        const obj = JSON.parse(content);
        
        console.log("onmessage", obj);
       
    }

    handleWebsocketSendMessage(){
        const message = this.state.message;
        if (message.length === 0){
            return;
        }


        const payload = {
            
            "message":message,
           
        }
        this.state.ws.sendMessage(payload);

        this.setState({
            message:"",
        });
    }

    handleWebsocketOnOpen(){        

        const wsState = this.state.ws.getState();
        if (wsState === "OPEN"){
             //send our init message
            const payload = {
                "action":"init",
                "prompt_flow_id":this.state.promptFlowId,
                
            }
            this.state.ws.sendMessage(payload);
        }

       
    }

    handleWebsocketOnClose(){
        console.log("Websocket closed");
    }

    handleWebsocketOnError(e){
        console.log("Websocket Error", e);
    }

    handleResize(){
        
        const innerHeight = window.innerHeight;
        console.log("resize",innerHeight);
        this.setState({sidebarHeight:innerHeight})
    }

    calculateTextBoxSize(){

    }

    handleMessageInput(e){
        e.preventDefault();
        const text = e.target.value;
        this.setState({message:text});
    }

    handleSystemInput(e){
        e.preventDefault();
        const text = e.target.value;
        this.setState({context:text});
    }

    handleChatWithMedia(payload){
        console.log("handleChatWithMedia", payload);

        //TODO: send the message over the websocket
        this.chatWithItem(payload)

    }

    // Function to fetch items
    async fetchItems(pageNum){
        try {
            //const topics = this.state.topics.join(",");
            const response = await this.state.api.getPersonalizedDiscoveryFeedItems(this.state.feed_id, pageNum);
            console.log("fetchItems", response, pageNum);
            return response; 
        } catch (error) {
            console.error("Error fetching data:", error);
            return [];
        }
    }

    async fetchFeed(feed_id){
        try {
            const response = await this.state.api.getDiscoveryFeed(feed_id);
            console.log(response);
            return response; 
        } catch (error) {
            console.error("Error fetching data:", error);
            return {};
        }
    }

    async chatWithItem(payload){
        try {
            const response = await this.state.api.chatMediaItem(payload);
            console.log("chat with item", response);
            return response; 
        } catch (error) {
            console.error("Error fetching data:", error);
            return {};
        }
    }

    // Initial data load
    init(){
        this.fetchFeed(this.state.feed_id).then(feed => {
            this.setState({feed:feed})
        })

        this.fetchItems(0).then(newItems => {
            this.setState({items:newItems});
        });
    }

    // Function to fetch more data
    fetchMoreData() {
        const nextPage = page + 1;
        fetchItems(nextPage).then(newItems => {
            if (newItems.length === 0) {
                this.setState({hasMore:false});
            } else {
                this.setState({
                    items:[...this.state.items, ...newItems],
                    nextPage: nextPage,
                });
                
            }
        });
    };

    changeTopics(e){
        console.log(e.target.value);
        this.setState({
            topics:e.target.value,
        })
    }

    searchTopics(){
        this.fetchItems().then(items => {
            this.setState({
                items:items,
            })
        })
    }

    handleUpvote(itemId){
        console.log("Upvoted:", itemId);
        // Implement upvote logic
    };

    handleDownvote(itemId){
        console.log("Downvoted:", itemId);
        // Implement downvote logic
    };

    handleSave(itemId){
        console.log("Saved:", itemId);
        // Implement save logic
    };

    handleComment(itemId) {
        console.log("Comment on:", itemId);
        // Implement comment logic
    };


    render(){

        let feed_info = (<div></div>);
        if (this.state.feed){
            const feed = this.state.feed;
            let topics = (<div></div>);
            if (feed.topics){
                topics = feed.topics.map(function(t){
                    return (<li>{t.topic}</li>)
                })
            }
            const editUrl = `/app/discovery-feed-creator/${this.state.feed_id}`;
            feed_info = (<div>
                <span>Feed: {feed.name}</span>
                <ul>{topics}</ul>
                <a href={editUrl}>Edit feed</a>
            </div>)
        }

        let items = (<div>Loading...</div>)
        if (this.state.items.length > 0){
            items = this.state.items.map(item => (
                <EnhancedMediaItem
                    key={item.id}
                    item={item}
                    onUpvote={this.handleUpvote}
                    onDownvote={this.handleDownvote}
                    onSave={this.handleSave}
                    onComment={this.handleComment}
                    onChat={this.handleChatWithMedia}
                />
            ))
        }


        return (
            <div className='container'
                    
                >
                
               
                <div className='row'
                    style={{
                        height:window.innerHeight, // -100,
                        overflowY: "scroll"
                    }}
                >
                    <div className='col-sm-2'>
                    {feed_info}
                    </div>
                    <div className='col-sm-8'>
                        
                            {items}
                            
                       
                    </div>
                    <div className='col-sm-2'></div>
                </div>
                {/* <div className='row'>
                    <div className='col-sm-2'></div>
                    <div className='col-sm-6'>
                        <textarea
                            className="form-control"
                        ></textarea>
                    </div>

                    <div className='col-sm-2'>
                        <button
                            className="btn btn-primary"
                        >Submit</button>
                    </div>
                    <div className='col-sm-2'></div>
                </div> */}
            </div>
    
        );
    }
    

}

export default withRouter(DiscoverChat);
