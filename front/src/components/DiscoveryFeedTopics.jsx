// App.js or Feed.js
import MediaItem from './MediaItem';
import InfiniteScroll from 'react-infinite-scroll-component';
import Api from './api';
import { withRouter } from './utils.jsx';

import React, { useState, useEffect } from 'react';

const default_items = [];

class DiscoveryFeedTopics extends React.Component {
   
    constructor(props) {
        super(props);
        this.state = {
          api:new Api(),
          sidebarHeight:window.innerHeight,
          loaded:false,
          items: [
          ],
          topics:"bitcoin",
          hasMore:true,
          nextPage: 1,
        }

        this.changeTopics = this.changeTopics.bind(this);
        this.searchTopics = this.searchTopics.bind(this);

    }

    componentDidMount(){
        console.log("discovery feed topics")
        this.init()
    }

    // Function to fetch items
    async fetchItems(pageNum){
        try {
            //const topics = this.state.topics.join(",");
            const response = await this.state.api.getDiscoveryTopics(this.state.topics, this.state.nextPage);
            console.log(response);
            return response; 
        } catch (error) {
            console.error("Error fetching data:", error);
            return [];
        }
    }

    // Initial data load
    init(){
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
        return (
            <div className='container'
                    
                >
                <div class="input-group mb-3">
                    <input onChange={this.changeTopics} type="text" className="form-control" placeholder="Bitcoin..." aria-label="search" aria-describedby="button-addon2" />
                    <button onClick={this.searchTopics} className="btn btn-primary" type="button" id="button-addon2">Search</button>
                </div>

               
                <div className='row'>
                    <div className='col-sm-2'></div>
                    <div className='col-sm-8'>
                        
                            {this.state.items.map(item => (
                                    <MediaItem
                                        key={item.id}
                                        item={item}
                                        onUpvote={this.handleUpvote}
                                        onDownvote={this.handleDownvote}
                                        onSave={this.handleSave}
                                        onComment={this.handleComment}
                                    />
                                ))}
                            
                       
                    </div>
                    <div className='col-sm-2'></div>
                </div>
            </div>
    
        );
    }
    

}

export default withRouter(DiscoveryFeedTopics);
