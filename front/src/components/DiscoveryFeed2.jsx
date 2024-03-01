// App.js or Feed.js
import MediaItem from './MediaItem';
import InfiniteScroll from 'react-infinite-scroll-component';
import Api from './api';
import { withRouter } from './utils.jsx';

import React, { useState, useEffect } from 'react';

const default_items = [];

class DiscoveryFeed extends React.Component {
   
    constructor(props) {
        super(props);
        this.state = {
          api:new Api(),
          sidebarHeight:window.innerHeight,
          loaded:false,
          items: [
          ],
          hasMore:true,
          nextPage: 1,

          feed_id:null,
          feed:{},
        }

    }

    componentDidMount(){
        console.log("discovery feed topics");

        const routerParams = this.props.params;
        
        console.log(routerParams);
        if (routerParams.discoveryFeedId){
            this.setState({feed_id:routerParams.discoveryFeedId}, () => {this.init()})
        }


        
    }

    // Function to fetch items
    async fetchItems(pageNum){
        try {
            //const topics = this.state.topics.join(",");
            const response = await this.state.api.getCustomDiscoveryFeedItems(this.state.feed_id, this.state.nextPage);
            console.log(response);
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

    async chatWithItem(item_id){
        try {
            const response = await this.state.api.chatMediaItem(item_id);
            console.log(response);
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

        this.fetchItems(1).then(newItems => {
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
                <MediaItem
                    key={item.id}
                    item={item}
                    onUpvote={this.handleUpvote}
                    onDownvote={this.handleDownvote}
                    onSave={this.handleSave}
                    onComment={this.handleComment}
                />
            ))
        }


        return (
            <div className='container'
                    
                >
                
               
                <div className='row'>
                    <div className='col-sm-2'>
                    {feed_info}
                    </div>
                    <div className='col-sm-8'>
                        
                            {items}
                            
                       
                    </div>
                    <div className='col-sm-2'></div>
                </div>
            </div>
    
        );
    }
    

}

export default withRouter(DiscoveryFeed);
