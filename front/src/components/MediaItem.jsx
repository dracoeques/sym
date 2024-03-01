import React from 'react';

import ReactMarkdown from 'react-markdown'


function MediaItem({ item, onUpvote, onDownvote, onSave, onComment }) {

    let img = (<div></div>)
    if (item.image){
        img = (<img 
        style={{maxHeight:512, maxWidth:512}}
        src={item.image} 
        alt={item.title} className="" />);
    }

    let topics = (<div></div>);
    if (item.topics){
        topics = (<span>{item.topics.join(", ")}</span>)
        // topics = item.topics.map(function(x){
        //     return {x}</span>
        // })
    }

    return (


        <div className="card mb-3"
            style={{maxWidth:512}}
        >

            {img}

            <div className="card-body">
                <h5 className="card-title"> <a href={item.source_url} target='_blank'>{item.title}</a></h5>
                
            </div>
            <div className="card-body">
                <p className="card-text"><ReactMarkdown children={item.summary} ></ReactMarkdown></p>
            </div>

            

            <div class="card-footer text-muted">
            <div className="media-actions">
                <button onClick={() => onUpvote(item.id)}>Upvote</button>
                <button onClick={() => onDownvote(item.id)}>Downvote</button>
                <button onClick={() => onSave(item.id)}>Save</button>
                <button onClick={() => onComment(item.id)}>Comment</button>
            </div>
            </div>
            
        </div>


        
    );
}

export default MediaItem;