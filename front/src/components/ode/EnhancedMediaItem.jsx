import React from 'react';

import ReactMarkdown from 'react-markdown'


class EnhancedMediaItem extends React.Component {
    constructor(props){
        super(props);
        this.state = {
           
            item:props.item,
            message:"",
            item_chats:[],

                
        }

        this.onChat = this.onChat.bind(this);
        this.onSave = this.onSave.bind(this);
        this.onUpvote = this.onUpvote.bind(this);
        this.onDownvote = this.onDownvote.bind(this);
        this.onComment = this.onComment.bind(this);
        this.onChangeInputText = this.onChangeInputText.bind(this);
    }

    onChat(item_id){
        console.log(item_id, this.state.message);

        const payload = {
            "id_media_item":item_id,
            "message":this.state.message,
        }

        this.props.onChat(payload);
        this.setState({
            "message":"",
        })
    }

    onChangeInputText(e){
        this.setState({message:e.target.value})
    }

    onSave(e){

    }

    onUpvote(e){

    }

    onDownvote(e){

    }

    onComment(e){

    }

    renderItemChats(){

    }

    render(){

        const item = this.state.item;

        let img = (<div></div>)
        if (item.image){
            img = (<img 
            style={{maxHeight:512, maxWidth:512}}
            src={item.image} 
            alt={item.title} className="" />);
        }

        return (
            <div className="card mb-3"
            style={{maxWidth:512}}
        >

            {img}

            <div class="card-footer text-muted">
            <div className="media-actions">
                <button onClick={() => this.onUpvote(item.id)}>Upvote</button>
                <button onClick={() => this.onDownvote(item.id)}>Downvote</button>
                {/* <button onClick={() => this.onSave(item.id)}>Save</button>
                <button onClick={() => this.onComment(item.id)}>Comment</button> */}
            </div>
            </div>

            <div className="card-body">
                <h5 className="card-title"> <a href={item.source_url} target='_blank'>{item.title}</a></h5>
                
            </div>
            <div className="card-body">
                <div className="card-text"><ReactMarkdown children={item.summary} ></ReactMarkdown></div>
            
                <hr></hr>
                <h4>Personalized Content</h4>
                <div className="card-text">
                    <ReactMarkdown children={item.personalized_summary} ></ReactMarkdown>
                </div>
            </div>

            

            
            <div class="card-footer text-muted">
            <div className="media-actions">
                <div className='row'> 
                    <div className='col-sm-8'>
                        <input 
                            onChange={this.onChangeInputText}
                            className='form-control'/>
                    </div>
                    <div className='col-sm-4'>
                        <button 
                            className='btn btn-primary' onClick={() => this.onChat(item.id)}>Chat</button>
                    </div>
                </div>
            </div>
            </div>
            
        </div>
        )
    }

}

export default EnhancedMediaItem;  
