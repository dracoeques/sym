// App.js or Feed.js
import MediaItem from './MediaItem';
import InfiniteScroll from 'react-infinite-scroll-component';
import Api from './api';
import { withRouter } from './utils.jsx';

import React, { useState, useEffect } from 'react';

const default_items = [];

class DiscoveryFeedCreator extends React.Component {
   
    constructor(props) {
        super(props);
        this.state = {
        
          api:new Api(),
          sidebarHeight:window.innerHeight,
          loaded:false,
          id:null,
          topics: [],
          name: '',
          description: ''
        }

        //this.addTopic = this.changeTopics.bind(this);
        //this.searchTopics = this.searchTopics.bind(this);
        this.handleSave = this.handleSave.bind(this);
    }

    componentDidMount(){

        const routerParams = this.props.params;
        console.log(routerParams);
        if (routerParams.discoveryFeedId){
            this.initFeed(routerParams.discoveryFeedId);
            
        }
    }

    async initFeed(feed_id){
        try {
            const response = await this.state.api.getDiscoveryFeed(feed_id);
            console.log(response);

            const topics = response.topics.map(function(x){
                return x.topic
            })
            this.setState({
                id:response.id,
                name:response.name,
                description:response.description,
                topics:topics,
            })
        } catch (error) {
            console.error("Error fetching data:", error);
            return {};
        }
    }

    handleTopicAddition = (topic) => {
        this.setState(prevState => ({
            topics: [...prevState.topics, topic]
        }));
    };

    handleRemoveTopic = (index) => {
        this.setState(prevState => ({
            topics: prevState.topics.filter((_, i) => i !== index)
        }));
    };

    handleFeedNameChange = (event) => {
        this.setState({ name: event.target.value });
    };

    handleDescriptionChange = (event) => {
        this.setState({ description: event.target.value });
    };

    async handleSave(){
        // Implement save logic here
        console.log('Saved:', this.state);

        let payload = {
            "topics":this.state.topics,
            "name":this.state.name,
            "description":this.state.description,
        }

        if (this.state.id){
            payload["id"] = this.state.id;
        }

        try {
            //const topics = this.state.topics.join(",");
            const response = await this.state.api.createDiscoveryFeed(payload);
            console.log(response);
            this.setState({
                id:response.id,

            })
            return response; 
        } catch (error) {
            console.error("Error fetching data:", error);
            return [];
        }
    };

    addTopic = (event) => {
        console.log(event.target.value);
    }

    handleNewTopicChange = (event) => {
        this.setState({ newTopic: event.target.value });
    };
    
    handleAddTopic = () => {
        if (this.state.newTopic) {
          this.setState(prevState => ({
            topics: [...prevState.topics, prevState.newTopic],
            newTopic: '' // Clear the input after adding
          }));
        }
    };
    
    handleRemoveTopic = (index) => {
        this.setState(prevState => ({
          topics: prevState.topics.filter((_, i) => i !== index)
        }));
    };

    renderTopicList() {
        return this.state.topics.map((topic, index) => (
            <li key={index} className='list-group-item list-group-item-action d-flex justify-content-between align-items-center'>
            {topic}
            <span 
            onClick={() => this.handleRemoveTopic(index)}
            class="badge bg-primary rounded-pill"
            style={{cursor:"pointer"}}
            >X</span>
            
            </li>
        ));
    }
    
    render() {

        let feedUrl = (<div></div>);
        if (this.state.id){
            let href = `/app/discovery/${this.state.id}`
            feedUrl = (<a href={href}>{href}</a>)
        }

        return (
          <div className='container'>
            Feed: {feedUrl}
            <input 
              type="text" 
              placeholder="Feed Name" 
              className="form-control"
              value={this.state.name} 
              onChange={this.handleFeedNameChange} 
            />
            <br></br>
            <textarea 
              placeholder="Description" 
              className="form-control"
              value={this.state.description} 
              onChange={this.handleDescriptionChange} 
            />
            <br></br>
                
            <div class="input-group mb-3">
                <input 
                    type="text" 
                    placeholder="New Topic" 
                    className="form-control"
                    value={this.state.newTopic} 
                    onChange={this.handleNewTopicChange} 
                />
                <button onClick={this.handleAddTopic} className="btn btn-primary" type="button" id="button-addon2">Add Topic</button>
                
            </div>
            <hr></hr>
            <ul className='list-group'>
              {this.renderTopicList()}
            </ul>
            <br></br>
            <button className="btn btn-primary" onClick={this.handleSave}>Save</button>
          </div>
        );
      }
}
    

export default withRouter(DiscoveryFeedCreator);
